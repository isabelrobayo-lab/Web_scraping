"""WebSocket hub for managing connected clients and broadcasting messages.

Manages a set of connected WebSocket clients and provides methods to
broadcast messages to all connected clients. Integrates with Redis Pub/Sub
to forward task status changes and progress updates.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import structlog
from fastapi import WebSocket

logger = structlog.get_logger(__name__)

# Redis Pub/Sub channel (same as ProgressPublisher)
PROGRESS_CHANNEL = "scraping:progress"


class WebSocketHub:
    """Manages WebSocket connections and message broadcasting.

    Thread-safe management of connected WebSocket clients with
    Redis Pub/Sub integration for real-time task notifications.
    """

    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """Register a new WebSocket connection."""
        async with self._lock:
            self._connections.add(websocket)
        logger.debug(
            "WebSocket client connected",
            total_connections=len(self._connections),
        )

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        async with self._lock:
            self._connections.discard(websocket)
        logger.debug(
            "WebSocket client disconnected",
            total_connections=len(self._connections),
        )

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Send a message to all connected WebSocket clients.

        Disconnected clients are automatically removed.
        """
        if not self._connections:
            return

        payload = json.dumps(message)
        disconnected: list[WebSocket] = []

        async with self._lock:
            connections = list(self._connections)

        for ws in connections:
            try:
                await ws.send_text(payload)
            except Exception:
                disconnected.append(ws)

        # Clean up disconnected clients
        if disconnected:
            async with self._lock:
                for ws in disconnected:
                    self._connections.discard(ws)

    @property
    def connection_count(self) -> int:
        """Return the number of active connections."""
        return len(self._connections)


# Singleton hub instance
hub = WebSocketHub()


async def redis_pubsub_listener() -> None:
    """Background task that listens to Redis Pub/Sub and forwards messages.

    Subscribes to the scraping:progress channel and broadcasts received
    messages to all connected WebSocket clients.

    Reconnects automatically on Redis connection errors.
    """
    import redis.asyncio as aioredis

    from app.core.config import settings

    while True:
        try:
            redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
            )
            pubsub = redis_client.pubsub()
            await pubsub.subscribe(PROGRESS_CHANNEL)

            logger.info(
                "Redis Pub/Sub listener started",
                channel=PROGRESS_CHANNEL,
            )

            async for raw_message in pubsub.listen():
                if raw_message["type"] != "message":
                    continue

                try:
                    message = json.loads(raw_message["data"])
                    await hub.broadcast(message)
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(
                        "Invalid message from Redis Pub/Sub",
                        error=str(e),
                    )

        except Exception as e:
            logger.error(
                "Redis Pub/Sub listener error, reconnecting in 5s",
                error=str(e),
            )
            await asyncio.sleep(5)
