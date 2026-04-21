"""Celery Beat dynamic schedule from Configuracion_Scraping cron expressions.

Provides a function to build the beat_schedule dict from active configurations
with modo_ejecucion='Programado' and a valid cron_expression. Also provides
a periodic task that refreshes the schedule from the database.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone

import structlog
from croniter import croniter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.celery_app import celery_app
from app.core.config import settings
from app.models.configuracion_scraping import ConfiguracionScraping
from app.models.tarea_scraping import TareaScraping

logger = structlog.get_logger(__name__)


def parse_cron_to_celery_schedule(cron_expr: str) -> dict | None:
    """Parse a 5-field cron expression into Celery crontab kwargs.

    Args:
        cron_expr: A standard 5-field cron expression (minute hour dom month dow).

    Returns:
        dict with keys minute, hour, day_of_month, month_of_year, day_of_week
        suitable for celery.schedules.crontab, or None if invalid.
    """
    if not cron_expr or not cron_expr.strip():
        return None

    parts = cron_expr.strip().split()
    if len(parts) != 5:
        return None

    try:
        # Validate with croniter
        croniter(cron_expr)
    except (ValueError, KeyError):
        return None

    return {
        "minute": parts[0],
        "hour": parts[1],
        "day_of_month": parts[2],
        "month_of_year": parts[3],
        "day_of_week": parts[4],
    }


async def _get_scheduled_configs() -> list[dict]:
    """Fetch all active scheduled configurations from the database."""
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=2,
        max_overflow=1,
    )
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    configs = []
    async with session_factory() as db:
        result = await db.execute(
            select(ConfiguracionScraping).where(
                ConfiguracionScraping.active.is_(True),
                ConfiguracionScraping.modo_ejecucion == "Programado",
                ConfiguracionScraping.cron_expression.isnot(None),
            )
        )
        for config in result.scalars().all():
            configs.append({
                "id": config.id,
                "cron_expression": config.cron_expression,
                "url_base": config.url_base,
            })

    await engine.dispose()
    return configs


def build_beat_schedule() -> dict:
    """Build Celery Beat schedule from active scheduled configurations.

    Returns:
        dict suitable for celery_app.conf.beat_schedule.
    """
    from celery.schedules import crontab

    loop = asyncio.new_event_loop()
    try:
        configs = loop.run_until_complete(_get_scheduled_configs())
    finally:
        loop.close()

    schedule = {}
    for config in configs:
        cron_kwargs = parse_cron_to_celery_schedule(config["cron_expression"])
        if cron_kwargs is None:
            logger.warning(
                "Invalid cron expression for config, skipping",
                config_id=config["id"],
                cron_expression=config["cron_expression"],
            )
            continue

        schedule_name = f"scraping-config-{config['id']}"
        schedule[schedule_name] = {
            "task": "tasks.execute_scheduled_scraping",
            "schedule": crontab(**cron_kwargs),
            "args": [config["id"]],
        }

        logger.info(
            "Scheduled scraping config registered",
            config_id=config["id"],
            cron_expression=config["cron_expression"],
        )

    return schedule


async def _execute_scheduled(config_id: int) -> dict:
    """Create a TareaScraping and enqueue the scraping task for a scheduled config.

    Includes concurrent execution guard — skips if a task is already
    queued or running for this config_id.
    """
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=2,
        max_overflow=1,
    )
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as db:
        # Concurrent execution guard
        existing_result = await db.execute(
            select(TareaScraping).where(
                TareaScraping.config_id == config_id,
                TareaScraping.status.in_(["queued", "running"]),
            )
        )
        existing_task = existing_result.scalar_one_or_none()
        if existing_task is not None:
            logger.warning(
                "Scheduled execution skipped — task already running",
                config_id=config_id,
                existing_task_id=str(existing_task.task_id),
                existing_status=existing_task.status,
            )
            await engine.dispose()
            return {"status": "skipped", "reason": "concurrent_task_exists"}

        # Create TareaScraping record
        correlation_id = str(uuid.uuid4())
        task_id = uuid.uuid4()
        tarea = TareaScraping(
            task_id=task_id,
            config_id=config_id,
            status="queued",
            correlation_id=correlation_id,
        )
        db.add(tarea)
        await db.commit()

    await engine.dispose()

    # Enqueue Celery task
    from app.tasks.scraping import execute_scraping

    execute_scraping.apply_async(
        args=[str(task_id), config_id, correlation_id],
        task_id=str(task_id),
        headers={"correlation_id": correlation_id},
    )

    logger.info(
        "Scheduled scraping task enqueued",
        task_id=str(task_id),
        config_id=config_id,
        correlation_id=correlation_id,
    )

    return {
        "status": "queued",
        "task_id": str(task_id),
        "correlation_id": correlation_id,
    }


@celery_app.task(name="tasks.execute_scheduled_scraping")
def execute_scheduled_scraping(config_id: int) -> dict:
    """Celery task triggered by Beat for scheduled scraping executions.

    Creates a TareaScraping record and delegates to the main scraping task.
    Includes concurrent execution guard.

    Args:
        config_id: ID of the ConfiguracionScraping to execute.

    Returns:
        dict with task_id and status.
    """
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(_execute_scheduled(config_id))
        return result
    finally:
        loop.close()
