# Feature: web-scraping-platform, Property 22, Property 23
"""Property-based tests for Observability Layer (Req 14).

Property 22: Correlation_ID Propagation
    For any API request, the system SHALL generate a unique Correlation_ID
    and propagate it through response headers, associated records, and log entries.

Property 23: Structured Log Format
    For any log entry emitted by the system, the JSON output SHALL contain:
    timestamp, level, service, correlation_id, and message.
"""

import json
import logging
import uuid
from io import StringIO

import pytest
import structlog
from hypothesis import given, settings
from hypothesis import strategies as st

from app.middleware.correlation_id import (
    HEADER_NAME,
    CorrelationIDMiddleware,
    correlation_id_ctx,
)


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Valid UUID4 strings
uuid_strategy = st.uuids(version=4).map(str)

# Arbitrary non-empty strings for log messages
log_message_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z")),
    min_size=1,
    max_size=200,
)

# Log levels
log_level_strategy = st.sampled_from(["debug", "info", "warning", "error", "critical"])


# ---------------------------------------------------------------------------
# Property 22: Correlation_ID Propagation
# ---------------------------------------------------------------------------


class TestCorrelationIDPropagation:
    """Property 22: Correlation_ID Propagation.

    **Validates: Requirements 14.1**

    For any API request, the system SHALL generate a unique Correlation_ID
    and propagate it through response headers, associated records, and log entries.
    """

    @given(uuid_strategy)
    @settings(max_examples=50)
    def test_incoming_correlation_id_is_preserved_in_response(self, cid: str):
        """When a request includes X-Correlation-ID, the same value appears
        in the response headers."""
        from starlette.testclient import TestClient

        from app.main import app

        client = TestClient(app)
        response = client.get("/api/v1/health", headers={HEADER_NAME: cid})

        assert response.status_code == 200
        assert response.headers.get(HEADER_NAME) == cid

    @given(st.integers(min_value=1, max_value=100))
    @settings(max_examples=20)
    def test_missing_correlation_id_generates_valid_uuid(self, _: int):
        """When a request does NOT include X-Correlation-ID, the system
        generates a valid UUID4 and returns it in the response headers."""
        from starlette.testclient import TestClient

        from app.main import app

        client = TestClient(app)
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        returned_cid = response.headers.get(HEADER_NAME)
        assert returned_cid is not None
        # Validate it's a proper UUID
        parsed = uuid.UUID(returned_cid, version=4)
        assert str(parsed) == returned_cid

    @given(uuid_strategy, uuid_strategy)
    @settings(max_examples=30)
    def test_different_requests_get_different_correlation_ids(
        self, cid1: str, cid2: str
    ):
        """Two requests with different incoming Correlation_IDs get different
        response Correlation_IDs."""
        from starlette.testclient import TestClient

        from app.main import app

        client = TestClient(app)
        r1 = client.get("/api/v1/health", headers={HEADER_NAME: cid1})
        r2 = client.get("/api/v1/health", headers={HEADER_NAME: cid2})

        assert r1.headers.get(HEADER_NAME) == cid1
        assert r2.headers.get(HEADER_NAME) == cid2

    @given(uuid_strategy)
    @settings(max_examples=30)
    def test_correlation_id_context_variable_is_set(self, cid: str):
        """The correlation_id context variable is accessible during request
        processing and matches the header value."""
        from starlette.testclient import TestClient

        from app.main import app

        captured_cid = None

        # Temporarily add a route that captures the context variable
        @app.get("/api/v1/_test_cid_capture")
        async def _capture_cid():
            nonlocal captured_cid
            captured_cid = correlation_id_ctx.get()
            return {"cid": captured_cid}

        client = TestClient(app)
        response = client.get(
            "/api/v1/_test_cid_capture", headers={HEADER_NAME: cid}
        )

        assert response.status_code == 200
        assert captured_cid == cid

        # Cleanup: remove the test route
        app.routes[:] = [r for r in app.routes if getattr(r, "path", "") != "/api/v1/_test_cid_capture"]


# ---------------------------------------------------------------------------
# Property 23: Structured Log Format
# ---------------------------------------------------------------------------


