"""Data extraction using Mapa_Selectores for 66-field Esquema_Inmueble.

Extracts property data from pages using configured CSS selectors.
For each field, tries selectors in priority order (first non-empty match wins).
Fields not found are set to null (not omitted).

Selector types supported:
- Plain CSS selector (default): query_selector + text_content
- "label:..." : Search technical sheet for label-value pair
- "amenity:..." : Search amenities list for matching text (returns "Si"/"No")
- "url_regex:..." : Extract from page URL using regex
- "meta:..." : Extract content attribute from meta tag by property
- "fixed:..." : Return a fixed/hardcoded value
"""

from __future__ import annotations

import re
from typing import Any, Optional, Protocol

import structlog

logger = structlog.get_logger(__name__)

# The 66 fields of Esquema_Inmueble as defined in the Diccionario de Datos
ESQUEMA_INMUEBLE_FIELDS: list[str] = [
    "Id_Interno",
    "Codigo_Inmueble",
    "Tipo_Inmueble",
    "Habitaciones",
    "Banos",
    "Operacion",
    "Estacionamiento",
    "Administracion_Valor",
    "Antiguedad_Detalle",
    "Rango_Antiguedad",
    "Tipo_Estudio",
    "Es_Loft",
    "Dueno_Anuncio",
    "Telefono_Principal",
    "Telefono_Opcional",
    "Correo_Contacto",
    "Tipo_Publicador",
    "Descripcion_Anuncio",
    "Fecha_Control",
    "Fecha_Actualizacion",
    "Municipio",
    "Amoblado",
    "Titulo_Anuncio",
    "Metros_Utiles",
    "Metros_Totales",
    "Orientacion",
    "Latitud",
    "Longitud",
    "Url_Anuncio",
    "Url_Imagen_Principal",
    "Sector",
    "Barrio",
    "Estrato",
    "Sitio_Origen",
    "Fecha_Publicacion",
    "Direccion",
    "Estado_Activo",
    "Fecha_Desactivacion",
    "Precio_USD",
    "Precio_Local",
    "Simbolo_Moneda",
    "Piso_Propiedad",
    "Tiene_Ascensores",
    "Tiene_Balcones",
    "Tiene_Seguridad",
    "Tiene_Bodega_Deposito",
    "Tiene_Terraza",
    "Cuarto_Servicio",
    "Bano_Servicio",
    "Tiene_Calefaccion",
    "Tiene_Alarma",
    "Acceso_Controlado",
    "Circuito_Cerrado",
    "Estacionamiento_Visita",
    "Cocina_Americana",
    "Tiene_Gimnasio",
    "Tiene_BBQ",
    "Tiene_Piscina",
    "En_Conjunto_Residencial",
    "Uso_Comercial",
    "Cambio_Precio_Valor",
    "Precio_Bajo",
    "Tipo_Empresa",
    "Glosa_Administracion",
    "Area_Privada",
    "Area_Construida",
]


class PageLike(Protocol):
    """Protocol for page objects that support query_selector and text_content."""

    async def query_selector(self, selector: str) -> Optional[Any]:
        """Query a single element by CSS selector."""
        ...


class ElementLike(Protocol):
    """Protocol for element objects that support text_content."""

    async def text_content(self) -> Optional[str]:
        """Get the text content of the element."""
        ...


