"""Upsert service for EsquemaInmueble records.

Implements transactional upsert logic using PostgreSQL ON CONFLICT
on the unique constraint (codigo_inmueble, sitio_origen).

Handles:
- INSERT: new records with Estado_Activo=true, Fecha_Control=now
- UPDATE: changed records with Fecha_Actualizacion=now
- SKIP: unchanged records (idempotence)
- Price change detection: Cambio_Precio_Valor = new - old, Precio_Bajo = (new < old)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.esquema_inmueble import EsquemaInmueble

logger = structlog.get_logger(__name__)


class UpsertAction(str, Enum):
    """Possible outcomes of an upsert operation."""

    INSERTED = "inserted"
    UPDATED = "updated"
    SKIPPED = "skipped"


@dataclass
class UpsertResult:
    """Result of a single upsert operation."""

    action: UpsertAction
    codigo_inmueble: str
    sitio_origen: str
    cambio_precio_valor: Decimal | None = None
    precio_bajo: bool | None = None


# Fields to compare for change detection (excludes computed/meta fields)
_COMPARE_FIELDS: list[str] = [
    "tipo_inmueble",
    "habitaciones",
    "banos",
    "operacion",
    "estacionamiento",
    "administracion_valor",
    "antiguedad_detalle",
    "rango_antiguedad",
    "tipo_estudio",
    "es_loft",
    "dueno_anuncio",
    "telefono_principal",
    "telefono_opcional",
    "correo_contacto",
    "tipo_publicador",
    "descripcion_anuncio",
    "municipio",
    "amoblado",
    "titulo_anuncio",
    "metros_utiles",
    "metros_totales",
    "orientacion",
    "latitud",
    "longitud",
    "url_anuncio",
    "url_imagen_principal",
    "sector",
    "barrio",
    "estrato",
    "fecha_publicacion",
    "direccion",
    "precio_usd",
    "precio_local",
    "simbolo_moneda",
    "piso_propiedad",
    "tiene_ascensores",
    "tiene_balcones",
    "tiene_seguridad",
    "tiene_bodega_deposito",
    "tiene_terraza",
    "cuarto_servicio",
    "bano_servicio",
    "tiene_calefaccion",
    "tiene_alarma",
    "acceso_controlado",
    "circuito_cerrado",
    "estacionamiento_visita",
    "cocina_americana",
    "tiene_gimnasio",
    "tiene_bbq",
    "tiene_piscina",
    "en_conjunto_residencial",
    "uso_comercial",
    "tipo_empresa",
    "glosa_administracion",
    "area_privada",
    "area_construida",
]


class UpsertService:
    """Upsert logic for EsquemaInmueble records.

    Uses Clave_Upsert = (codigo_inmueble, sitio_origen) to determine
    whether to insert, update, or skip a record.
    """

    async def upsert(
        self,
        session: AsyncSession,
        record_data: dict[str, Any],
    ) -> UpsertResult:
        """Perform upsert for a single record within the given session.

        Args:
            session: Active async database session (caller manages transaction).
            record_data: Dictionary with field values for the record.

        Returns:
            UpsertResult indicating the action taken.
        """
        codigo_inmueble = record_data["codigo_inmueble"]
        sitio_origen = record_data["sitio_origen"]

        # Look up existing record by unique key
        stmt = select(EsquemaInmueble).where(
            EsquemaInmueble.codigo_inmueble == codigo_inmueble,
            EsquemaInmueble.sitio_origen == sitio_origen,
        )
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is None:
            return await self._insert(session, record_data)
        else:
            return await self._update_or_skip(session, existing, record_data)

    async def upsert_batch(
        self,
        session: AsyncSession,
        records: list[dict[str, Any]],
    ) -> list[UpsertResult]:
        """Perform upsert for a batch of records within a single transaction.

        Args:
            session: Active async database session.
            records: List of record dictionaries.

        Returns:
            List of UpsertResult for each record.
        """
        results: list[UpsertResult] = []
        for record_data in records:
            result = await self.upsert(session, record_data)
            results.append(result)
        return results

    async def _insert(
        self,
        session: AsyncSession,
        record_data: dict[str, Any],
    ) -> UpsertResult:
        """Insert a new record with Estado_Activo=true and Fecha_Control=now."""
        now = datetime.utcnow()

        # Set insert-specific fields
        record_data["estado_activo"] = True
        record_data["fecha_control"] = now

        # Remove id_interno if present (auto-generated)
        record_data.pop("id_interno", None)

        new_record = EsquemaInmueble(**record_data)
        session.add(new_record)
        await session.flush()

        logger.info(
            "Record inserted",
            codigo_inmueble=record_data["codigo_inmueble"],
            sitio_origen=record_data["sitio_origen"],
        )

        return UpsertResult(
            action=UpsertAction.INSERTED,
            codigo_inmueble=record_data["codigo_inmueble"],
            sitio_origen=record_data["sitio_origen"],
        )

    async def _update_or_skip(
        self,
        session: AsyncSession,
        existing: EsquemaInmueble,
        record_data: dict[str, Any],
    ) -> UpsertResult:
        """Update if changed, skip if unchanged (idempotence)."""
        if not self._has_changes(existing, record_data):
            logger.debug(
                "Record unchanged, skipping",
                codigo_inmueble=existing.codigo_inmueble,
                sitio_origen=existing.sitio_origen,
            )
            return UpsertResult(
                action=UpsertAction.SKIPPED,
                codigo_inmueble=existing.codigo_inmueble,
                sitio_origen=existing.sitio_origen,
            )

        # Detect price change before updating
        cambio_precio_valor, precio_bajo = self._detect_price_change(
            existing, record_data
        )

        # Apply updates
        now = datetime.utcnow()
        for field in _COMPARE_FIELDS:
            if field in record_data:
                setattr(existing, field, record_data[field])

        existing.fecha_actualizacion = now

        # Apply price change fields
        if cambio_precio_valor is not None:
            existing.cambio_precio_valor = cambio_precio_valor
            existing.precio_bajo = precio_bajo

        await session.flush()

        logger.info(
            "Record updated",
            codigo_inmueble=existing.codigo_inmueble,
            sitio_origen=existing.sitio_origen,
            cambio_precio_valor=str(cambio_precio_valor) if cambio_precio_valor else None,
        )

        return UpsertResult(
            action=UpsertAction.UPDATED,
            codigo_inmueble=existing.codigo_inmueble,
            sitio_origen=existing.sitio_origen,
            cambio_precio_valor=cambio_precio_valor,
            precio_bajo=precio_bajo,
        )

    def _has_changes(
        self, existing: EsquemaInmueble, record_data: dict[str, Any]
    ) -> bool:
        """Compare existing record with new data to detect changes."""
        for field in _COMPARE_FIELDS:
            if field not in record_data:
                continue
            old_value = getattr(existing, field, None)
            new_value = record_data[field]

            # Normalize for comparison (Decimal vs float)
            if isinstance(old_value, Decimal) and isinstance(new_value, (int, float)):
                new_value = Decimal(str(new_value))
            elif isinstance(new_value, Decimal) and isinstance(old_value, (int, float)):
                old_value = Decimal(str(old_value))

            if old_value != new_value:
                return True
        return False

    def _detect_price_change(
        self, existing: EsquemaInmueble, record_data: dict[str, Any]
    ) -> tuple[Decimal | None, bool | None]:
        """Detect price change and compute Cambio_Precio_Valor and Precio_Bajo.

        Returns:
            Tuple of (cambio_precio_valor, precio_bajo) or (None, None) if no price change.
        """
        new_precio = record_data.get("precio_local")
        old_precio = existing.precio_local

        if new_precio is None or old_precio is None:
            return None, None

        # Normalize to Decimal
        if not isinstance(new_precio, Decimal):
            new_precio = Decimal(str(new_precio))
        if not isinstance(old_precio, Decimal):
            old_precio = Decimal(str(old_precio))

        if new_precio == old_precio:
            return None, None

        cambio = new_precio - old_precio
        precio_bajo = new_precio < old_precio

        return cambio, precio_bajo
