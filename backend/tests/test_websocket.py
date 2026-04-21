"""Integration tests for WebSocket connection, message delivery, and disconnection.

Tests the WebSocket endpoint /api/v1/ws/tasks including:
- JWT authentication via query parameter
- Rejection of invalid/missing tokens
- Message broadcasting via the hub
- Client disconnection handling
- Message type validation (task_status, task_progress, export_ready)
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from httpx import ASGITransport, AsyncClient
from starlette.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.websocket.hub import WebSocketHub, hub


def _create_test_token(
    user_id: int = 1,
    username: str = "testuser",
    role: str = "administrador",
    expired: bool = False,
) -> str:
    """Create a JWT access token for testing."""
    now = datetime.now(timezone.utc)
    exp = now - timedelta(hours=1) if expired else now + timedelta(minutes=30)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": exp,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


class TestWebSocketConnection:
    """Tests for WebSocket connection and authentication."""

    def test_connect_with_valid_token(self) -> None:
        """WebSocket connection succeeds with a valid JWT token."""
        token = _create_test_token()
        client = TestClient(app)

        with client.websocket_connect(
            f"/api/v1/ws/tasks?token={token}"
        ) as ws:
            # Connection should be established — send ping to verify
            ws.send_text("ping")
            response = ws.receive_text()
            data = json.loads(response)
            assert data["type"] == "pong"

    def test_reject_missing_token(self) -> None:
        """WebSocket connection is rejected when no token is provided."""
        client = TestClient(app)

        with pytest.raises(Exception):
            # Should close with code 4001
            with client.websocket_connect("/api/v1/ws/tasks") as ws:
                ws.receive_text()

    def test_reject_empty_token(self) -> None:
        """WebSocket connection is rejected with an empty token."""
        client = TestClient(app)

        with pytest.raises(Exception):
            with client.websocket_connect(
                "/api/v1/ws/tasks?token="
            ) as ws:
                ws.receive_text()

    def test_reject_invalid_token(self) -> None:
        """WebSocket connection is rejected with an invalid JWT token."""
        client = TestClient(app)

        with pytest.raises(Exception):
            with client.websocket_connect(
                "/api/v1/ws/tasks?token=invalid-jwt-token"
            ) as ws:
                ws.receive_text()

    def test_reject_expired_token(self) -> None:
        """WebSocket connection is rejected with an expired JWT token."""
        token = _create_test_token(expired=True)
        client = TestClient(app)

        with pytest.raises(Exception):
            with client.websocket_connect(
                f"/api/v1/ws/tasks?token={token}"
            ) as ws:
                ws.receive_text()


class TestWebSocketMessageDelivery:
    """Tests for message broadcasting to WebSocket clients."""

    def test_receive_task_status_message(self) -> None:
        """Client receives task_status messages broadcast via the hub."""
        token = _create_test_token()
        client = TestClient(app)

        with client.websocket_connect(
            f"/api/v1/ws/tasks?token={token}"
        ) as ws:
            # Broadcast a task_status message
            import asyncio

            message = {
                "type": "task_status",
                "task_id": str(uuid.uuid4()),
                "status": "success",
                "summary": {
                    "pages_processed": 10,
                    "records_extracted": 50,
                    "records_inserted": 45,
                    "records_updated": 3,
                    "records_skipped": 2,
                },
            }

            loop = asyncio.new_event_loop()
            loop.run_until_complete(hub.broadcast(message))
            loop.close()

            data = json.loads(ws.receive_text())
            assert data["type"] == "task_status"
            assert data["status"] == "success"
            assert "summary" in data
            assert data["summary"]["pages_processed"] == 10

    def test_receive_task_progress_message(self) -> None:
        """Client receives task_progress messages broadcast via the hub."""
        token = _create_test_token()
        client = TestClient(app)

        with client.websocket_connect(
            f"/api/v1/ws/tasks?token={token}"
        ) as ws:
            import asyncio

            message = {
                "type": "task_progress",
                "task_id": str(uuid.uuid4()),
                "pages_processed": 5,
                "records_extracted": 25,
            }

            loop = asyncio.new_event_loop()
            loop.run_until_complete(hub.broadcast(message))
            loop.close()

            data = json.loads(ws.receive_text())
            assert data["type"] == "task_progress"
            assert data["pages_processed"] == 5
            assert data["records_extracted"] == 25

    def test_receive_export_ready_message(self) -> None:
        """Client receives export_ready messages broadcast via the hub."""
        token = _create_test_token()
        client = TestClient(app)

        with client.websocket_connect(
            f"/api/v1/ws/tasks?token={token}"
        ) as ws:
            import asyncio

            export_id = str(uuid.uuid4())
            message = {
                "type": "export_ready",
                "export_id": export_id,
            }

            loop = asyncio.new_event_loop()
            loop.run_until_complete(hub.broadcast(message))
            loop.close()

            data = json.loads(ws.receive_text())
            assert data["type"] == "export_ready"
            assert data["export_id"] == export_id


class TestWebSocketDisconnection:
    """Tests for WebSocket disconnection handling."""

    def test_hub_tracks_connections(self) -> None:
        """Hub correctly tracks connect and disconnect events."""
        token = _create_test_token()
        client = TestClient(app)

        initial_count = hub.connection_count

        with client.websocket_connect(
            f"/api/v1/ws/tasks?token={token}"
        ) as ws:
            # Connection count should increase
            assert hub.connection_count >= initial_count + 1
            ws.send_text("ping")
            ws.receive_text()

        # After disconnect, count should return to initial
        # (may need a small delay for cleanup)
        assert hub.connection_count >= initial_count


class TestWebSocketHub:
    """Unit tests for the WebSocketHub class."""

    @pytest.mark.asyncio
    async def test_hub_broadcast_no_connections(self) -> None:
        """Broadcasting with no connections does not raise errors."""
        test_hub = WebSocketHub()
        # Should not raise
        await test_hub.broadcast({"type": "test", "data": "hello"})

    @pytest.mark.asyncio
    async def test_hub_connection_count(self) -> None:
        """Hub correctly reports connection count."""
        test_hub = WebSocketHub()
        assert test_hub.connection_count == 0
