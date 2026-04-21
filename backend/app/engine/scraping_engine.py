"""ScrapingEngine orchestrator with fail-safe error handling.

Orchestrates the full scraping process:
1. Load selector map for the sitio_origen
2. Initialize browser with stealth config
3. Process URLs from crawl queue
4. Extract data from detail pages
5. Handle errors gracefully (log, skip, continue)
6. Publish progress via Redis Pub/Sub
7. Rotate sessions every 50 requests

Fail-safe: errors on individual URLs don't stop execution.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Optional

import structlog

from app.engine.backoff import ExponentialBackoff
from app.engine.browser_manager import BrowserManager
from app.engine.captcha_detector import CaptchaDetector
from app.engine.crawl_queue import CrawlQueue
from app.engine.data_extractor import DataExtractor
from app.engine.progress_publisher import ProgressPublisher
from app.engine.stealth_config import StealthConfig

logger = structlog.get_logger(__name__)


@dataclass
class ExecutionResult:
    """Result of a scraping engine execution."""

    task_id: str
    pages_processed: int = 0
    records_extracted: int = 0
    errors: list[dict[str, Any]] = field(default_factory=list)
    status: str = "success"


class ScrapingEngine:
    """Main orchestrator for the scraping process.

    Coordinates all engine components to execute a scraping task:
    - BrowserManager for browser lifecycle
    - CrawlQueue for URL management
    - DataExtractor for field extraction
    - CaptchaDetector for CAPTCHA detection
    - ExponentialBackoff for 429 handling
    - ProgressPublisher for real-time updates

    Fail-safe: errors on individual URLs are logged and skipped,
    never halting the entire execution.
    """

    def __init__(
        self,
        stealth_config: Optional[StealthConfig] = None,
        progress_publisher: Optional[ProgressPublisher] = None,
    ) -> None:
        """Initialize the scraping engine.

        Args:
            stealth_config: Stealth configuration. Uses defaults if not provided.
            progress_publisher: Progress publisher for Redis Pub/Sub.
        """
        self._stealth_config = stealth_config or StealthConfig()
        self._browser_manager = BrowserManager(self._stealth_config)
        self._data_extractor = DataExtractor()
        self._captcha_detector = CaptchaDetector()
        self._backoff = ExponentialBackoff(
            base=self._stealth_config.backoff_initial,
            max_delay=self._stealth_config.backoff_max,
        )
        self._progress_publisher = progress_publisher or ProgressPublisher()

    async def execute(
        self,
        task_id: str,
        base_url: str,
        max_depth: int,
        selector_map: dict[str, list[str]],
        sitio_origen: str,
        correlation_id: str,
        playwright: Optional[Any] = None,
    ) -> ExecutionResult:
        """Execute a complete scraping task.

        Orchestrates the full scraping process with fail-safe error handling.
        Errors on individual URLs are logged and skipped.

        Args:
            task_id: Unique task identifier.
            base_url: The starting URL to crawl.
            max_depth: Maximum crawl depth (Profundidad_Navegacion).
            selector_map: CSS selector mappings for field extraction.
            sitio_origen: The site origin identifier.
            correlation_id: Correlation ID for traceability.
            playwright: Optional Playwright instance (for testing).

        Returns:
            ExecutionResult with counts and status.
        """
        result = ExecutionResult(task_id=task_id)

        logger.info(
            "Scraping engine started",
            task_id=task_id,
            base_url=base_url,
            max_depth=max_depth,
            sitio_origen=sitio_origen,
            correlation_id=correlation_id,
        )

        # Initialize crawl queue with seed URL
        crawl_queue = CrawlQueue(max_depth=max_depth)
        crawl_queue.add(base_url, depth=0)

        try:
            # Launch browser if playwright instance provided
            if playwright is not None:
                await self._browser_manager.launch(playwright)

            # Process URLs from the queue
            while not crawl_queue.is_empty:
                item = crawl_queue.next()
                if item is None:
                    break

                try:
                    await self._process_url(
                        item.url,
                        item.depth,
                        crawl_queue,
                        selector_map,
                        sitio_origen,
                        result,
                        correlation_id,
                    )
                except Exception as e:
                    # Fail-safe: log error, skip URL, continue
                    error_info = {
                        "url": item.url,
                        "depth": item.depth,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    }
                    result.errors.append(error_info)

                    logger.error(
                        "Error processing URL, skipping",
                        url=item.url,
                        error=str(e),
                        error_type=type(e).__name__,
                        correlation_id=correlation_id,
                    )

                result.pages_processed += 1

                # Publish progress
                await self._progress_publisher.publish_progress(
                    task_id=task_id,
                    pages_processed=result.pages_processed,
                    records_extracted=result.records_extracted,
                )

                # Check if session rotation is needed
                if self._browser_manager.should_rotate():
                    await self._browser_manager.rotate_session()

                # Apply random delay between requests
                delay = self._stealth_config.get_random_delay()
                await asyncio.sleep(delay)

        except Exception as e:
            # Critical error that stops execution
            logger.error(
                "Critical engine error",
                task_id=task_id,
                error=str(e),
                correlation_id=correlation_id,
            )
            result.status = "failure"
            result.errors.append({
                "url": None,
                "error": str(e),
                "error_type": "CriticalError",
            })
        finally:
            # Always close the browser
            await self._browser_manager.close()

        # Determine final status
        if result.status != "failure":
            if result.errors:
                result.status = "partial_success"
            else:
                result.status = "success"

        # Publish completion
        await self._progress_publisher.publish_completion(
            task_id=task_id,
            status=result.status,
            pages_processed=result.pages_processed,
            records_extracted=result.records_extracted,
        )

        logger.info(
            "Scraping engine completed",
            task_id=task_id,
            status=result.status,
            pages_processed=result.pages_processed,
            records_extracted=result.records_extracted,
            errors_count=len(result.errors),
            correlation_id=correlation_id,
        )

        return result

    async def _process_url(
        self,
        url: str,
        depth: int,
        crawl_queue: CrawlQueue,
        selector_map: dict[str, list[str]],
        sitio_origen: str,
        result: ExecutionResult,
        correlation_id: str,
    ) -> None:
        """Process a single URL (navigate, detect CAPTCHA, extract data).

        Args:
            url: The URL to process.
            depth: Current depth level.
            crawl_queue: The crawl queue for adding discovered links.
            selector_map: CSS selector mappings.
            sitio_origen: Site origin identifier.
            result: Execution result to update.
            correlation_id: Correlation ID for traceability.
        """
        # Navigate to the URL
        response = await self._browser_manager.navigate(url)

        # Check for HTTP 429
        if response is not None and hasattr(response, "status"):
            if response.status == 429:
                delay = self._backoff.record_429()
                logger.warning(
                    "HTTP 429 received, applying backoff",
                    url=url,
                    delay_seconds=delay,
                    correlation_id=correlation_id,
                )
                await asyncio.sleep(delay)
                # Retry once after backoff
                response = await self._browser_manager.navigate(url)
            else:
                self._backoff.reset()

        # Get the page
        page = await self._browser_manager.get_page()

        # Check for CAPTCHA
        captcha_detected = await self._captcha_detector.detect(page)
        if captcha_detected:
            result.errors.append({
                "url": url,
                "error": "CAPTCHA detected",
                "error_type": "CAPTCHA",
            })
            logger.warning(
                "CAPTCHA detected, skipping page",
                url=url,
                correlation_id=correlation_id,
            )
            return

        # Extract data from the page
        extracted = await self._data_extractor.extract(page, selector_map)

        # Check if this is a detail page (has Codigo_Inmueble)
        if extracted.get("Codigo_Inmueble") is not None:
            result.records_extracted += 1

        # Discover links for further crawling (if not at max depth)
        if depth < crawl_queue.max_depth:
            await self._discover_links(page, url, depth, crawl_queue)

    async def _discover_links(
        self,
        page: Any,
        current_url: str,
        current_depth: int,
        crawl_queue: CrawlQueue,
    ) -> None:
        """Discover internal links on the page and add to crawl queue.

        Args:
            page: The current Playwright page.
            current_url: The current page URL.
            current_depth: The current depth level.
            crawl_queue: The crawl queue to add discovered links to.
        """
        try:
            links = await page.query_selector_all("a[href]")
            for link in links:
                href = await link.get_attribute("href")
                if href and self._is_internal_link(href, current_url):
                    crawl_queue.add(href, current_depth + 1)
        except Exception as e:
            logger.debug(
                "Link discovery failed",
                url=current_url,
                error=str(e),
            )

    @staticmethod
    def _is_internal_link(href: str, base_url: str) -> bool:
        """Check if a link is internal to the same domain.

        Args:
            href: The href attribute value.
            base_url: The base URL to compare against.

        Returns:
            True if the link is internal.
        """
        from urllib.parse import urlparse

        if not href or href.startswith("#") or href.startswith("javascript:"):
            return False

        try:
            base_parsed = urlparse(base_url)
            href_parsed = urlparse(href)

            # Relative URLs are internal
            if not href_parsed.netloc:
                return True

            # Same domain
            return href_parsed.netloc == base_parsed.netloc
        except Exception:
            return False
