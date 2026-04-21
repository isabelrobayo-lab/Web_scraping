"""Export API endpoints.

Provides:
- POST /api/v1/exports                  — Create export (sync or async)
- GET  /api/v1/exports/{id}/status      — Check export status
- GET  /api/v1/exports/{id}/download    — Download completed export file
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import RBACMiddleware, UserClaims
from app.core.config import settings
from app.core.database import get_db
from app.dashboard.schemas import ExportCreateResponse, ExportRequest, ExportStatusResponse
from app.exports.service import generate_export, get_content_type, get_file_extension
from app.models.esquema_inmueble import EsquemaInmueble
from app.models.exportacion import Exportacion

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/exports", tags=["exports"])


@router.post(
    "",
    response_model=ExportCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_export(
    payload: ExportRequest,
    current_user: UserClaims = Depends(RBACMiddleware("dashboard:export")),
    db: AsyncSession = Depends(get_db),
) -> ExportCreateResponse:
    """Create a data export.

    For small datasets (<100k records), generates synchronously.
    For large datasets (>=100k records), dispatches to Celery worker.
    """
    if payload.format not in ("csv", "excel", "json"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Formato debe ser 'csv', 'excel' o 'json'",
        )

    export_id = uuid.uuid4()

    # Count matching records to decide sync vs async
    count_query = select(func.count()).select_from(EsquemaInmueble)
    filters = payload.filters or {}

    if filters.get("sitio_origen"):
        count_query = count_query.where(
            EsquemaInmueble.sitio_origen == filters["sitio_origen"]
        )
    if filters.get("tipo_inmueble"):
        count_query = count_query.where(
            EsquemaInmueble.tipo_inmueble == filters["tipo_inmueble"]
        )
    if filters.get("operacion"):
        count_query = count_query.where(
            EsquemaInmueble.operacion == filters["operacion"]
        )
    if filters.get("municipio"):
        count_query = count_query.where(
            EsquemaInmueble.municipio == filters["municipio"]
        )
    if filters.get("estado_activo") is not None:
        count_query = count_query.where(
            EsquemaInmueble.estado_activo == filters["estado_activo"]
        )
    if filters.get("precio_min") is not None:
        count_query = count_query.where(
            EsquemaInmueble.precio_local >= filters["precio_min"]
        )
    if filters.get("precio_max") is not None:
        count_query = count_query.where(
            EsquemaInmueble.precio_local <= filters["precio_max"]
        )

    count_result = await db.execute(count_query)
    total_records = count_result.scalar() or 0

    # Create Exportacion record
    exportacion = Exportacion(
        export_id=export_id,
        user_id=current_user.user_id,
        format=payload.format,
        filters=payload.filters,
        status="processing",
        record_count=0,
    )
    db.add(exportacion)
    await db.flush()

    if total_records >= settings.EXPORT_ASYNC_THRESHOLD:
        # Async export via Celery
        from app.exports.tasks import generate_export_task

        generate_export_task.delay(
            str(export_id),
            payload.format,
            payload.filters,
        )
        logger.info(
            "Async export dispatched",
            export_id=str(export_id),
            format=payload.format,
            estimated_records=total_records,
        )
    else:
        # Sync export — fetch records and generate file inline
        try:
            records = await _fetch_filtered_records(db, filters)
            file_path, record_count = generate_export(
                records, payload.format, str(export_id)
            )
            exportacion.status = "ready"
            exportacion.record_count = record_count
            exportacion.file_path = file_path
            exportacion.completed_at = datetime.now(timezone.utc)
            await db.flush()

            logger.info(
                "Sync export completed",
                export_id=str(export_id),
                format=payload.format,
                record_count=record_count,
            )
        except Exception as exc:
            exportacion.status = "failed"
            exportacion.completed_at = datetime.now(timezone.utc)
            await db.flush()
            logger.error(
                "Sync export failed",
                export_id=str(export_id),
                error=str(exc),
            )

    return ExportCreateResponse(
        export_id=str(export_id),
        status=exportacion.status,
    )


@router.get(
    "/{export_id}/status",
    response_model=ExportStatusResponse,
    dependencies=[Depends(RBACMiddleware("dashboard:export"))],
)
async def get_export_status(
    export_id: str,
    db: AsyncSession = Depends(get_db),
) -> ExportStatusResponse:
    """Check the status of an export."""
    try:
        eid = uuid.UUID(export_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="export_id debe ser un UUID válido",
        )

    result = await db.execute(
        select(Exportacion).where(Exportacion.export_id == eid)
    )
    export = result.scalar_one_or_none()
    if export is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exportación con id={export_id} no encontrada",
        )

    return ExportStatusResponse(
        export_id=str(export.export_id),
        status=export.status,
        record_count=export.record_count,
    )


@router.get(
    "/{export_id}/download",
    dependencies=[Depends(RBACMiddleware("dashboard:export"))],
)
async def download_export(
    export_id: str,
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Download a completed export file."""
    try:
        eid = uuid.UUID(export_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="export_id debe ser un UUID válido",
        )

    result = await db.execute(
        select(Exportacion).where(Exportacion.export_id == eid)
    )
    export = result.scalar_one_or_none()
    if export is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exportación con id={export_id} no encontrada",
        )

    if export.status != "ready":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Exportación no está lista (status={export.status})",
        )

    if not export.file_path or not Path(export.file_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo de exportación no encontrado",
        )

    content_type = get_content_type(export.format)
    ext = get_file_extension(export.format)
    filename = f"export_{export_id}{ext}"

    return FileResponse(
        path=export.file_path,
        media_type=content_type,
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


async def _fetch_filtered_records(
    db: AsyncSession,
    filters: dict,
) -> list[dict]:
    """Fetch property records matching the given filters."""
    query = select(EsquemaInmueble)

    if filters.get("sitio_origen"):
        query = query.where(EsquemaInmueble.sitio_origen == filters["sitio_origen"])
    if filters.get("tipo_inmueble"):
        query = query.where(EsquemaInmueble.tipo_inmueble == filters["tipo_inmueble"])
    if filters.get("operacion"):
        query = query.where(EsquemaInmueble.operacion == filters["operacion"])
    if filters.get("municipio"):
        query = query.where(EsquemaInmueble.municipio == filters["municipio"])
    if filters.get("estado_activo") is not None:
        query = query.where(EsquemaInmueble.estado_activo == filters["estado_activo"])
    if filters.get("precio_min") is not None:
        query = query.where(EsquemaInmueble.precio_local >= filters["precio_min"])
    if filters.get("precio_max") is not None:
        query = query.where(EsquemaInmueble.precio_local <= filters["precio_max"])

    result = await db.execute(query)
    rows = result.scalars().all()

    records = []
    for row in rows:
        record = {}
        for col in EsquemaInmueble.__table__.columns:
            val = getattr(row, col.name)
            record[col.name] = val
        records.append(record)

    return records
