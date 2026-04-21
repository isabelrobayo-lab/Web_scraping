"""Celery task for scraping execution with Correlation_ID propagation.

Wraps ScrapingEngine.execute as a Celery task, propagating the Correlation_ID
via task headers (set up in celery_correlation.py). Updates TareaScraping
status in the database throughout the execution lifecycle.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.celery_app import celery_app
from app.core.config import settings
from app.middleware.correlation_id import correlation_id_ctx
from app.models.configuracion_scraping import ConfiguracionScraping
from app.models.mapa_selectores import MapaSelectores
from app.models.tarea_scraping import TareaScraping

logger = structlog.get_logger(__name__)


def _get_async_session_factory() -> async_sessionmaker:
    """Create an async session factory for use inside Celery workers."""
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        pool_size=5,
        max_overflow=2,
    )
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def _run_scraping_task(
    task_id: str,
    config_id: int,
    correlation_id: str,
) -> dict:
    """Async implementation of the scraping task.

    Loads configuration and selector map, runs the ScrapingEngine,
    and updates TareaScraping status throughout the lifecycle.
    """
    from app.engine.scraping_engine import ScrapingEngine

    session_factory = _get_async_session_factory()

    async with session_factory() as db:
        # Update task status to running
        now = datetime.now(timezone.utc)
        await db.execute(
            update(TareaScraping)
            .where(TareaScraping.task_id == uuid.UUID(task_id))
            .values(status="running", started_at=now)
        )
        await db.commit()

        # Load configuration
        result = await db.execute(
            select(ConfiguracionScraping).where(
                ConfiguracionScraping.id == config_id
            )
        )
        config = result.scalar_one_or_none()

        if config is None:
            await db.execute(
                update(TareaScraping)
                .where(TareaScraping.task_id == uuid.UUID(task_id))
                .values(
                    status="failure",
                    ended_at=datetime.now(timezone.utc),
                    errors_by_type={"Configuracion": 1},
                )
            )
            await db.commit()
            return {"status": "failure", "error": "Configuration not found"}

        # Derive sitio_origen from URL
        from urllib.parse import urlparse

        parsed = urlparse(config.url_base)
        sitio_origen = parsed.netloc or config.url_base

        # Load latest selector map for this sitio_origen
        selector_result = await db.execute(
            select(MapaSelectores)
            .where(MapaSelectores.sitio_origen == sitio_origen)
            .order_by(MapaSelectores.version.desc())
            .limit(1)
        )
        selector_map_record = selector_result.scalar_one_or_none()

        selector_map = {}
        selector_map_version = 0
        if selector_map_record:
            selector_map = selector_map_record.mappings or {}
            selector_map_version = selector_map_record.version

        # Log ENGINE start (Req 14.3)
        logger.info(
            "ENGINE start",
            task_id=task_id,
            config_id=config_id,
            sitio_origen=sitio_origen,
            profundidad=config.profundidad_navegacion,
            selector_map_version=selector_map_version,
            correlation_id=correlation_id,
        )

        # Execute scraping engine
        engine = ScrapingEngine()
        try:
            exec_result = await engine.execute(
                task_id=task_id,
                base_url=config.url_base,
                max_depth=config.profundidad_navegacion,
                selector_map=selector_map,
                sitio_origen=sitio_origen,
                correlation_id=correlation_id,
            )

            # Determine final status
            final_status = exec_result.status
            ended_at = datetime.now(timezone.utc)
            started_at_result = await db.execute(
                select(TareaScraping.started_at).where(
                    TareaScraping.task_id == uuid.UUID(task_id)
                )
            )
            started_at = started_at_result.scalar_one_or_none() or now
            duration = (ended_at - started_at).total_seconds()

            # Classify errors by type
            errors_by_type: dict[str, int] = {}
            for err in exec_result.errors:
                err_type = err.get("error_type", "Unknown")
                errors_by_type[err_type] = errors_by_type.get(err_type, 0) + 1

            # Update task with results
            await db.execute(
                update(TareaScraping)
                .where(TareaScraping.task_id == uuid.UUID(task_id))
                .values(
                    status=final_status,
                    ended_at=ended_at,
                    duration_seconds=duration,
                    pages_processed=exec_result.pages_processed,
                    records_extracted=exec_result.records_extracted,
                    errors_by_type=errors_by_type if errors_by_type else None,
                )
            )

            # Update last_execution_at on the configuration
            await db.execute(
                update(ConfiguracionScraping)
                .where(ConfiguracionScraping.id == config_id)
                .values(last_execution_at=ended_at)
            )
            await db.commit()

            logger.info(
                "Scraping task completed",
                task_id=task_id,
                status=final_status,
                pages_processed=exec_result.pages_processed,
                records_extracted=exec_result.records_extracted,
                duration_seconds=duration,
                correlation_id=correlation_id,
            )

            return {
                "status": final_status,
                "pages_processed": exec_result.pages_processed,
                "records_extracted": exec_result.records_extracted,
                "duration_seconds": duration,
            }

        except Exception as e:
            ended_at = datetime.now(timezone.utc)
            duration = (ended_at - now).total_seconds()

            await db.execute(
                update(TareaScraping)
                .where(TareaScraping.task_id == uuid.UUID(task_id))
                .values(
                    status="failure",
                    ended_at=ended_at,
                    duration_seconds=duration,
                    errors_by_type={"CriticalError": 1},
                )
            )
            await db.commit()

            logger.error(
                "Scraping task failed",
                task_id=task_id,
                error=str(e),
                correlation_id=correlation_id,
            )

            return {"status": "failure", "error": str(e)}


@celery_app.task(
    name="tasks.execute_scraping",
    bind=True,
    max_retries=0,
    acks_late=True,
)
def execute_scraping(
    self,
    task_id: str,
    config_id: int,
    correlation_id: str,
) -> dict:
    """Celery task that executes a scraping job.

    Propagates Correlation_ID from task headers (injected by celery_correlation.py).
    Wraps the async ScrapingEngine.execute in an event loop.

    Args:
        task_id: UUID of the TareaScraping record.
        config_id: ID of the ConfiguracionScraping to execute.
        correlation_id: Correlation_ID for traceability.

    Returns:
        dict with execution results (status, counts, duration).
    """
    # Set correlation_id in context (also done by signal, but ensure it's set)
    cid = correlation_id
    if not cid:
        # Try to get from task headers
        request = self.request
        if hasattr(request, "headers") and request.headers:
            cid = request.headers.get("correlation_id", "")
    if cid:
        correlation_id_ctx.set(cid)

    logger.info(
        "Celery scraping task started",
        task_id=task_id,
        config_id=config_id,
        correlation_id=cid,
    )

    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(
            _run_scraping_task(task_id, config_id, cid)
        )
        return result
    finally:
        loop.close()