class TestStructuredLogFormat:
    """Property 23: Structured Log Format.

    **Validates: Requirements 14.2**

    For any log entry emitted by the system, the JSON output SHALL contain:
    timestamp, level, service, correlation_id, and message.
    """

    @given(log_message_strategy, log_level_strategy, uuid_strategy)
    @settings(max_examples=50)
    def test_log_output_contains_required_fields(
        self, message: str, level: str, cid: str
    ):
        """Every log entry emitted contains timestamp, level, service,
        correlation_id, and message (event) fields."""
        from app.core.config import settings as app_settings
        from app.core.logging import configure_logging

        # Set correlation_id in context
        token = correlation_id_ctx.set(cid)

        try:
            # Reconfigure logging to capture output
            configure_logging()

            # Capture log output
            stream = StringIO()
            handler = logging.StreamHandler(stream)

            formatter = structlog.stdlib.ProcessorFormatter(
                processors=[
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.processors.JSONRenderer(),
                ],
            )
            handler.setFormatter(formatter)

            test_logger = logging.getLogger(f"test.{uuid.uuid4().hex[:8]}")
            test_logger.handlers.clear()
            test_logger.addHandler(handler)
            test_logger.setLevel(logging.DEBUG)

            # Get a structlog logger bound to our test stdlib logger
            logger = structlog.wrap_logger(test_logger)

            # Emit a log at the specified level
            log_method = getattr(logger, level)
            log_method(message)

            # Parse the output
            output = stream.getvalue().strip()
            assert output, f"No log output for level={level}, message={message!r}"

            log_entry = json.loads(output)

            # Verify required fields
            assert "timestamp" in log_entry, f"Missing 'timestamp' in {log_entry}"
            assert "level" in log_entry, f"Missing 'level' in {log_entry}"
            assert "service" in log_entry, f"Missing 'service' in {log_entry}"
            assert "correlation_id" in log_entry, f"Missing 'correlation_id' in {log_entry}"
            assert "event" in log_entry, f"Missing 'event' (message) in {log_entry}"

            # Verify field values
            assert log_entry["level"] == level
            assert log_entry["service"] == app_settings.APP_NAME
            assert log_entry["correlation_id"] == cid
            assert log_entry["event"] == message

        finally:
            correlation_id_ctx.reset(token)

    @given(log_message_strategy, uuid_strategy)
    @settings(max_examples=30)
    def test_log_timestamp_is_iso_format(self, message: str, cid: str):
        """The timestamp field in log entries is in ISO 8601 format."""
        from datetime import datetime

        from app.core.logging import configure_logging

        token = correlation_id_ctx.set(cid)

        try:
            configure_logging()

            stream = StringIO()
            handler = logging.StreamHandler(stream)

            formatter = structlog.stdlib.ProcessorFormatter(
                processors=[
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.processors.JSONRenderer(),
                ],
            )
            handler.setFormatter(formatter)

            test_logger = logging.getLogger(f"test.ts.{uuid.uuid4().hex[:8]}")
            test_logger.handlers.clear()
            test_logger.addHandler(handler)
            test_logger.setLevel(logging.DEBUG)

            logger = structlog.wrap_logger(test_logger)
            logger.info(message)

            output = stream.getvalue().strip()
            log_entry = json.loads(output)

            timestamp = log_entry["timestamp"]
            # Should be parseable as ISO 8601
            parsed_dt = datetime.fromisoformat(timestamp)
            assert parsed_dt is not None

        finally:
            correlation_id_ctx.reset(token)

    @given(
        st.dictionaries(
            keys=st.text(
                alphabet=st.characters(whitelist_categories=("L",)),
                min_size=1,
                max_size=20,
            ),
            values=st.one_of(st.text(max_size=50), st.integers(), st.floats(allow_nan=False)),
            min_size=1,
            max_size=5,
        ),
        uuid_strategy,
    )
    @settings(max_examples=30)
    def test_additional_kwargs_are_included_in_log(
        self, extra_fields: dict, cid: str
    ):
        """Additional keyword arguments passed to the logger are included
        in the JSON output alongside the required fields."""
        from app.core.logging import configure_logging

        token = correlation_id_ctx.set(cid)

        try:
            configure_logging()

            stream = StringIO()
            handler = logging.StreamHandler(stream)

            formatter = structlog.stdlib.ProcessorFormatter(
                processors=[
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.processors.JSONRenderer(),
                ],
            )
            handler.setFormatter(formatter)

            test_logger = logging.getLogger(f"test.extra.{uuid.uuid4().hex[:8]}")
            test_logger.handlers.clear()
            test_logger.addHandler(handler)
            test_logger.setLevel(logging.DEBUG)

            logger = structlog.wrap_logger(test_logger)
            logger.info("test_event", **extra_fields)

            output = stream.getvalue().strip()
            log_entry = json.loads(output)

            # Required fields still present
            assert "timestamp" in log_entry
            assert "level" in log_entry
            assert "service" in log_entry
            assert "correlation_id" in log_entry

            # Extra fields are included
            for key, value in extra_fields.items():
                if key not in ("timestamp", "level", "service", "correlation_id", "event"):
                    assert key in log_entry

        finally:
            correlation_id_ctx.reset(token)
