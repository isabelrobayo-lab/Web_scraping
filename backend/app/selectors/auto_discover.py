"""Auto-discovery of CSS selectors for a given URL.

Navigates to a URL using Playwright, analyzes the HTML structure,
and generates a selector map for the 66-field Esquema_Inmueble.

This runs as a Celery task so it doesn't block the API.
"""

from __future__ import annotations

import re
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# Common CSS patterns found in real estate sites for each field
_DISCOVERY_RULES: list[dict[str, Any]] = [
    {"field": "Codigo_Inmueble", "strategies": [
        {"type": "url_regex", "pattern": r"/(\d{5,})$"},
        {"type": "url_regex", "pattern": r"id[=/-](\d+)"},
        {"type": "css", "selectors": [".property-code", ".listing-id", "[data-id]"]},
    ]},
    {"field": "Titulo_Anuncio", "strategies": [
        {"type": "css", "selectors": [
            "h1.property-title", "h1.listing-title", "h1.detail-title",
            ".property-header h1", ".listing-header h1", "h1",
        ]},
    ]},
    {"field": "Precio_Local", "strategies": [
        {"type": "css", "selectors": [
            ".property-price", ".price-tag", ".main-price",
            ".listing-price", "[class*='price']", "[data-price]",
        ]},
    ]},
    {"field": "Habitaciones", "strategies": [
        {"type": "css", "selectors": [
            "[class*='bedroom']", "[class*='habitacion']",
            ".typology-item-container:nth-child(1)",
        ]},
        {"type": "label", "labels": ["Habitaciones", "Alcobas", "Bedrooms"]},
    ]},
    {"field": "Banos", "strategies": [
        {"type": "css", "selectors": [
            "[class*='bathroom']", "[class*='bano']",
            ".typology-item-container:nth-child(2)",
        ]},
        {"type": "label", "labels": ["Baños", "Banos", "Bathrooms"]},
    ]},
    {"field": "Metros_Totales", "strategies": [
        {"type": "css", "selectors": [
            "[class*='area']", "[class*='metro']",
            ".typology-item-container:nth-child(3)",
        ]},
        {"type": "label", "labels": ["Área", "Area", "m²", "Metros"]},
    ]},
    {"field": "Municipio", "strategies": [
        {"type": "css", "selectors": [
            ".property-location", ".location-tag", "[class*='location']",
            "[class*='city']",
        ]},
    ]},
    {"field": "Barrio", "strategies": [
        {"type": "css", "selectors": ["[class*='neighborhood']", "[class*='barrio']"]},
        {"type": "label", "labels": ["Barrio", "Sector", "Zona"]},
    ]},
    {"field": "Descripcion_Anuncio", "strategies": [
        {"type": "css", "selectors": [
            ".property-description", ".listing-description",
            "[class*='description']", "[class*='descripcion']",
        ]},
    ]},
    {"field": "Dueno_Anuncio", "strategies": [
        {"type": "css", "selectors": [
            ".owner-name", "[class*='agent']", "[class*='owner']",
        ]},
    ]},
    {"field": "Url_Imagen_Principal", "strategies": [
        {"type": "meta", "properties": ["og:image"]},
    ]},
    {"field": "Url_Anuncio", "strategies": [
        {"type": "meta", "properties": ["og:url"]},
    ]},
    {"field": "Estacionamiento", "strategies": [
        {"type": "label", "labels": ["Parqueaderos", "Garajes", "Parking", "Estacionamiento"]},
    ]},
    {"field": "Estrato", "strategies": [
        {"type": "label", "labels": ["Estrato"]},
    ]},
    {"field": "Antiguedad_Detalle", "strategies": [
        {"type": "label", "labels": ["Antigüedad", "Antiguedad"]},
    ]},
    {"field": "Piso_Propiedad", "strategies": [
        {"type": "label", "labels": ["Piso", "Floor"]},
    ]},
    {"field": "Administracion_Valor", "strategies": [
        {"type": "css", "selectors": ["[class*='admin']", "[class*='commonExpenses']"]},
        {"type": "label", "labels": ["Administración", "Administracion"]},
    ]},
    {"field": "Area_Privada", "strategies": [
        {"type": "label", "labels": ["Área Privada", "Area Privada"]},
    ]},
    {"field": "Area_Construida", "strategies": [
        {"type": "label", "labels": ["Área Construida", "Area Construida"]},
    ]},
    {"field": "Tipo_Inmueble", "strategies": [
        {"type": "label", "labels": ["Tipo de Inmueble", "Tipo Inmueble", "Property Type"]},
    ]},
]


