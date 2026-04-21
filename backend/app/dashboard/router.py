"""Dashboard API endpoints for properties, summary, errors, and tasks.

Provides:
- GET /api/v1/properties          — Paginated property search with combinable filters
- GET /api/v1/properties/{id}     — Property detail (all 66 fields)
- GET /api/v1/summary             — Dashboard summary totals
- GET /api/v1/errors              — Paginated error listing with filters
- GET /api/v1/tasks               — Paginated task listing with filters
- GET /api/v1/tasks/{task_id}     — Task detail with full execution summary
"""

import math
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import RBACMiddleware
from app.core.database import get_db
from app.dashboard.schemas import (
    CountByField,
    ErrorListItem,
    PaginatedErrorResponse,
    PaginatedPropertyResponse,
    PaginatedTaskResponse,
    PropertyDetail,
    PropertyListItem,
    SummaryResponse,
    TaskDetail,
    TaskListItem,
)
from app.models.esquema_inmueble import EsquemaInmueble
from app.models.log_error import LogError
from app.models.tarea_scraping import TareaScraping

router = APIRouter(tags=["dashboard"])


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------


@router.get(
    "/properties",
    response_model=PaginatedPropertyResponse,
    dependencies=[Depends(RBACMiddleware("dashboard:read"))],
)
async def list_properties(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=100),
    sitio_origen: str | None = Query(default=None),
    tipo_inmueble: str | None = Query(default=None),
    operacion: str | None = Query(default=None),
    municipio: str | None = Query(default=None),
    sector: str | None = Query(default=None),
    barrio: str | None = Query(default=None),
    estrato: int | None = Query(default=None),
    precio_min: float | None = Query(default=None),
    precio_max: float | None = Query(default=None),
    metros_min: float | None = Query(default=None),
    metros_max: float | None = Query(default=None),
    estado_activo: bool | None = Query(default=None),
    fecha_control_from: datetime | None = Query(default=None),
    fecha_control_to: datetime | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedPropertyResponse:
    """List properties with combinable filters and pagination."""
    query = select(EsquemaInmueble)

    # Apply filters — all optional, all combinable
    if sitio_origen is not None:
        query = query.where(EsquemaInmueble.sitio_origen == sitio_origen)
    if tipo_inmueble is not None:
        query = query.where(EsquemaInmueble.tipo_inmueble == tipo_inmueble)
    if operacion is not None:
        query = query.where(EsquemaInmueble.operacion == operacion)
    if municipio is not None:
        query = query.where(EsquemaInmueble.municipio == municipio)
    if sector is not None:
        query = query.where(EsquemaInmueble.sector == sector)
    if barrio is not None:
        query = query.where(EsquemaInmueble.barrio == barrio)
    if estrato is not None:
        query = query.where(EsquemaInmueble.estrato == estrato)
    if precio_min is not None:
        query = query.where(EsquemaInmueble.precio_local >= precio_min)
    if precio_max is not None:
        query = query.where(EsquemaInmueble.precio_local <= precio_max)
    if metros_min is not None:
        query = query.where(EsquemaInmueble.metros_utiles >= metros_min)
    if metros_max is not None:
        query = query.where(EsquemaInmueble.metros_utiles <= metros_max)
    if estado_activo is not None:
        query = query.where(EsquemaInmueble.estado_activo == estado_activo)
    if fecha_control_from is not None:
        query = query.where(EsquemaInmueble.fecha_control >= fecha_control_from)
    if fecha_control_to is not None:
        query = query.where(EsquemaInmueble.fecha_control <= fecha_control_to)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    pages = math.ceil(total / size) if total > 0 else 0
    offset = (page - 1) * size

    # Fetch paginated results
    query = query.order_by(EsquemaInmueble.fecha_control.desc().nullslast())
    query = query.offset(offset).limit(size)
    result = await db.execute(query)
    properties = result.scalars().all()

    items = [PropertyListItem.model_validate(p) for p in properties]

    return PaginatedPropertyResponse(
        items=items, total=total, page=page, pages=pages
    )


@router.get(
    "/properties/{property_id}",
    response_model=PropertyDetail,
    dependencies=[Depends(RBACMiddleware("dashboard:read"))],
)
async def get_property(
    property_id: int,
    db: AsyncSession = Depends(get_db),
) -> PropertyDetail:
    """Get a single property with all 66 fields."""
    result = await db.execute(
        select(EsquemaInmueble).where(
            EsquemaInmueble.id_interno == property_id
        )
    )
    prop = result.scalar_one_or_none()
    if prop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Propiedad con id={property_id} no encontrada",
        )
    return PropertyDetail.model_validate(prop)


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


