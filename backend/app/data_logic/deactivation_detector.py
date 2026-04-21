"""Deactivation detection for EsquemaInmueble records.

Implements detection of properties that have disappeared from a Sitio_Origen,
marking them as inactive. Also handles reactivation of previously deactivated
records that reappear.

Scope isolation: only evaluates records for the current sitio_origen.
"""

from __future__ import annotations

from datetime import datetime

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.esquema_inmueble import EsquemaInmueble

logger = structlog.get_logger(__name__)


class DeactivationDetector:
    """Detection of deactivated properties by Sitio_Origen.

    Compares the set of found property keys against the database to:
    1. Mark missing records as inactive (Estado_Activo=false, Fecha_Desactivacion=now)
    2. Reactivate previously deactivated records that reappear (Estado_Activo=true, Fecha_Desactivacion=null)

    Scope isolation: only affects records of the current sitio_origen.
    """

    async def detect(
        self,
        session: AsyncSession,
        sitio_origen: str,
        found_keys: set[str],
    ) -> dict[str, int]:
        """Detect deactivations and reactivations for a sitio_origen.

        Args:
            session: Active async database session.
            sitio_origen: The site origin to evaluate.
            found_keys: Set of codigo_inmueble values found in the current scrape.

        Returns:
            Dictionary with counts: {"deactivated": int, "reactivated": int}
        """
        deactivated_count = await self._deactivate_missing(
            session, sitio_origen, found_keys
        )
        reactivated_count = await self._reactivate_found(
            session, sitio_origen, found_keys
        )

        logger.info(
            "Deactivation detection completed",
            sitio_origen=sitio_origen,
            found_keys_count=len(found_keys),
            deactivated=deactivated_count,
            reactivated=reactivated_count,
        )

        return {
            "deactivated": deactivated_count,
            "reactivated": reactivated_count,
        }

    async def _deactivate_missing(
        self,
        session: AsyncSession,
        sitio_origen: str,
        found_keys: set[str],
    ) -> int:
        """Mark records NOT in found_keys as inactive.

        Only affects records that are currently active for the given sitio_origen.
        Sets Estado_Activo=false and Fecha_Desactivacion=now.
        """
        if not found_keys:
            # If no keys found, don't deactivate anything (safety measure)
            return 0

        now = datetime.utcnow()

        # Find active records for this sitio_origen that are NOT in found_keys
        stmt = select(EsquemaInmueble).where(
            EsquemaInmueble.sitio_origen == sitio_origen,
            EsquemaInmueble.estado_activo == True,  # noqa: E712
            EsquemaInmueble.codigo_inmueble.notin_(found_keys),
        )
        result = await session.execute(stmt)
        records_to_deactivate = result.scalars().all()

        count = 0
        for record in records_to_deactivate:
            record.estado_activo = False
            record.fecha_desactivacion = now
            count += 1

        if count > 0:
            await session.flush()
            logger.info(
                "Records deactivated",
                sitio_origen=sitio_origen,
                count=count,
            )

        return count

    async def _reactivate_found(
        self,
        session: AsyncSession,
        sitio_origen: str,
        found_keys: set[str],
    ) -> int:
        """Reactivate previously deactivated records that reappear.

        Only affects records that are currently inactive for the given sitio_origen
        and whose codigo_inmueble is in found_keys.
        Sets Estado_Activo=true and Fecha_Desactivacion=null.
        """
        if not found_keys:
            return 0

        # Find inactive records for this sitio_origen that ARE in found_keys
        stmt = select(EsquemaInmueble).where(
            EsquemaInmueble.sitio_origen == sitio_origen,
            EsquemaInmueble.estado_activo == False,  # noqa: E712
            EsquemaInmueble.codigo_inmueble.in_(found_keys),
        )
        result = await session.execute(stmt)
        records_to_reactivate = result.scalars().all()

        count = 0
        for record in records_to_reactivate:
            record.estado_activo = True
            record.fecha_desactivacion = None
            count += 1

        if count > 0:
            await session.flush()
            logger.info(
                "Records reactivated",
                sitio_origen=sitio_origen,
                count=count,
            )

        return count
