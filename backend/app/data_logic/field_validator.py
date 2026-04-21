"""Field validation and type parsing for the 66-field Esquema_Inmueble.

Implements parse_numeric, parse_boolean, parse_date, coordinate validation,
and URL validation as specified in Req 8 of the design document.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from urllib.parse import urlparse

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of validating a raw data dictionary."""

    data: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Return True if no errors occurred."""
        return len(self.errors) == 0


class FieldValidator:
    """Validation and normalization of the 66 fields per Diccionario de Datos.

    Parses numeric, boolean, and date fields from raw string values extracted
    by the scraping engine. Validates coordinate ranges and URL formats.
    """

    NUMERIC_FIELDS: list[str] = [
        "Habitaciones",
        "Baños",
        "Estacionamiento",
        "Administracion_Valor",
        "Metros_Utiles",
        "Metros_Totales",
        "Latitud",
        "Longitud",
        "Estrato",
        "Precio_USD",
        "Precio_Local",
        "Piso_Propiedad",
        "Cambio_Precio_Valor",
        "Area_Privada",
        "Area_Construida",
    ]

    BOOLEAN_FIELDS: list[str] = [
        "Tipo_Estudio",
        "Es_Loft",
        "Tiene_Ascensores",
        "Tiene_Balcones",
        "Tiene_Seguridad",
        "Tiene_Bodega_Deposito",
        "Tiene_Terraza",
        "Cuarto_Servicio",
        "Baño_Servicio",
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
        "Precio_Bajo",
    ]

    DATE_FIELDS: list[str] = [
        "Fecha_Control",
        "Fecha_Actualizacion",
        "Fecha_Publicacion",
        "Fecha_Desactivacion",
    ]

    URL_FIELDS: list[str] = [
        "Url_Anuncio",
        "Url_Imagen_Principal",
    ]

    # Patterns for parse_numeric: strip currency symbols, thousands separators
    _NUMERIC_PATTERN = re.compile(r"-?\d[\d,]*\.?\d*")

    # Recognized true/false string values for parse_boolean
    _TRUE_VALUES: set[str] = {"si", "sí", "yes", "true", "1"}
    _FALSE_VALUES: set[str] = {"no", "false", "0"}

    # Date formats to attempt in parse_date (order matters)
    _DATE_FORMATS: list[str] = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m-%d-%Y",
        "%d %b %Y",
        "%b %d, %Y",
        "%d-%m-%Y",
    ]

    def validate(self, raw_data: dict[str, Any]) -> ValidationResult:
        """Validate and normalize all fields in raw_data.

        Parses numeric, boolean, and date fields. Validates coordinates
        and URLs. Returns a ValidationResult with cleaned data, warnings,
        and errors.
        """
        result = ValidationResult()
        data = dict(raw_data)

        for field_name in self.NUMERIC_FIELDS:
            if field_name in data and data[field_name] is not None:
                value = data[field_name]
                if isinstance(value, (int, float)):
                    data[field_name] = float(value)
                elif isinstance(value, str):
                    parsed = self.parse_numeric(value)
                    if parsed is None:
                        result.warnings.append(
                            f"Failed to parse numeric value for '{field_name}': '{value}'"
                        )
                    data[field_name] = parsed

        for field_name in self.BOOLEAN_FIELDS:
            if field_name in data and data[field_name] is not None:
                value = data[field_name]
                if isinstance(value, bool):
                    pass  # already correct type
                elif isinstance(value, str):
                    parsed = self.parse_boolean(value)
                    if parsed is None:
                        result.warnings.append(
                            f"Failed to parse boolean value for '{field_name}': '{value}'"
                        )
                    data[field_name] = parsed

        for field_name in self.DATE_FIELDS:
            if field_name in data and data[field_name] is not None:
                value = data[field_name]
                if isinstance(value, datetime):
                    pass  # already correct type
                elif isinstance(value, str):
                    parsed = self.parse_date(value)
                    if parsed is None:
                        result.warnings.append(
                            f"Failed to parse date value for '{field_name}': '{value}'"
                        )
                    data[field_name] = parsed

        # Validate latitude range [-90, 90]
        if "Latitud" in data and data["Latitud"] is not None:
            lat = data["Latitud"]
            if isinstance(lat, (int, float)) and not (-90 <= lat <= 90):
                result.warnings.append(
                    f"Latitud value {lat} out of range [-90, 90]"
                )
                data["Latitud"] = None

        # Validate longitude range [-180, 180]
        if "Longitud" in data and data["Longitud"] is not None:
            lon = data["Longitud"]
            if isinstance(lon, (int, float)) and not (-180 <= lon <= 180):
                result.warnings.append(
                    f"Longitud value {lon} out of range [-180, 180]"
                )
                data["Longitud"] = None

        # Validate URL fields
        for field_name in self.URL_FIELDS:
            if field_name in data and data[field_name] is not None:
                value = data[field_name]
                if isinstance(value, str) and not self._is_valid_url(value):
                    result.warnings.append(
                        f"Invalid URL for '{field_name}': '{value}'"
                    )
                    data[field_name] = None

        result.data = data
        return result

    def parse_numeric(self, value: str) -> Optional[float]:
        """Extract numeric portion from a string value.

        Handles currency symbols, thousands separators, and trailing text.
        Returns None on failure with a warning log.

        Examples:
            "1,500.50" -> 1500.50
            "$2,000" -> 2000.0
            "3 habitaciones" -> 3.0
            "abc" -> None
        """
        if not value or not value.strip():
            return None

        cleaned = value.strip()
        match = self._NUMERIC_PATTERN.search(cleaned)
        if match:
            numeric_str = match.group()
            # Remove thousands separators (commas)
            numeric_str = numeric_str.replace(",", "")
            try:
                return float(numeric_str)
            except ValueError:
                pass

        logger.warning(
            "Failed to parse numeric value",
            value=value,
        )
        return None

    def parse_boolean(self, value: str) -> Optional[bool]:
        """Interpret string as boolean value.

        Recognizes: Si/Si'/Yes/True/true/1 -> True
                    No/False/false/0 -> False
        Returns None for unrecognizable values with a warning log.
        """
        if not value or not value.strip():
            logger.warning(
                "Failed to parse boolean value",
                value=value,
            )
            return None

        normalized = value.strip().lower()

        if normalized in self._TRUE_VALUES:
            return True
        if normalized in self._FALSE_VALUES:
            return False

        logger.warning(
            "Failed to parse boolean value",
            value=value,
        )
        return None

    def parse_date(self, value: str) -> Optional[datetime]:
        """Parse string into a datetime using multiple format attempts.

        Tries ISO 8601, DD/MM/YYYY, MM-DD-YYYY, and other common formats.
        Returns None on failure with a warning log.
        """
        if not value or not value.strip():
            logger.warning(
                "Failed to parse date value",
                value=value,
            )
            return None

        cleaned = value.strip()

        for fmt in self._DATE_FORMATS:
            try:
                return datetime.strptime(cleaned, fmt)
            except ValueError:
                continue

        logger.warning(
            "Failed to parse date value",
            value=value,
        )
        return None

    @staticmethod
    def _is_valid_url(value: str) -> bool:
        """Check if a string is a well-formed HTTP or HTTPS URL."""
        try:
            parsed = urlparse(value)
            return parsed.scheme in ("http", "https") and bool(parsed.netloc)
        except Exception:
            return False
