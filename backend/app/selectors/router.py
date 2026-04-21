"""API endpoints for Mapa_Selectores management.

Provides:
- GET  /api/v1/selector-maps/{sitio_origen}  — Get latest selector map version
- PUT  /api/v1/selector-maps/{sitio_origen}  — Create/update selector map (new version)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import RBACMiddleware
from app.core.database import get_db
from app.models.mapa_selectores import MapaSelectores
from app.selectors.schemas import SelectorMapResponse, SelectorMapUpdate

router = APIRouter(prefix="/selector-maps", tags=["selector-maps"])


@router.get(
    "/{sitio_origen}",
    response_model=SelectorMapResponse,
    dependencies=[Depends(RBACMiddleware("configs:read"))],
)
async def get_selector_map(
    sitio_origen: str,
    db: AsyncSession = Depends(get_db),
) -> SelectorMapResponse:
    """Get the latest version of a selector map for a given sitio_origen."""
    result = await db.execute(
        select(MapaSelectores)
        .where(MapaSelectores.sitio_origen == sitio_origen)
        .order_by(MapaSelectores.version.desc())
        .limit(1)
    )
    selector_map = result.scalar_one_or_none()

    if selector_map is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mapa de selectores para '{sitio_origen}' no encontrado",
        )

    return SelectorMapResponse(
        sitio_origen=selector_map.sitio_origen,
        version=selector_map.version,
        mappings=selector_map.mappings,
        created_at=selector_map.created_at,
    )


@router.put(
    "/{sitio_origen}",
    response_model=SelectorMapResponse,
    dependencies=[Depends(RBACMiddleware("configs:write"))],
)
async def update_selector_map(
    sitio_origen: str,
    payload: SelectorMapUpdate,
    db: AsyncSession = Depends(get_db),
) -> SelectorMapResponse:
    """Create or update a selector map for a given sitio_origen.

    Creates a NEW record with version = previous_version + 1.
    The previous version record is preserved (not modified).
    If no map exists, creates version 1.
    """
    # Find the current latest version
    result = await db.execute(
        select(MapaSelectores)
        .where(MapaSelectores.sitio_origen == sitio_origen)
        .order_by(MapaSelectores.version.desc())
        .limit(1)
    )
    current_map = result.scalar_one_or_none()

    # Determine new version number
    new_version = (current_map.version + 1) if current_map else 1

    # Create new version record (previous version is preserved)
    new_map = MapaSelectores(
        sitio_origen=sitio_origen,
        version=new_version,
        mappings=payload.mappings,
    )
    db.add(new_map)
    await db.flush()
    await db.refresh(new_map)

    return SelectorMapResponse(
        sitio_origen=new_map.sitio_origen,
        version=new_map.version,
        mappings=new_map.mappings,
        created_at=new_map.created_at,
    )