class SelectorAutoDiscoverer:
    """Auto-discovers CSS selectors by analyzing a live page."""

    async def discover(self, url: str, sitio_origen: str) -> dict[str, Any]:
        """Discover selectors for a URL.

        If the URL is a listing/home page, navigates to find a detail page first.
        Returns dict with status, selector_map, fields_found, total_fields.
        """
        discovered_map: dict[str, list[str]] = {}
        field_results: dict[str, dict[str, Any]] = {}
        fields_found = 0

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as pw:
                browser = await pw.chromium.launch(
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
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
                except Exception as e:
                    await browser.close()
                    return {
                        "sitio_origen": sitio_origen, "url": url,
                        "status": "error", "error": f"Navigation failed: {e}",
                        "selector_map": {}, "fields_found": 0,
                        "total_fields": len(_DISCOVERY_RULES),
                    }

                # Check if this is a detail page (has numeric ID in URL)
                import re
                if not re.search(r"/\d{5,}$", page.url):
                    # This is likely a listing/home page — find a detail page
                    detail_url = await self._find_detail_page(page, url)
                    if detail_url:
                        logger.info("Found detail page", detail_url=detail_url)
                        try:
                            await page.goto(detail_url, wait_until="networkidle", timeout=30000)
                        except Exception:
                            pass

                for rule in _DISCOVERY_RULES:
                    field_name = rule["field"]
                    selectors = await self._try_strategies(page, rule["strategies"], page.url)
                    if selectors:
                        discovered_map[field_name] = selectors
                        fields_found += 1
                        field_results[field_name] = {"found": True, "selectors": selectors}
                    else:
                        field_results[field_name] = {"found": False}

                discovered_map["Sitio_Origen"] = [f"fixed:{sitio_origen}"]
                discovered_map["Simbolo_Moneda"] = ["fixed:$"]
                await browser.close()

        except Exception as e:
            logger.error("Auto-discovery failed", url=url, error=str(e))
            return {
                "sitio_origen": sitio_origen, "url": url,
                "status": "error", "error": str(e),
                "selector_map": {}, "fields_found": 0,
                "total_fields": len(_DISCOVERY_RULES),
            }

        status = "ready" if fields_found >= 5 else "partial"
        logger.info(
            "Auto-discovery completed", url=url, sitio_origen=sitio_origen,
            fields_found=fields_found, status=status,
        )
        return {
            "sitio_origen": sitio_origen, "url": url, "status": status,
            "selector_map": discovered_map, "fields_found": fields_found,
            "total_fields": len(_DISCOVERY_RULES), "field_results": field_results,
        }

    async def _find_detail_page(self, page: Any, base_url: str) -> str | None:
        """Navigate a listing page to find a property detail URL.

        Looks for links that end in numeric IDs (typical of property detail pages).
        """
        import re
        from urllib.parse import urljoin, urlparse

        try:
            links = await page.query_selector_all("a[href]")
            for link in links:
                href = await link.get_attribute("href")
                if not href:
                    continue
                # Convert relative to absolute
                if href.startswith("/"):
                    parsed = urlparse(base_url)
                    href = f"{parsed.scheme}://{parsed.netloc}{href}"
                # Look for detail pages (URLs ending in numeric ID)
                if re.search(r"/\d{5,}$", href):
                    # Skip known non-property URLs
                    if any(skip in href for skip in ["/inmobiliarias/", "/constructoras/", "/perfil/"]):
                        continue
                    return href
            # If no numeric ID found, try links with property-like patterns
            for link in links:
                href = await link.get_attribute("href")
                if not href:
                    continue
                if href.startswith("/"):
                    parsed = urlparse(base_url)
                    href = f"{parsed.scheme}://{parsed.netloc}{href}"
                # Property detail patterns
                if re.search(r"(venta|arriendo|alquiler).+\d+", href):
                    return href
                if re.search(r"(apartamento|casa|inmueble|propiedad)", href) and re.search(r"\d+", href):
                    return href
        except Exception as e:
            logger.debug("Detail page search failed", error=str(e))

        return None

    async def _try_strategies(self, page: Any, strategies: list[dict], page_url: str) -> list[str]:
        """Try strategies for a field, return working selectors."""
        working: list[str] = []
        for strategy in strategies:
            stype = strategy["type"]
            if stype == "url_regex":
                if re.search(strategy["pattern"], page_url):
                    working.append(f"url_regex:{strategy['pattern']}")
            elif stype == "meta":
                for prop in strategy.get("properties", []):
                    el = await page.query_selector(f'meta[property="{prop}"]')
                    if el:
                        content = await el.get_attribute("content")
                        if content and content.strip():
                            working.append(f"meta:{prop}")
            elif stype == "label":
                for label in strategy.get("labels", []):
                    rows = await page.query_selector_all(
                        ".technical-sheet .ant-row, table tr, dl dt, "
                        "[class*='detail'] [class*='row'], "
                        "[class*='spec'] [class*='row']"
                    )
                    for row in rows:
                        text = await row.text_content()
                        if text and label.lower() in text.lower():
                            working.append(f"label:{label}")
                            break
            elif stype == "css":
                for sel in strategy.get("selectors", []):
                    try:
                        el = await page.query_selector(sel)
                        if el:
                            text = await el.text_content()
                            if text and text.strip():
                                working.append(sel)
                    except Exception:
                        continue
        return working
