"""Data extraction using Mapa_Selectores for 66-field Esquema_Inmueble.

Extracts property data from pages using configured CSS selectors.
For each field, tries selectors in priority order (first non-empty match wins).
Fields not found are set to null (not omitted).
"""

from __future__ import annotations

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
    """

    async def extract(
        self,
        page: Any,
        selector_map: dict[str, list[str]],
    ) -> dict[str, Any]:
        """Extract all 66 fields from a page using the selector map.

        Args:
            page: A Playwright Page object (or compatible mock).
            selector_map: Dictionary mapping field names to lists of CSS selectors.
                         Each field has one or more selectors tried in order.

        Returns:
            Dictionary with exactly 66 keys matching ESQUEMA_INMUEBLE_FIELDS.
            Fields not found are set to None.
        """
        result: dict[str, Any] = {}

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

        Args:
            page: A Playwright Page object.
            field_name: Name of the field being extracted.
            selectors: List of CSS selectors to try in priority order.

        Returns:
            The text content of the first matching selector, or None if
            no selector returns a non-empty value.
        """
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element is not None:
                    text = await element.text_content()
                    if text is not None and text.strip():
                        return text.strip()
            except Exception as e:
                logger.debug(
                    "Selector extraction failed",
                    field_name=field_name,
                    selector=selector,
                    error=str(e),
                )
                continue

        return None

    def extract_sync(
        self,
        page_data: dict[str, str],
        selector_map: dict[str, list[str]],
    ) -> dict[str, Any]:
        """Synchronous extraction for testing without a real browser.

        Uses a dictionary of selector->value mappings instead of a real page.

        Args:
            page_data: Dictionary mapping CSS selectors to their text values.
            selector_map: Dictionary mapping field names to lists of CSS selectors.

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
                value = page_data.get(selector)
                if value is not None and value.strip():
                    result[field_name] = value.strip()
                    break  # First match wins

        return result
