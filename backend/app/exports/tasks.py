"""Celery tasks for asynchronous export generation.

Handles large dataset exports (>100k records) via background processing.
Publishes export_ready notification via Redis Pub/Sub on completion.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import structlog

from app.core.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="app.exports.tasks.generate_export_task", bind=True)
def generate_export_task(
    self,
    export_id: str,
    export_format: str,
    filters: dict | None = None,
) -> dict:
    """Celery task for asynchronous export generation.

    Queries the database synchronously (Celery worker context),
    generates the export file, updates the Exportacion record,
    and publishes an export_ready notification via Redis Pub/Sub.

    Args:
        export_id: UUID of the Exportacion record.
        export_format: One of 'csv', 'excel', 'json'.
        filters: Optional property filters to apply.

    Returns:
        Dict with export_id, status, record_count, file_path.
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import Session

    from app.core.config import settings
    from app.exports.service import generate_export

    # Build sync database URL from async URL
    sync_url = settings.DATABASE_URL.replace(
        "postgresql+asyncpg", "postgresql+psycopg2"
    ).replace("postgresql+aiosqlite", "sqlite")

    engine = create_engine(sync_url)

    try:
        with Session(engine) as session:
            # Build query with filters
            query_parts = ["SELECT * FROM esquema_inmueble WHERE 1=1"]
            params: dict = {}

            if filters:
                if filters.get("sitio_origen"):
                    query_parts.append("AND sitio_origen = :sitio_origen")
                    params["sitio_origen"] = filters["sitio_origen"]
                if filters.get("tipo_inmueble"):
                    query_parts.append("AND tipo_inmueble = :tipo_inmueble")
                    params["tipo_inmueble"] = filters["tipo_inmueble"]
                if filters.get("operacion"):
                    query_parts.append("AND operacion = :operacion")
                    params["operacion"] = filters["operacion"]
                if filters.get("municipio"):
                    query_parts.append("AND municipio = :municipio")
                    params["municipio"] = filters["municipio"]
                if filters.get("estado_activo") is not None:
                    query_parts.append("AND estado_activo = :estado_activo")
                    params["estado_activo"] = filters["estado_activo"]
                if filters.get("precio_min") is not None:
                    query_parts.append("AND precio_local >= :precio_min")
                    params["precio_min"] = filters["precio_min"]
                if filters.get("precio_max") is not None:
                    query_parts.append("AND precio_local <= :precio_max")
                    params["precio_max"] = filters["precio_max"]

            sql = " ".join(query_parts)
            result = session.execute(text(sql), params)
            rows = result.mappings().all()
            records = [dict(row) for row in rows]

            # Generate the export file
            file_path, record_count = generate_export(
                records, export_format, export_id
            )

            # Update the Exportacion record
            session.execute(
                text(
                    "UPDATE exportacion SET status = :status, "
                    "record_count = :count, file_path = :path, "
                    "completed_at = :completed "
                    "WHERE export_id = :eid"
                ),
                {
                    "status": "ready",
                    "count": record_count,
                    "path": file_path,
                    "completed": datetime.now(timezone.utc),
                    "eid": export_id,
                },
            )
            session.commit()

        # Publish export_ready notification via Redis
        _publish_export_ready(export_id)

        logger.info(
            "Async export completed",
            export_id=export_id,
            format=export_format,
            record_count=record_count,
        )

        return {
            "export_id": export_id,
            "status": "ready",
            "record_count": record_count,
            "file_path": file_path,
        }

    except Exception as exc:
        logger.error(
            "Async export failed",
            export_id=export_id,
            error=str(exc),
        )
        # Mark export as failed
        try:
            with Session(engine) as session:
                session.execute(
                    text(
                        "UPDATE exportacion SET status = 'failed', "
                        "completed_at = :completed "
                        "WHERE export_id = :eid"
                    ),
                    {
                        "completed": datetime.now(timezone.utc),
                        "eid": export_id,
                    },
                )
                session.commit()
        except Exception:
            pass
        raise


def _publish_export_ready(export_id: str) -> None:
    """Publish export_ready message via Redis Pub/Sub."""
    import redis

    from app.core.config import settings

    try:
        r = redis.from_url(settings.REDIS_URL)
        message = json.dumps({
            "type": "export_ready",
            "export_id": export_id,
        })
        r.publish("scraping:progress", message)
        logger.debug("Export ready notification published", export_id=export_id)
    except Exception as e:
        logger.warning(
            "Failed to publish export_ready notification",
            export_id=export_id,
            error=str(e),
        )
