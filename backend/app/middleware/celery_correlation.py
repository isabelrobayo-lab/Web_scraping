"""Correlation_ID propagation to Celery tasks via task headers.

Uses Celery signals to inject the current Correlation_ID into task headers
before publishing, and to extract it on the worker side before task execution.

This module should be imported at Celery app startup to register the signals.

Usage:
    # In celery_app.py or app startup:
    import app.middleware.celery_correlation  # noqa: F401 — registers signals
"""

from celery import current_task
from celery.signals import before_task_publish, task_prerun

from app.middleware.correlation_id import correlation_id_ctx

HEADER_KEY = "correlation_id"


@before_task_publish.connect
def inject_correlation_id(headers: dict | None = None, **kwargs) -> None:
    """Inject the current Correlation_ID into Celery task headers before publishing.

    This signal fires on the producer side (API/scheduler) when a task is
    about to be sent to the broker.
    """
    if headers is None:
        return

    cid = correlation_id_ctx.get()
    if cid:
        headers[HEADER_KEY] = cid


@task_prerun.connect
def extract_correlation_id(task_id: str | None = None, task=None, **kwargs) -> None:
    """Extract Correlation_ID from task headers and set it in the context variable.

    This signal fires on the worker side just before a task starts executing.
    """
    if task is None:
        return

    request = task.request
    cid = ""

    # Try to get correlation_id from task headers
    if hasattr(request, "headers") and request.headers:
        cid = request.headers.get(HEADER_KEY, "")
    elif hasattr(request, "get") and callable(request.get):
        cid = request.get(HEADER_KEY, "")

    if cid:
        correlation_id_ctx.set(cid)
