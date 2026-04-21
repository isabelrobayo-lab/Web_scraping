"""Example Celery task for health check verification.

This task validates that the Celery worker is running and can process tasks.
"""

from app.core.celery_app import celery_app


@celery_app.task(name="tasks.health_check")
def health_check() -> dict:
    """Simple health check task to verify Celery worker connectivity.

    Returns:
        dict with status and message confirming the worker is operational.
    """
    return {"status": "ok", "message": "Celery worker is operational"}
