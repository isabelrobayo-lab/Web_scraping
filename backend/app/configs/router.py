"""CRUD API endpoints for Configuracion_Scraping.

Provides:
- GET    /api/v1/configs          — Paginated list (with active filter)
- POST   /api/v1/configs          — Create configuration
- GET    /api/v1/configs/{id}     — Get single configuration
- PUT    /api/v1/configs/{id}     — Update configuration
- DELETE /api/v1/configs/{id}     — Soft delete (set active=false)
"""

import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import RBACMiddleware
from app.configs.cron_utils import get_cron_preview
from app.configs.schemas import (
    ConfigCreate,
    ConfigResponse,
    ConfigUpdate,
    PaginatedConfigResponse,
)
from app.core.database import get_db
from app.models.configuracion_scraping import ConfiguracionScraping

router = APIRouter(prefix="/configs", tags=["configs"])


def _to_response(config: ConfiguracionScraping) -> ConfigResponse:
    """Convert a SQLAlchemy model instance to a ConfigResponse schema."""
    cron_preview = None
    if config.cron_expression:
        cron_preview = get_cron_preview(config.cron_expression)

    return ConfigResponse(
        id=config.id,
        url_base=config.url_base,
        profundidad_navegacion=config.profundidad_navegacion,
        tipo_operacion=config.tipo_operacion,
        modo_ejecucion=config.modo_ejecucion,
        cron_expression=config.cron_expression,
        cron_preview=cron_preview,
        active=config.active,
        created_at=config.created_at,
        updated_at=config.updated_at,
        last_execution_at=config.last_execution_at,
    )


@router.get(
    "",
    response_model=PaginatedConfigResponse,
    dependencies=[Depends(RBACMiddleware("configs:read"))],
)
async def list_configs(
    page: int = Query(default=1, ge=1, description="Número de página"),
    size: int = Query(default=20, ge=1, le=100, description="Elementos por página"),
    active: bool | None = Query(default=None, description="Filtrar por estado activo"),
    db: AsyncSession = Depends(get_db),
) -> PaginatedConfigResponse:
    """List scraping configurations with pagination and optional active filter."""
    query = select(ConfiguracionScraping)

    if active is not None:
        query = query.where(ConfiguracionScraping.active == active)

    # Count total records
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Calculate pagination
    pages = math.ceil(total / size) if total > 0 else 0
    offset = (page - 1) * size

    # Fetch paginated results
    query = query.order_by(ConfiguracionScraping.created_at.desc())
    query = query.offset(offset).limit(size)
    result = await db.execute(query)
    configs = result.scalars().all()

    items = [_to_response(c) for c in configs]

    return PaginatedConfigResponse(
        items=items,
        total=total,
        page=page,
        pages=pages,
    )


@router.post(
    "",
    response_model=ConfigResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RBACMiddleware("configs:write"))],
)
async def create_config(
    payload: ConfigCreate,
    db: AsyncSession = Depends(get_db),
) -> ConfigResponse:
    """Create a new scraping configuration."""
    config = ConfiguracionScraping(
        url_base=payload.url_base,
        profundidad_navegacion=payload.profundidad_navegacion,
        tipo_operacion=payload.tipo_operacion.value,
        modo_ejecucion=payload.modo_ejecucion.value,
        cron_expression=payload.cron_expression,
        active=True,
    )
    db.add(config)
    await db.flush()
    await db.refresh(config)
    return _to_response(config)


@router.get(
    "/{config_id}",
    response_model=ConfigResponse,
    dependencies=[Depends(RBACMiddleware("configs:read"))],
)
async def get_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
) -> ConfigResponse:
    """Get a single scraping configuration by ID."""
    result = await db.execute(
        select(ConfiguracionScraping).where(ConfiguracionScraping.id == config_id)
    )
    config = result.scalar_one_or_none()
    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuración con id={config_id} no encontrada",
        )
    return _to_response(config)


@router.put(
    "/{config_id}",
    response_model=ConfigResponse,
    dependencies=[Depends(RBACMiddleware("configs:write"))],
)
async def update_config(
    config_id: int,
    payload: ConfigUpdate,
    db: AsyncSession = Depends(get_db),
) -> ConfigResponse:
    """Update an existing scraping configuration."""
    result = await db.execute(
        select(ConfiguracionScraping).where(ConfiguracionScraping.id == config_id)
    )
    config = result.scalar_one_or_none()
    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuración con id={config_id} no encontrada",
        )

    # Apply only provided fields
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "tipo_operacion" and value is not None:
            setattr(config, field, value.value if hasattr(value, "value") else value)
        elif field == "modo_ejecucion" and value is not None:
            setattr(config, field, value.value if hasattr(value, "value") else value)
        else:
            setattr(config, field, value)

    await db.flush()
    await db.refresh(config)
    return _to_response(config)


@router.delete(
    "/{config_id}",
    response_model=ConfigResponse,
    dependencies=[Depends(RBACMiddleware("configs:write"))],
)
async def delete_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
) -> ConfigResponse:
    """Soft delete a scraping configuration (sets active=false)."""
    result = await db.execute(
        select(ConfiguracionScraping).where(ConfiguracionScraping.id == config_id)
    )
    config = result.scalar_one_or_none()
    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuración con id={config_id} no encontrada",
        )

    config.active = False
    await db.flush()
    await db.refresh(config)
    return _to_response(config)
