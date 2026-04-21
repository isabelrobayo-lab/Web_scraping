"""WebSocket endpoint for real-time task notifications.

Provides:
- WS /api/v1/ws/tasks?token={jwt_access_token} — Authenticated WebSocket

Message types sent to clients:
- task_status: { "type": "task_status", "task_id": str, "status": str, "summary": {...} }
- task_progress: { "type": "task_progress", "task_id": str, "pages_processed": int, "records_extracted": int }
- export_ready: { "type": "export_ready", "export_id": str }
"""

from __future__ import annotations

import structlog
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from app.auth.service import AuthService
from app.websocket.hub import hub

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/tasks")
async def websocket_tasks(
    websocket: WebSocket,
    token: str = Query(default=""),
) -> None:
    """WebSocket endpoint for real-time task notifications.

    Authenticates the client using a JWT token passed as a query parameter.
    Once authenticated, the client receives all task status changes,
    progress updates, and export ready notifications.

    Message types:
    - task_status: Task status changed (queued, running, success, etc.)
    - task_progress: Real-time progress (pages processed, records extracted)
    - export_ready: Export file is ready for download

    Close codes:
    - 4001: Authentication failed (invalid or missing token)
    """
    # Validate JWT token from query parameter
    if not token:
        await websocket.close(code=4001, reason="Token de acceso requerido")
        return

    auth_service = AuthService(db=None)  # No DB needed for token verification
    user_claims = auth_service.verify_token(token)

    if user_claims is None:
        await websocket.close(code=4001, reason="Token inválido o expirado")
        return

    # Accept the WebSocket connection
    await websocket.accept()
    await hub.connect(websocket)

    logger.info(
        "WebSocket client authenticated",
        username=user_claims.username,
        role=user_claims.role,
    )

    try:
        # Keep the connection alive — listen for client messages (ping/pong)
        while True:
            # Wait for any message from the client (keeps connection alive)
            # Clients can send ping messages; we just read and discard
            data = await websocket.receive_text()
            # Optional: handle client-side ping
            if data == "ping":
                await websocket.send_text('{"type": "pong"}')
    except WebSocketDisconnect:
        logger.info(
            "WebSocket client disconnected",
            username=user_claims.username,
        )
    except Exception as e:
        logger.warning(
            "WebSocket connection error",
            username=user_claims.username,
            error=str(e),
        )
    finally:
        await hub.disconnect(websocket)
