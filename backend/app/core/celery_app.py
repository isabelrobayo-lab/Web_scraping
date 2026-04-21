"""Celery application configuration with Redis broker and Celery Beat.

Provides the Celery application instance configured for async task execution
(scraping, exports) and scheduled tasks via Celery Beat.

Usage:
    from app.core.celery_app import celery_app
"""

from celery import Celery
from celery.schedules import crontab  # noqa: F401 — available for schedule definitions

from app.core.config import settings

celery_app = Celery(
    "scraping_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Serialization configuration
celery_app.conf.update(
    # Task serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Reliability: acknowledge tasks after execution (not before)
    task_acks_late=True,
    # Reject tasks on worker shutdown so they get requeued
    task_reject_on_worker_lost=True,
    # Worker concurrency (default to prefork pool)
    worker_concurrency=4,
    worker_prefetch_multiplier=1,
    # Result expiration (24 hours)
    result_expires=86400,
    # Task tracking
    task_track_started=True,
)

# Celery Beat schedule configuration
# Populated dynamically from Configuracion_Scraping cron expressions (Task 13.3)
celery_app.conf.beat_schedule = {}

# Autodiscover tasks from the app.tasks package
celery_app.autodiscover_tasks(["app.tasks", "app.exports"])

# Register Correlation_ID propagation signals
import app.middleware.celery_correlation  # noqa: E402, F401