class DataExtractor:
    """Extracts 66 fields from a page using Mapa_Selectores.

    For each field in the selector map, tries selectors in order.
    The first selector that returns a non-empty value wins (priority order).
    Fields not found on the page are set to null.

    Supports extended selector prefixes for sites that require
    non-standard extraction (e.g. label-value tables, amenity lists):
    - No prefix or "css:" → standard CSS selector + text_content
    - "label:..." → search technical sheet rows for a label match
    - "amenity:..." → search amenity list for matching text
    - "url_regex:..." → extract from the current page URL via regex
    - "meta:..." → extract content attribute from <meta property="...">
    - "fixed:..." → return a literal fixed value
    """

    # Sentinel value used by some sites to indicate missing data
    PLACEHOLDER_VALUES: set[str] = frozenset({
        "Preguntale!",
        "Pregúntale!",
        "No disponible",
        "N/A",
    })

    # ---- Technical sheet cache (populated once per page) ----
    _tech_sheet_cache: dict[str, str] | None = None
    # ---- Amenities cache (populated once per page) ----
    _amenities_cache: list[str] | None = None

    async def extract(
        self,
        page: Any,
        selector_map: dict[str, list[str]],
    ) -> dict[str, Any]:
        """Extract all 66 fields from a page using the selector map.

        Args:
            page: A Playwright Page object (or compatible mock).
            selector_map: Dictionary mapping field names to lists of selectors.
                         Each field has one or more selectors tried in order.

        Returns:
            Dictionary with exactly 66 keys matching ESQUEMA_INMUEBLE_FIELDS.
            Fields not found are set to None.
        """
        result: dict[str, Any] = {}

        # Reset per-page caches
        self._tech_sheet_cache = None
        self._amenities_cache = None

        # Initialize all 66 fields to None
        for field_name in ESQUEMA_INMUEBLE_FIELDS:
            result[field_name] = None

        # Extract each field using selector map
        for field_name, selectors in selector_map.items():
            if field_name not in result:
                # Skip fields not in the schema
                logger.debug(
                    "Selector map field not in schema, skipping",
                    field_name=field_name,
                )
                continue

            value = await self._extract_field(page, field_name, selectors)
            result[field_name] = value

        return result

    async def _extract_field(
        self,
        page: Any,
        field_name: str,
        selectors: list[str],
    ) -> Optional[str]:
        """Try each selector in order and return the first non-empty match.

        Supports extended selector prefixes:
        - "label:..." -> technical sheet label-value lookup
        - "amenity:..." -> amenity list text search
        - "url_regex:..." -> regex extraction from page URL
        - "meta:..." -> meta tag content attribute
        - "fixed:..." -> literal fixed value

        Args:
            page: A Playwright Page object.
            field_name: Name of the field being extracted.
            selectors: List of selectors to try in priority order.

        Returns:
            The extracted value, or None if no selector matches.
        """
        for selector in selectors:
            try:
                value = await self._resolve_selector(page, selector)
                if value is not None:
                    cleaned = value.strip()
                    if cleaned and cleaned not in self.PLACEHOLDER_VALUES:
                        return cleaned
            except Exception as e:
                logger.debug(
                    "Selector extraction failed",
                    field_name=field_name,
                    selector=selector,
                    error=str(e),
                )
                continue

        return None

    async def _resolve_selector(
        self,
        page: Any,
        selector: str,
    ) -> Optional[str]:
        """Resolve a single selector string, dispatching by prefix.

        Args:
            page: A Playwright Page object.
            selector: Selector string, optionally prefixed.

        Returns:
            Extracted text value, or None.
        """
        if selector.startswith("fixed:"):
            return selector[6:]

        if selector.startswith("url_regex:"):
            return await self._extract_from_url(page, selector[10:])

        if selector.startswith("meta:"):
            return await self._extract_meta(page, selector[5:])

        if selector.startswith("label:"):
            return await self._extract_label(page, selector[6:])

        if selector.startswith("amenity:"):
            return await self._extract_amenity(page, selector[8:])

        # Strip optional "css:" prefix for explicit CSS selectors
        css_selector = selector[4:] if selector.startswith("css:") else selector

        return await self._extract_css(page, css_selector)

    async def _extract_css(
        self,
        page: Any,
        selector: str,
    ) -> Optional[str]:
        """Extract text content using a standard CSS selector."""
        element = await page.query_selector(selector)
        if element is not None:
            text = await element.text_content()
            if text is not None and text.strip():
                return text.strip()
        return None

    async def _extract_from_url(
        self,
        page: Any,
        pattern: str,
    ) -> Optional[str]:
        """Extract a value from the current page URL using a regex pattern."""
        try:
            url = page.url if isinstance(page.url, str) else str(page.url)
            match = re.search(pattern, url)
            if match:
                return match.group(1) if match.lastindex else match.group(0)
        except Exception as e:
            logger.debug("URL regex extraction failed", pattern=pattern, error=str(e))
        return None

    async def _extract_meta(
        self,
        page: Any,
        property_name: str,
    ) -> Optional[str]:
        """Extract the content attribute from a <meta property="..."> tag."""
        selector = f'meta[property="{property_name}"]'
        element = await page.query_selector(selector)
        if element is not None:
            content = await element.get_attribute("content")
            if content is not None and content.strip():
                return content.strip()
        return None

    async def _extract_label(
        self,
        page: Any,
        label_text: str,
    ) -> Optional[str]:
        """Extract a value from a technical sheet (label-value rows).

        Searches for rows in .technical-sheet with Ant Design layout:
        .ant-row > .ant-col (label) + .ant-col (dots) + .ant-col (value)

        Results are cached per page to avoid repeated DOM queries.
        """
        if self._tech_sheet_cache is None:
            self._tech_sheet_cache = await self._build_tech_sheet_cache(page)

        # Case-insensitive lookup, stripping leading asterisks and whitespace
        normalized_label = label_text.strip().lower()
        return self._tech_sheet_cache.get(normalized_label)

    async def _build_tech_sheet_cache(self, page: Any) -> dict[str, str]:
        """Build a cache of label->value pairs from the technical sheet."""
        cache: dict[str, str] = {}
        try:
            rows = await page.query_selector_all(
                ".technical-sheet .ant-row.ant-row-space-between"
            )
            for row in rows:
                cols = await row.query_selector_all(":scope > .ant-col")
                if len(cols) >= 3:
                    label_el = cols[0]
                    value_el = cols[-1]
                    label = await label_el.text_content()
                    value = await value_el.text_content()
                    if label and value:
                        # Normalize: strip leading "* ", lowercase
                        clean_label = label.strip().lstrip("* ").lower()
                        clean_value = value.strip()
                        if (
                            clean_value
                            and clean_value not in self.PLACEHOLDER_VALUES
                        ):
                            cache[clean_label] = clean_value
        except Exception as e:
            logger.debug("Technical sheet extraction failed", error=str(e))
        return cache

    async def _extract_amenity(
        self,
        page: Any,
        amenity_text: str,
    ) -> Optional[str]:
        """Check if an amenity exists in the amenities list.

        Searches .CO-facility-batch .ant-typography elements for matching text.
        Returns "Si" if found, None if not found.

        Results are cached per page to avoid repeated DOM queries.
        """
        if self._amenities_cache is None:
            self._amenities_cache = await self._build_amenities_cache(page)

        normalized = amenity_text.strip().lower()
        for amenity in self._amenities_cache:
            if normalized in amenity.lower():
                return "Si"
        return None

    async def _build_amenities_cache(self, page: Any) -> list[str]:
        """Build a cache of amenity names from the facilities section."""
        amenities: list[str] = []
        try:
            elements = await page.query_selector_all(
                ".CO-facility-batch .ant-typography"
            )
            for el in elements:
                text = await el.text_content()
                if text and text.strip() and text.strip() != "*":
                    amenities.append(text.strip())
        except Exception as e:
            logger.debug("Amenities extraction failed", error=str(e))
        return amenities

    def extract_sync(
        self,
        page_data: dict[str, str],
        selector_map: dict[str, list[str]],
        page_url: str = "",
    ) -> dict[str, Any]:
        """Synchronous extraction for testing without a real browser.

        Uses a dictionary of selector->value mappings instead of a real page.
        Supports extended selector prefixes (fixed:, url_regex:, meta:,
        label:, amenity:) in addition to plain CSS selectors.

        Args:
            page_data: Dictionary mapping selectors to their text values.
                       For label: selectors, use "label:<Label Text>" as key.
                       For amenity: selectors, use "amenity:<Amenity Name>".
                       For meta: selectors, use "meta:<property>".
            selector_map: Dictionary mapping field names to lists of selectors.
            page_url: Simulated page URL for url_regex: selectors.

        Returns:
            Dictionary with exactly 66 keys matching ESQUEMA_INMUEBLE_FIELDS.
        """
        result: dict[str, Any] = {}

        # Initialize all 66 fields to None
        for field_name in ESQUEMA_INMUEBLE_FIELDS:
            result[field_name] = None

        # Extract each field using selector map
        for field_name, selectors in selector_map.items():
            if field_name not in result:
                continue

            for selector in selectors:
                value: str | None = None

                if selector.startswith("fixed:"):
                    value = selector[6:]
                elif selector.startswith("url_regex:"):
                    pattern = selector[10:]
                    match = re.search(pattern, page_url)
                    if match:
                        value = (
                            match.group(1) if match.lastindex else match.group(0)
                        )
                elif selector.startswith("amenity:"):
                    # Look up in page_data with the full prefixed key
                    value = page_data.get(selector)
                elif selector.startswith("label:"):
                    # Look up in page_data with the full prefixed key
                    value = page_data.get(selector)
                elif selector.startswith("meta:"):
                    value = page_data.get(selector)
                else:
                    # Plain CSS selector or "css:" prefixed
                    css_sel = (
                        selector[4:] if selector.startswith("css:") else selector
                    )
                    value = page_data.get(css_sel)

                if value is not None and value.strip():
                    cleaned = value.strip()
                    if cleaned not in self.PLACEHOLDER_VALUES:
                        result[field_name] = cleaned
                        break  # First match wins

        return result
