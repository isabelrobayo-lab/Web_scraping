"""Automatic CSS selector validation against a live URL.

When a new URL is added to a configuration, this service validates
that the configured CSS selectors for the corresponding sitio_origen
can actually find elements on the target page.

Uses Playwright in headless mode with stealth config to render the page
and test each selector in the map.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class SelectorValidationResult:
    """Result of validating selectors against a URL."""

    url: str
    sitio_origen: str
    total_fields: int = 0
    fields_found: int = 0
    fields_missing: int = 0
    field_results: dict[str, dict[str, Any]] = field(default_factory=dict)
    is_valid: bool = False
    error: str | None = None


class SelectorValidator:
    """Validates CSS selector maps against live URLs.

    Navigates to a URL using Playwright and tests each selector
    in the map to verify it can find elements on the page.
    """

    async def validate(
        self,
        url: str,
        selector_map: dict[str, list[str]],
        sitio_origen: str,
    ) -> SelectorValidationResult:
        """Validate a selector map against a live URL.

        Args:
            url: The URL to test selectors against.
            selector_map: Dictionary mapping field names to lists of selectors.
            sitio_origen: The site origin identifier.

        Returns:
            SelectorValidationResult with per-field results.
        """
        result = SelectorValidationResult(
            url=url,
            sitio_origen=sitio_origen,
            total_fields=len(selector_map),
        )

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as pw:
                browser = await pw.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                    ],
                )
                context = await browser.new_context(
                    viewport={"width": 1366, "height": 768},
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                )
                page = await context.new_page()

                try:
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                except Exception as nav_err:
                    result.error = f"Navigation failed: {nav_err}"
                    await browser.close()
                    return result

                # Test each field's selectors
                for field_name, selectors in selector_map.items():
                    field_result = await self._test_field(
                        page, field_name, selectors, url
                    )
                    result.field_results[field_name] = field_result

                    if field_result["found"]:
                        result.fields_found += 1
                    else:
                        result.fields_missing += 1

                await browser.close()

        except Exception as e:
            result.error = f"Validation error: {e}"
            logger.error(
                "Selector validation failed",
                url=url,
                error=str(e),
            )
            return result

        # Consider valid if at least 30% of fields are found
        # (some fields may legitimately not be on every page)
        if result.total_fields > 0:
            ratio = result.fields_found / result.total_fields
            result.is_valid = ratio >= 0.3

        logger.info(
            "Selector validation completed",
            url=url,
            sitio_origen=sitio_origen,
            total_fields=result.total_fields,
            fields_found=result.fields_found,
            fields_missing=result.fields_missing,
            is_valid=result.is_valid,
        )

        return result

    async def _test_field(
        self,
        page: Any,
        field_name: str,
        selectors: list[str],
        page_url: str,
    ) -> dict[str, Any]:
        """Test selectors for a single field against the page.

        Args:
            page: Playwright page object.
            field_name: Name of the field being tested.
            selectors: List of selectors to try.
            page_url: Current page URL (for url_regex selectors).

        Returns:
            Dictionary with test results for this field.
        """
        import re

        for selector in selectors:
            try:
                # Handle special selector prefixes
                if selector.startswith("fixed:"):
                    return {
                        "found": True,
                        "selector": selector,
                        "value": selector[6:],
                        "type": "fixed",
                    }

                if selector.startswith("url_regex:"):
                    pattern = selector[10:]
                    match = re.search(pattern, page_url)
                    if match:
                        value = match.group(1) if match.lastindex else match.group(0)
                        return {
                            "found": True,
                            "selector": selector,
                            "value": value,
                            "type": "url_regex",
                        }
                    continue

                if selector.startswith("meta:"):
                    prop = selector[5:]
                    el = await page.query_selector(
                        f'meta[property="{prop}"]'
                    )
                    if el:
                        content = await el.get_attribute("content")
                        if content and content.strip():
                            return {
                                "found": True,
                                "selector": selector,
                                "value": content.strip()[:100],
                                "type": "meta",
                            }
                    continue

                if selector.startswith("label:"):
                    # Test label extraction from technical sheet
                    label = selector[6:]
                    rows = await page.query_selector_all(
                        ".technical-sheet .ant-row"
                    )
                    for row in rows:
                        text = await row.text_content()
                        if text and label.lower() in text.lower():
                            return {
                                "found": True,
                                "selector": selector,
                                "value": f"(label match: {label})",
                                "type": "label",
                            }
                    continue

                if selector.startswith("amenity:"):
                    amenity = selector[8:]
                    elements = await page.query_selector_all(
                        ".CO-facility-batch .ant-typography"
                    )
                    for el in elements:
                        text = await el.text_content()
                        if text and amenity.lower() in text.lower():
                            return {
                                "found": True,
                                "selector": selector,
                                "value": "Si",
                                "type": "amenity",
                            }
                    continue

                # Standard CSS selector
                css = selector[4:] if selector.startswith("css:") else selector
                el = await page.query_selector(css)
                if el:
                    text = await el.text_content()
                    if text and text.strip():
                        return {
                            "found": True,
                            "selector": selector,
                            "value": text.strip()[:100],
                            "type": "css",
                        }

            except Exception as e:
                logger.debug(
                    "Selector test failed",
                    field_name=field_name,
                    selector=selector,
                    error=str(e),
                )
                continue

        return {
            "found": False,
            "selector": None,
            "value": None,
            "type": None,
            "tried_selectors": selectors,
        }