@router.get(
    "/summary",
    response_model=SummaryResponse,
    dependencies=[Depends(RBACMiddleware("dashboard:read"))],
)
async def get_summary(
    db: AsyncSession = Depends(get_db),
) -> SummaryResponse:
    """Get dashboard summary: totals by Sitio_Origen, Operacion, active count, last task."""
    # Total active records
    active_result = await db.execute(
        select(func.count()).where(EsquemaInmueble.estado_activo.is_(True))
    )
    total_active = active_result.scalar() or 0

    # Count by Sitio_Origen
    sitio_result = await db.execute(
        select(
            EsquemaInmueble.sitio_origen,
            func.count().label("count"),
        )
        .where(EsquemaInmueble.sitio_origen.isnot(None))
        .group_by(EsquemaInmueble.sitio_origen)
        .order_by(func.count().desc())
    )
    by_sitio = [
        CountByField(value=row.sitio_origen, count=row.count)
        for row in sitio_result.all()
    ]

    # Count by Operacion
    op_result = await db.execute(
        select(
            EsquemaInmueble.operacion,
            func.count().label("count"),
        )
        .where(EsquemaInmueble.operacion.isnot(None))
        .group_by(EsquemaInmueble.operacion)
        .order_by(func.count().desc())
    )
    by_operacion = [
        CountByField(value=row.operacion, count=row.count)
        for row in op_result.all()
    ]

    # Last successful task
    last_task_result = await db.execute(
        select(TareaScraping.ended_at)
        .where(TareaScraping.status == "success")
        .order_by(TareaScraping.ended_at.desc().nullslast())
        .limit(1)
    )
    last_task_row = last_task_result.scalar_one_or_none()

    return SummaryResponse(
        total_active=total_active,
        by_sitio_origen=by_sitio,
        by_operacion=by_operacion,
        last_successful_task=last_task_row,
    )


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


@router.get(
    "/errors",
    response_model=PaginatedErrorResponse,
    dependencies=[Depends(RBACMiddleware("dashboard:read"))],
)
async def list_errors(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=100),
    error_type: str | None = Query(default=None),
    sitio_origen: str | None = Query(default=None),
    task_id: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedErrorResponse:
    """List errors with filters and pagination."""
    query = select(LogError)

    if error_type is not None:
        query = query.where(LogError.error_type == error_type)
    if sitio_origen is not None:
        query = query.where(LogError.sitio_origen == sitio_origen)
    if task_id is not None:
        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="task_id debe ser un UUID válido",
            )
        query = query.where(LogError.task_id == task_uuid)
    if date_from is not None:
        query = query.where(LogError.created_at >= date_from)
    if date_to is not None:
        query = query.where(LogError.created_at <= date_to)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    pages = math.ceil(total / size) if total > 0 else 0
    offset = (page - 1) * size

    query = query.order_by(LogError.created_at.desc())
    query = query.offset(offset).limit(size)
    result = await db.execute(query)
    errors = result.scalars().all()

    items = [
        ErrorListItem(
            id=e.id,
            task_id=str(e.task_id),
            sitio_origen=e.sitio_origen,
            url=e.url,
            error_type=e.error_type,
            error_message=e.error_message,
            error_metadata=e.error_metadata,
            correlation_id=e.correlation_id,
            created_at=e.created_at,
        )
        for e in errors
    ]

    return PaginatedErrorResponse(
        items=items, total=total, page=page, pages=pages
    )


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------


@router.get(
    "/tasks",
    response_model=PaginatedTaskResponse,
    dependencies=[Depends(RBACMiddleware("tasks:read"))],
)
async def list_tasks(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    task_status: str | None = Query(default=None, alias="status"),
    config_id: int | None = Query(default=None),
    sitio_origen: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedTaskResponse:
    """List tasks with filters and pagination."""
    query = select(TareaScraping)

    if task_status is not None:
        query = query.where(TareaScraping.status == task_status)
    if config_id is not None:
        query = query.where(TareaScraping.config_id == config_id)
    if sitio_origen is not None:
        # Join with config to filter by sitio_origen (derived from url_base)
        from app.models.configuracion_scraping import ConfiguracionScraping

        query = query.join(
            ConfiguracionScraping,
            TareaScraping.config_id == ConfiguracionScraping.id,
        ).where(ConfiguracionScraping.url_base.contains(sitio_origen))
    if date_from is not None:
        query = query.where(TareaScraping.started_at >= date_from)
    if date_to is not None:
        query = query.where(TareaScraping.started_at <= date_to)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    pages_count = math.ceil(total / size) if total > 0 else 0
    offset = (page - 1) * size

    query = query.order_by(TareaScraping.started_at.desc().nullslast())
    query = query.offset(offset).limit(size)
    result = await db.execute(query)
    tasks = result.scalars().all()

    items = [
        TaskListItem(
            task_id=str(t.task_id),
            config_id=t.config_id,
            status=t.status,
            started_at=t.started_at,
            ended_at=t.ended_at,
            duration_seconds=t.duration_seconds,
            pages_processed=t.pages_processed,
            records_extracted=t.records_extracted,
            records_inserted=t.records_inserted,
            records_updated=t.records_updated,
            records_skipped=t.records_skipped,
            correlation_id=t.correlation_id,
        )
        for t in tasks
    ]

    return PaginatedTaskResponse(
        items=items, total=total, page=page, pages=pages_count
    )


@router.get(
    "/tasks/{task_id}",
    response_model=TaskDetail,
    dependencies=[Depends(RBACMiddleware("tasks:read"))],
)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
) -> TaskDetail:
    """Get a single task with full execution summary including correlation_id."""
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="task_id debe ser un UUID válido",
        )

    result = await db.execute(
        select(TareaScraping).where(TareaScraping.task_id == task_uuid)
    )
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarea con id={task_id} no encontrada",
        )

    return TaskDetail(
        task_id=str(task.task_id),
        config_id=task.config_id,
        status=task.status,
        started_at=task.started_at,
        ended_at=task.ended_at,
        duration_seconds=task.duration_seconds,
        pages_processed=task.pages_processed,
        records_extracted=task.records_extracted,
        records_inserted=task.records_inserted,
        records_updated=task.records_updated,
        records_skipped=task.records_skipped,
        errors_by_type=task.errors_by_type,
        correlation_id=task.correlation_id,
    )
