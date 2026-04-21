"""Structured logging configuration using structlog.

Emits JSON logs with standardized fields: timestamp, level, service,
correlation_id, and message. Additional fields can be passed via kwargs.

Usage:
    from app.core.logging import get_logger

    logger = get_logger()
    logger.info("Task started", task_id="abc-123", config_id=1)
"""

import logging
import sys

import structlog

from app.core.config import settings
from app.middleware.correlation_id import correlation_id_ctx


def _add_correlation_id(
    logger: logging.Logger, method_name: str, event_dict: dict
) -> dict:
    """Processor that injects the current correlation_id from context."""
    event_dict["correlation_id"] = correlation_id_ctx.get() or ""
    return event_dict


def _add_service_name(
    logger: logging.Logger, method_name: str, event_dict: dict
) -> dict:
    """Processor that injects the service name from settings."""
    event_dict["service"] = settings.APP_NAME
    return event_dict


def configure_logging() -> None:
    """Configure structlog for JSON structured logging.

    Call this once at application startup (e.g., in main.py).
    """
    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        _add_service_name,
        _add_correlation_id,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging to use structlog formatter
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO if not settings.DEBUG else logging.DEBUG)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Optional logger name. Defaults to the calling module.

    Returns:
        A structlog BoundLogger that emits JSON with standard fields.
    """
    return structlog.get_logger(name)
