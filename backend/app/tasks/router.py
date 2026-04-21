"""Task execution API endpoints.

Provides:
- POST /api/v1/tasks/{config_id}/execute — Manual execution with concurrent guard
"""

from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import RBACMiddleware, UserClaims
from app.core.database import get_db
from app.middleware.correlation_id import correlation_id_ctx
from app.models.configuracion_scraping import ConfiguracionScraping
from app.models.tarea_scraping import TareaScraping

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


class ExecuteResponse(BaseModel):
    """Response for task execution request."""

    task_id: str
    status: str
    correlation_id: str


@router.post(
    "/{config_id}/execute",
    response_model=ExecuteResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(RBACMiddleware("tasks:execute"))],
)
async def execute_task(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserClaims = Depends(RBACMiddleware("tasks:execute")),
) -> ExecuteResponse:
    """Trigger manual execution of a scraping task for a configuration.

    Creates a TareaScraping record with status 'queued' and enqueues
    a Celery task for execution.

    Concurrent execution guard: rejects if a task with status 'queued'
    or 'running' already exists for this config_id.

    Returns:
        202 with task_id, status, and correlation_id.

    Raises:
        404: Configuration not found.
        409: A task is already running/queued for this configuration.
    """
    # Verify configuration exists and is active
    result = await db.execute(
        select(ConfiguracionScraping).where(
            ConfiguracionScraping.id == config_id,
            ConfiguracionScraping.active.is_(True),
        )
    )
    config = result.scalar_one_or_none()
    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuración con id={config_id} no encontrada o inactiva",
        )

    # Concurrent execution guard: check for queued or running tasks
    existing_result = await db.execute(
        select(TareaScraping).where(
            TareaScraping.config_id == config_id,
            TareaScraping.status.in_(["queued", "running"]),
        )
    )
    existing_task = existing_result.scalar_one_or_none()
    if existing_task is not None:
        logger.warning(
            "Concurrent execution rejected",
            config_id=config_id,
            existing_task_id=str(existing_task.task_id),
            existing_status=existing_task.status,
            correlation_id=correlation_id_ctx.get(),
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una tarea en ejecución para esta configuración",
        )

    # Get current correlation_id
    correlation_id = correlation_id_ctx.get() or str(uuid.uuid4())

    # Create TareaScraping record
    task_id = uuid.uuid4()
    tarea = TareaScraping(
        task_id=task_id,
        config_id=config_id,
        status="queued",
        correlation_id=correlation_id,
    )
    db.add(tarea)
    await db.flush()

    # Enqueue Celery task
    from app.tasks.scraping import execute_scraping

    execute_scraping.apply_async(
        args=[str(task_id), config_id, correlation_id],
        task_id=str(task_id),
        headers={"correlation_id": correlation_id},
    )

    logger.info(
        "Scraping task enqueued",
        task_id=str(task_id),
        config_id=config_id,
        correlation_id=correlation_id,
    )

    return ExecuteResponse(
        task_id=str(task_id),
        status="queued",
        correlation_id=correlation_id,
    )
