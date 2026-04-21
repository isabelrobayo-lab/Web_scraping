"""Unit tests for ErrorLogger service.

Tests error type classification, metadata recording per type,
and execution summary generation (Task 10.4).
"""

import uuid
from datetime import datetime

import pytest
from sqlalchemy import select

from app.data_logic.error_logger import (
    ErrorLogger,
    ExecutionSummary,
    ScrapingError,
    VALID_ERROR_TYPES,
)
from app.models.log_error import LogError
from app.models.tarea_scraping import TareaScraping


# ---------------------------------------------------------------------------
# Error type classification tests
# ---------------------------------------------------------------------------


class TestErrorTypeClassification:
    """Test that ScrapingError validates error types correctly."""

    def test_valid_error_types(self):
        """All valid error types should be accepted."""
        for error_type in VALID_ERROR_TYPES:
            error = ScrapingError(
                error_type=error_type,
                sitio_origen="test.com",
            )
            assert error.error_type == error_type

    def test_invalid_error_type_raises(self):
        """Invalid error types should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid error_type"):
            ScrapingError(
                error_type="InvalidType",
                sitio_origen="test.com",
            )

    def test_timeout_error_creation(self):
        """Timeout error should have correct metadata structure."""
        error = ErrorLogger.create_timeout_error(
            sitio_origen="example-site.com",
            url="https://example-site.com/listing/123",
            timeout_threshold=30.0,
            elapsed_time=35.5,
        )

        assert error.error_type == "Timeout"
        assert error.sitio_origen == "example-site.com"
        assert error.url == "https://example-site.com/listing/123"
        assert error.metadata["timeout_threshold"] == 30.0
        assert error.metadata["elapsed_time"] == 35.5
        assert "timed out" in error.message

    def test_captcha_error_creation(self):
        """CAPTCHA error should have correct metadata structure."""
        error = ErrorLogger.create_captcha_error(
            sitio_origen="example-realestate.com",
            url="https://example-realestate.com/search",
            page_title="Verify you are human",
        )

        assert error.error_type == "CAPTCHA"
        assert error.sitio_origen == "example-realestate.com"
        assert error.metadata["url"] == "https://example-realestate.com/search"
        assert error.metadata["page_title"] == "Verify you are human"

    def test_estructura_error_creation(self):
        """Estructura error should have correct metadata structure."""
        error = ErrorLogger.create_estructura_error(
            sitio_origen="example-props.com",
            url="https://example-props.com/property/456",
            field_name="Precio_Local",
            expected_selector="span.price-value",
        )

        assert error.error_type == "Estructura"
        assert error.metadata["field_name"] == "Precio_Local"
        assert error.metadata["expected_selector"] == "span.price-value"
        assert error.metadata["sitio_origen"] == "example-props.com"

    def test_conexion_error_creation(self):
        """Conexion error should have correct metadata structure."""
        error = ErrorLogger.create_conexion_error(
            sitio_origen="example-listings.com",
            url="https://example-listings.com/listings",
            connection_error_details="Connection refused: ECONNREFUSED",
        )

        assert error.error_type == "Conexion"
        assert error.metadata["url"] == "https://example-listings.com/listings"
        assert error.metadata["connection_error_details"] == "Connection refused: ECONNREFUSED"


# ---------------------------------------------------------------------------
# Error logging persistence tests
# ---------------------------------------------------------------------------


class TestErrorLogging:
    """Test error persistence to database."""

    @pytest.mark.asyncio
    async def test_log_persists_error(self, db_session):
        """Logging an error should persist it in the database."""
        # Create a task first (required FK)
        task_id = uuid.uuid4()
        task = TareaScraping(
            task_id=task_id,
            config_id=1,
            status="running",
        )
        db_session.add(task)
        await db_session.flush()

        error_logger = ErrorLogger()
        error = ErrorLogger.create_timeout_error(
            sitio_origen="test.com",
            url="https://test.com/page",
            timeout_threshold=30.0,
            elapsed_time=45.0,
        )

        correlation_id = str(uuid.uuid4())
        log_entry = await error_logger.log(
            db_session, str(task_id), error, correlation_id
        )

        assert log_entry.id is not None
        assert log_entry.error_type == "Timeout"
        assert log_entry.correlation_id == correlation_id
        assert log_entry.sitio_origen == "test.com"

    @pytest.mark.asyncio
    async def test_log_preserves_metadata(self, db_session):
        """Logged error should preserve all metadata."""
        task_id = uuid.uuid4()
        task = TareaScraping(
            task_id=task_id,
            config_id=1,
            status="running",
        )
        db_session.add(task)
        await db_session.flush()

        error_logger = ErrorLogger()
        error = ErrorLogger.create_captcha_error(
            sitio_origen="example.com",
            url="https://example.com/captcha",
            page_title="Robot Check",
        )

        log_entry = await error_logger.log(
            db_session, str(task_id), error, "corr-123"
        )

        assert log_entry.error_metadata["url"] == "https://example.com/captcha"
        assert log_entry.error_metadata["page_title"] == "Robot Check"


# ---------------------------------------------------------------------------
# Execution summary tests
# ---------------------------------------------------------------------------


class TestExecutionSummary:
    """Test execution summary generation."""

    @pytest.mark.asyncio
    async def test_generate_summary_with_counts(self, db_session):
        """Summary should reflect task counters and error aggregation."""
        task_id = uuid.uuid4()
        task = TareaScraping(
            task_id=task_id,
            config_id=1,
            status="success",
            pages_processed=50,
            records_extracted=200,
            records_inserted=150,
            records_updated=30,
            records_skipped=20,
            duration_seconds=120.5,
        )
        db_session.add(task)
        await db_session.flush()

        # Add some errors
        for i in range(3):
            db_session.add(LogError(
                task_id=task_id,
                sitio_origen="test.com",
                error_type="Timeout",
                error_message=f"Timeout error {i}",
                correlation_id="corr-1",
                created_at=datetime.utcnow(),
            ))
        for i in range(2):
            db_session.add(LogError(
                task_id=task_id,
                sitio_origen="test.com",
                error_type="Conexion",
                error_message=f"Connection error {i}",
                correlation_id="corr-1",
                created_at=datetime.utcnow(),
            ))
        await db_session.flush()

        error_logger = ErrorLogger()
        summary = await error_logger.generate_summary(db_session, str(task_id))

        assert summary.task_id == str(task_id)
        assert summary.pages_processed == 50
        assert summary.records_extracted == 200
        assert summary.records_inserted == 150
        assert summary.records_updated == 30
        assert summary.records_skipped == 20
        assert summary.duration_seconds == 120.5
        assert summary.errors_by_type == {"Timeout": 3, "Conexion": 2}

    @pytest.mark.asyncio
    async def test_generate_summary_missing_task(self, db_session):
        """Summary for non-existent task should return empty summary."""
        error_logger = ErrorLogger()
        fake_id = str(uuid.uuid4())
        summary = await error_logger.generate_summary(db_session, fake_id)

        assert summary.task_id == fake_id
        assert summary.pages_processed == 0
        assert summary.records_extracted == 0
        assert summary.errors_by_type == {}

    @pytest.mark.asyncio
    async def test_generate_summary_no_errors(self, db_session):
        """Summary with no errors should have empty errors_by_type."""
        task_id = uuid.uuid4()
        task = TareaScraping(
            task_id=task_id,
            config_id=1,
            status="success",
            pages_processed=10,
            records_extracted=50,
            records_inserted=50,
            records_updated=0,
            records_skipped=0,
            duration_seconds=30.0,
        )
        db_session.add(task)
        await db_session.flush()

        error_logger = ErrorLogger()
        summary = await error_logger.generate_summary(db_session, str(task_id))

        assert summary.errors_by_type == {}
        assert summary.pages_processed == 10
