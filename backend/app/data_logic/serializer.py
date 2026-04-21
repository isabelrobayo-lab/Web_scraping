"""Serialization and deserialization of EsquemaInmueble records.

Implements JSON serialization preserving all 66 fields (including nulls)
and deserialization with type restoration, as specified in Req 9.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# All 66 fields of the EsquemaInmueble in canonical order
ALL_FIELDS: list[str] = [
    "Id_Interno",
    "Codigo_Inmueble",
    "Tipo_Inmueble",
    "Habitaciones",
    "Baños",
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
    "Cambio_Precio_Valor",
    "Precio_Bajo",
    "Tipo_Empresa",
    "Glosa_Administracion",
    "Area_Privada",
    "Area_Construida",
]

# Required fields that must be present for deserialization
REQUIRED_FIELDS: list[str] = ["Codigo_Inmueble", "Sitio_Origen"]

# Fields that should be deserialized as datetime
DATE_FIELDS: set[str] = {
    "Fecha_Control",
    "Fecha_Actualizacion",
    "Fecha_Publicacion",
    "Fecha_Desactivacion",
}

# Fields that should be deserialized as float/numeric
NUMERIC_FIELDS: set[str] = {
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
}

# Fields that should be deserialized as boolean
BOOLEAN_FIELDS: set[str] = {
    "Tipo_Estudio",
    "Es_Loft",
    "Amoblado",
    "Estado_Activo",
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
}

# Integer-typed numeric fields (subset of NUMERIC_FIELDS)
INTEGER_FIELDS: set[str] = {
    "Habitaciones",
    "Baños",
    "Estacionamiento",
    "Estrato",
    "Piso_Propiedad",
}


class SerializationError(Exception):
    """Raised when serialization or deserialization fails."""

    def __init__(self, message: str, missing_fields: list[str] | None = None):
        super().__init__(message)
        self.missing_fields = missing_fields or []


class Serializer:
    """Serialization/deserialization of EsquemaInmueble records.

    Preserves all 66 fields including nulls with correct JSON types.
    Dates are serialized as ISO 8601 strings.
    """

    def to_json(self, record: dict[str, Any]) -> str:
        """Serialize a record to JSON preserving all 66 fields including nulls.

        Args:
            record: Dictionary with EsquemaInmueble field values.

        Returns:
            JSON string with all 66 fields, correct types, and nulls preserved.
        """
        output: dict[str, Any] = {}

        for field_name in ALL_FIELDS:
            value = record.get(field_name)

            if value is None:
                output[field_name] = None
            elif isinstance(value, datetime):
                output[field_name] = value.isoformat()
            elif isinstance(value, bool):
                output[field_name] = value
            elif isinstance(value, (int, float)):
                output[field_name] = value
            else:
                output[field_name] = str(value)

        return json.dumps(output, ensure_ascii=False)

    def from_json(self, json_str: str) -> dict[str, Any]:
        """Deserialize a JSON string to an EsquemaInmueble record.

        Restores all field types (strings, numbers, booleans, dates, nulls).
        Extra fields are ignored with a warning. Missing required fields
        (Codigo_Inmueble, Sitio_Origen) raise SerializationError.

        Args:
            json_str: JSON string to deserialize.

        Returns:
            Dictionary with all 66 fields and correct types restored.

        Raises:
            SerializationError: If required fields are missing.
        """
        raw = json.loads(json_str)

        # Check for missing required fields
        missing = [f for f in REQUIRED_FIELDS if f not in raw or raw[f] is None]
        if missing:
            raise SerializationError(
                f"Missing required fields: {', '.join(missing)}",
                missing_fields=missing,
            )

        # Warn about extra fields
        known_fields = set(ALL_FIELDS)
        extra_fields = [k for k in raw if k not in known_fields]
        if extra_fields:
            logger.warning(
                "Ignoring extra fields during deserialization",
                extra_fields=extra_fields,
            )

        # Build output with type restoration
        output: dict[str, Any] = {}

        for field_name in ALL_FIELDS:
            value = raw.get(field_name)

            if value is None:
                output[field_name] = None
            elif field_name in DATE_FIELDS:
                output[field_name] = self._restore_date(value)
            elif field_name in BOOLEAN_FIELDS:
                output[field_name] = bool(value) if value is not None else None
            elif field_name in INTEGER_FIELDS:
                output[field_name] = self._restore_integer(value)
            elif field_name in NUMERIC_FIELDS:
                output[field_name] = self._restore_numeric(value)
            else:
                # String fields and Id_Interno
                if field_name == "Id_Interno" and value is not None:
                    output[field_name] = int(value) if not isinstance(value, int) else value
                else:
                    output[field_name] = str(value) if value is not None else None

        return output

    @staticmethod
    def _restore_date(value: Any) -> datetime | None:
        """Restore a date value from ISO 8601 string."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except (ValueError, TypeError):
                return None
        return None

    @staticmethod
    def _restore_numeric(value: Any) -> float | None:
        """Restore a numeric value from JSON."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _restore_integer(value: Any) -> int | None:
        """Restore an integer value from JSON."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
