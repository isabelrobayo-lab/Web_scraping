"""Progress publishing via Redis Pub/Sub during scraping execution.

Publishes real-time progress updates including:
- task_id: The scraping task identifier
- pages_processed: Number of pages processed so far
- records_extracted: Number of records extracted so far
"""

from __future__ import annotations

import json
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)

# Redis Pub/Sub channel for task progress
PROGRESS_CHANNEL = "scraping:progress"


class ProgressPublisher:
    """Publishes scraping progress via Redis Pub/Sub.

    Sends progress messages during execution so that WebSocket
    clients can receive real-time updates.
    """

    def __init__(self, redis_client: Optional[Any] = None) -> None:
        """Initialize the progress publisher.

        Args:
            redis_client: An async Redis client instance.
                         If None, publishing is a no-op (useful for testing).
        """
        self._redis = redis_client

    async def publish_progress(
        self,
        task_id: str,
        pages_processed: int,
        records_extracted: int,
    ) -> None:
        """Publish a progress update via Redis Pub/Sub.

        Args:
            task_id: The scraping task identifier.
            pages_processed: Number of pages processed so far.
            records_extracted: Number of records extracted so far.
        """
        message = {
            "type": "task_progress",
            "task_id": task_id,
            "pages_processed": pages_processed,
            "records_extracted": records_extracted,
        }

        if self._redis is not None:
            try:
                await self._redis.publish(
                    PROGRESS_CHANNEL,
                    json.dumps(message),
                )
                logger.debug(
                    "Progress published",
                    task_id=task_id,
                    pages_processed=pages_processed,
                    records_extracted=records_extracted,
                )
            except Exception as e:
                logger.error(
                    "Failed to publish progress",
                    task_id=task_id,
                    error=str(e),
                )
        else:
            logger.debug(
                "Progress publish skipped (no Redis client)",
                task_id=task_id,
                pages_processed=pages_processed,
                records_extracted=records_extracted,
            )

    async def publish_completion(
        self,
        task_id: str,
        status: str,
        pages_processed: int,
        records_extracted: int,
        records_inserted: int = 0,
        records_updated: int = 0,
        records_skipped: int = 0,
    ) -> None:
        """Publish a task completion message via Redis Pub/Sub.

        Args:
            task_id: The scraping task identifier.
            status: Final task status (success, partial_success, failure).
            pages_processed: Total pages processed.
            records_extracted: Total records extracted.
            records_inserted: Total records inserted.
            records_updated: Total records updated.
            records_skipped: Total records skipped.
        """
        message = {
            "type": "task_status",
            "task_id": task_id,
            "status": status,
            "pages_processed": pages_processed,
            "records_extracted": records_extracted,
            "records_inserted": records_inserted,
            "records_updated": records_updated,
            "records_skipped": records_skipped,
        }

        if self._redis is not None:
            try:
                await self._redis.publish(
                    PROGRESS_CHANNEL,
                    json.dumps(message),
                )
                logger.info(
                    "Task completion published",
                    task_id=task_id,
                    status=status,
                )
            except Exception as e:
                logger.error(
                    "Failed to publish completion",
                    task_id=task_id,
                    error=str(e),
                )
        else:
            logger.debug(
                "Completion publish skipped (no Redis client)",
                task_id=task_id,
                status=status,
            )
