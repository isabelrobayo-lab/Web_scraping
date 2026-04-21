"""Crawl queue with depth control, URL deduplication, and visited URL tracking.

Implements a FIFO queue for URLs to process during scraping, with:
- Depth control: respects Profundidad_Navegacion limit
- URL deduplication: never enqueues a URL already visited or already in queue
- Visited URL tracking: maintains a set of all processed URLs
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Optional

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class CrawlItem:
    """An item in the crawl queue.

    Attributes:
        url: The URL to crawl.
        depth: The depth level of this URL relative to the base URL.
    """

    url: str
    depth: int


class CrawlQueue:
    """URL queue with depth control and deduplication.

    Manages the crawl frontier for a scraping session, ensuring:
    - URLs are not visited more than once
    - URLs beyond the configured max depth are rejected
    - FIFO ordering for breadth-first crawling
    """

    def __init__(self, max_depth: int) -> None:
        """Initialize the crawl queue.

        Args:
            max_depth: Maximum allowed depth (Profundidad_Navegacion).
        """
        self._max_depth = max_depth
        self._queue: deque[CrawlItem] = deque()
        self._visited: set[str] = set()
        self._enqueued: set[str] = set()

    @property
    def max_depth(self) -> int:
        """Return the configured maximum depth."""
        return self._max_depth

    @property
    def visited(self) -> set[str]:
        """Return the set of visited URLs."""
        return self._visited

    @property
    def size(self) -> int:
        """Return the number of items currently in the queue."""
        return len(self._queue)

    @property
    def is_empty(self) -> bool:
        """Return True if the queue has no more items to process."""
        return len(self._queue) == 0

    def add(self, url: str, depth: int) -> bool:
        """Add a URL to the crawl queue if not visited and within depth limit.

        Args:
            url: The URL to add.
            depth: The depth level of this URL.

        Returns:
            True if the URL was added, False if rejected (already visited,
            already enqueued, or exceeds max depth).
        """
        # Reject if depth exceeds maximum
        if depth > self._max_depth:
            logger.debug(
                "URL rejected: exceeds max depth",
                url=url,
                depth=depth,
                max_depth=self._max_depth,
            )
            return False

        # Reject if already visited
        if url in self._visited:
            logger.debug(
                "URL rejected: already visited",
                url=url,
            )
            return False

        # Reject if already in queue
        if url in self._enqueued:
            logger.debug(
                "URL rejected: already enqueued",
                url=url,
            )
            return False

        # Add to queue
        self._queue.append(CrawlItem(url=url, depth=depth))
        self._enqueued.add(url)
        return True

    def next(self) -> Optional[CrawlItem]:
        """Return the next URL to process, or None if queue is empty.

        Marks the URL as visited when dequeued.

        Returns:
            The next CrawlItem to process, or None if the queue is empty.
        """
        if not self._queue:
            return None

        item = self._queue.popleft()
        self._visited.add(item.url)
        self._enqueued.discard(item.url)
        return item

    def mark_visited(self, url: str) -> None:
        """Manually mark a URL as visited without processing it.

        Useful for marking the seed URL or URLs that failed.

        Args:
            url: The URL to mark as visited.
        """
        self._visited.add(url)
