"""Error logging service for scraping task errors.

Implements structured error classification, metadata recording,
and execution summary generation as specified in Req 7.

Error types: Timeout, CAPTCHA, Estructura, Conexion
Each error includes a Correlation_ID for end-to-end traceability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.log_error import LogError
from app.models.tarea_scraping import TareaScraping

logger = structlog.get_logger(__name__)


# Valid error type classifications
VALID_ERROR_TYPES = frozenset({"Timeout", "CAPTCHA", "Estructura", "Conexion"})


@dataclass
class ScrapingError:
    """Structured scraping error with type classification and metadata."""

    error_type: str
    sitio_origen: str
    url: str | None = None
    message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate error_type is one of the allowed classifications."""
        if self.error_type not in VALID_ERROR_TYPES:
            raise ValueError(
                f"Invalid error_type '{self.error_type}'. "
                f"Must be one of: {', '.join(sorted(VALID_ERROR_TYPES))}"
            )


@dataclass
class ExecutionSummary:
    """Summary of a scraping task execution."""

    task_id: str
    pages_processed: int = 0
    records_extracted: int = 0
    records_inserted: int = 0
    records_updated: int = 0
    records_skipped: int = 0
    errors_by_type: dict[str, int] = field(default_factory=dict)
    duration_seconds: float = 0.0


class ErrorLogger:
    """Structured error logging for scraping tasks.

    Classifies errors by type and records type-specific metadata:
    - Timeout: timeout_threshold, elapsed_time
    - CAPTCHA: url, page_title
    - Estructura: field_name, expected_selector, sitio_origen
    - Conexion: url, connection_error_details
    """

    async def log(
        self,
        session: AsyncSession,
        task_id: str,
        error: ScrapingError,
        correlation_id: str,
    ) -> LogError:
        """Persist a classified error in the log_error table.

        Args:
            session: Active async database session.
            task_id: UUID of the associated TareaScraping.
            error: Structured error with type and metadata.
            correlation_id: Correlation ID for traceability.

        Returns:
            The persisted LogError instance.
        """
        log_entry = LogError(
            task_id=task_id,
            sitio_origen=error.sitio_origen,
            url=error.url,
            error_type=error.error_type,
            error_message=error.message,
            error_metadata=error.metadata,
            correlation_id=correlation_id,
            created_at=datetime.utcnow(),
        )

        session.add(log_entry)
        await session.flush()

        logger.warning(
            "Scraping error logged",
            error_type=error.error_type,
            sitio_origen=error.sitio_origen,
            url=error.url,
            correlation_id=correlation_id,
            task_id=task_id,
        )

        return log_entry

    async def generate_summary(
        self,
        session: AsyncSession,
        task_id: str,
    ) -> ExecutionSummary:
        """Generate execution summary with detailed counts.

        Reads task counters and aggregates errors by type.

        Args:
            session: Active async database session.
            task_id: UUID of the TareaScraping to summarize.

        Returns:
            ExecutionSummary with all counts and error breakdown.
        """
        # Fetch task record
        stmt = select(TareaScraping).where(TareaScraping.task_id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()

        if task is None:
            logger.error("Task not found for summary generation", task_id=task_id)
            return ExecutionSummary(task_id=str(task_id))

        # Aggregate errors by type
        error_stmt = (
            select(LogError.error_type, func.count(LogError.id))
            .where(LogError.task_id == task_id)
            .group_by(LogError.error_type)
        )
        error_result = await session.execute(error_stmt)
        errors_by_type = {row[0]: row[1] for row in error_result.all()}

        return ExecutionSummary(
            task_id=str(task_id),
            pages_processed=task.pages_processed,
            records_extracted=task.records_extracted,
            records_inserted=task.records_inserted,
            records_updated=task.records_updated,
            records_skipped=task.records_skipped,
            errors_by_type=errors_by_type,
            duration_seconds=task.duration_seconds or 0.0,
        )

    @staticmethod
    def create_timeout_error(
        sitio_origen: str,
        url: str,
        timeout_threshold: float,
        elapsed_time: float,
        message: str | None = None,
    ) -> ScrapingError:
        """Create a Timeout error with appropriate metadata."""
        return ScrapingError(
            error_type="Timeout",
            sitio_origen=sitio_origen,
            url=url,
            message=message or f"Request timed out after {elapsed_time:.1f}s (threshold: {timeout_threshold:.1f}s)",
            metadata={
                "timeout_threshold": timeout_threshold,
                "elapsed_time": elapsed_time,
            },
        )

    @staticmethod
    def create_captcha_error(
        sitio_origen: str,
        url: str,
        page_title: str | None = None,
        message: str | None = None,
    ) -> ScrapingError:
        """Create a CAPTCHA error with appropriate metadata."""
        return ScrapingError(
            error_type="CAPTCHA",
            sitio_origen=sitio_origen,
            url=url,
            message=message or "CAPTCHA detected on page",
            metadata={
                "url": url,
                "page_title": page_title,
            },
        )

    @staticmethod
    def create_estructura_error(
        sitio_origen: str,
        url: str | None,
        field_name: str,
        expected_selector: str,
        message: str | None = None,
    ) -> ScrapingError:
        """Create an Estructura (structure) error with appropriate metadata."""
        return ScrapingError(
            error_type="Estructura",
            sitio_origen=sitio_origen,
            url=url,
            message=message or f"Expected selector '{expected_selector}' not found for field '{field_name}'",
            metadata={
                "field_name": field_name,
                "expected_selector": expected_selector,
                "sitio_origen": sitio_origen,
            },
        )

    @staticmethod
    def create_conexion_error(
        sitio_origen: str,
        url: str,
        connection_error_details: str,
        message: str | None = None,
    ) -> ScrapingError:
        """Create a Conexion (connection) error with appropriate metadata."""
        return ScrapingError(
            error_type="Conexion",
            sitio_origen=sitio_origen,
            url=url,
            message=message or f"Connection error: {connection_error_details}",
            metadata={
                "url": url,
                "connection_error_details": connection_error_details,
            },
        )
