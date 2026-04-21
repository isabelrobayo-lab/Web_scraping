"""Browser lifecycle management with Playwright stealth configuration.

Manages browser launch, context creation, and session rotation with
anti-detection settings:
- webdriver=false
- Random viewport from common resolutions
- Plugins emulation (PDF viewer, Chrome PDF)
- Session rotation every 50 requests (clear cookies, localStorage, new context)
"""

from __future__ import annotations

from typing import Any, Optional

import structlog

from app.engine.stealth_config import StealthConfig

logger = structlog.get_logger(__name__)


class BrowserManager:
    """Manages Playwright browser lifecycle with stealth configuration.

    Handles browser launch, context creation with anti-detection settings,
    and session rotation every N requests.
    """

    def __init__(self, stealth_config: Optional[StealthConfig] = None) -> None:
        """Initialize the browser manager.

        Args:
            stealth_config: Stealth configuration. Uses defaults if not provided.
        """
        self._stealth_config = stealth_config or StealthConfig()
        self._browser: Any = None
        self._context: Any = None
        self._page: Any = None
        self._request_count: int = 0

    @property
    def request_count(self) -> int:
        """Return the number of requests made in the current session."""
        return self._request_count

    @property
    def stealth_config(self) -> StealthConfig:
        """Return the stealth configuration."""
        return self._stealth_config

    async def launch(self, playwright: Any) -> None:
        """Launch the browser with stealth settings.

        Args:
            playwright: The Playwright instance (from async_playwright).
        """
        self._browser = await playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        await self._create_context()

        logger.info("Browser launched with stealth configuration")

    async def _create_context(self) -> None:
        """Create a new browser context with stealth settings."""
        if self._browser is None:
            raise RuntimeError("Browser not launched. Call launch() first.")

        viewport = self._stealth_config.get_random_viewport()
        user_agent = self._stealth_config.get_random_user_agent()

        self._context = await self._browser.new_context(
            viewport=viewport,
            user_agent=user_agent,
            java_script_enabled=True,
            ignore_https_errors=True,
        )

        # Apply stealth scripts to hide webdriver detection
        await self._context.add_init_script("""
            // Override navigator.webdriver to false
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });

            // Emulate plugins (PDF viewer, Chrome PDF)
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        name: 'Chrome PDF Plugin',
                        description: 'Portable Document Format',
                        filename: 'internal-pdf-viewer',
                        length: 1,
                    },
                    {
                        name: 'Chrome PDF Viewer',
                        description: '',
                        filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                        length: 1,
                    },
                    {
                        name: 'Native Client',
                        description: '',
                        filename: 'internal-nacl-plugin',
                        length: 2,
                    },
                ],
            });

            // Override navigator.languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['es-CO', 'es', 'en-US', 'en'],
            });

            // Override permissions query
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

        self._page = await self._context.new_page()

        logger.info(
            "Browser context created",
            viewport=viewport,
            user_agent=user_agent[:50] + "...",
        )

    async def get_page(self) -> Any:
        """Get the current page, creating one if needed.

        Returns:
            The current Playwright Page object.
        """
        if self._page is None:
            await self._create_context()
        return self._page

    async def navigate(self, url: str, timeout: int = 30000) -> Any:
        """Navigate to a URL and increment request count.

        Args:
            url: The URL to navigate to.
            timeout: Navigation timeout in milliseconds.

        Returns:
            The response from the navigation.
        """
        page = await self.get_page()
        self._request_count += 1

        response = await page.goto(url, timeout=timeout, wait_until="domcontentloaded")

        logger.debug(
            "Page navigated",
            url=url,
            request_count=self._request_count,
        )

        return response

    async def rotate_session(self) -> None:
        """Rotate the browser session.

        Closes the current context and creates a new one with fresh
        cookies, localStorage, and a new fingerprint.
        """
        if self._context is not None:
            await self._context.close()

        self._request_count = 0
        await self._create_context()

        logger.info("Browser session rotated")

    def should_rotate(self) -> bool:
        """Check if the session should be rotated based on request count."""
        return self._stealth_config.should_rotate_session(self._request_count)

    async def close(self) -> None:
        """Close the browser and all contexts."""
        if self._context is not None:
            await self._context.close()
            self._context = None
            self._page = None

        if self._browser is not None:
            await self._browser.close()
            self._browser = None

        self._request_count = 0
        logger.info("Browser closed")
