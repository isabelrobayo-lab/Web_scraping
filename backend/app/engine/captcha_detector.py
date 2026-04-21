"""CAPTCHA detection heuristics and skip-with-log behavior.

Detects CAPTCHA challenges on pages using heuristics:
- reCAPTCHA iframes
- hCaptcha elements
- Elements with class/id containing "captcha"

On detection: logs as CAPTCHA error, skips page, continues with next URL.
"""

from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# CSS selectors for CAPTCHA detection heuristics
CAPTCHA_SELECTORS: list[str] = [
    # reCAPTCHA iframes
    'iframe[src*="recaptcha"]',
    'iframe[src*="google.com/recaptcha"]',
    # hCaptcha elements
    'iframe[src*="hcaptcha"]',
    ".h-captcha",
    "#h-captcha",
    # Generic captcha class/id patterns
    '[class*="captcha"]',
    '[id*="captcha"]',
    '[class*="CAPTCHA"]',
    '[id*="CAPTCHA"]',
    # reCAPTCHA specific elements
    ".g-recaptcha",
    "#g-recaptcha",
    ".recaptcha",
    # Cloudflare challenge
    '[class*="cf-challenge"]',
    "#challenge-form",
]


class CaptchaDetector:
    """Detects CAPTCHA challenges on web pages.

    Uses heuristic-based detection by checking for known CAPTCHA
    element patterns (reCAPTCHA, hCaptcha, generic captcha elements).
    """

    def __init__(self, selectors: list[str] | None = None) -> None:
        """Initialize the CAPTCHA detector.

        Args:
            selectors: Custom list of CSS selectors to check.
                      Defaults to CAPTCHA_SELECTORS if not provided.
        """
        self._selectors = selectors or CAPTCHA_SELECTORS

    async def detect(self, page: Any) -> bool:
        """Check if the current page contains a CAPTCHA challenge.

        Args:
            page: A Playwright Page object (or compatible mock).

        Returns:
            True if a CAPTCHA is detected, False otherwise.
        """
        for selector in self._selectors:
            try:
                element = await page.query_selector(selector)
                if element is not None:
                    logger.warning(
                        "CAPTCHA detected on page",
                        selector=selector,
                    )
                    return True
            except Exception as e:
                logger.debug(
                    "CAPTCHA detection selector failed",
                    selector=selector,
                    error=str(e),
                )
                continue

        return False

    def detect_sync(self, page_selectors: set[str]) -> bool:
        """Synchronous CAPTCHA detection for testing.

        Checks if any of the CAPTCHA selectors are present in the
        provided set of page selectors.

        Args:
            page_selectors: Set of CSS selectors present on the page.

        Returns:
            True if a CAPTCHA is detected, False otherwise.
        """
        for selector in self._selectors:
            if selector in page_selectors:
                logger.warning(
                    "CAPTCHA detected on page",
                    selector=selector,
                )
                return True
        return False
