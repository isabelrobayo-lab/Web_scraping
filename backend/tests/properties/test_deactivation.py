"""Property-based tests for DeactivationDetector.

Tests Property 20 from the design document:
- Property 20: Deactivation and reactivation by Sitio_Origen
"""

import string

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from sqlalchemy import select

from app.data_logic.deactivation_detector import DeactivationDetector
from app.models.esquema_inmueble import EsquemaInmueble

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

codigo_inmueble_st = st.text(
    alphabet=string.ascii_uppercase + string.digits,
    min_size=4,
    max_size=15,
)

sitio_origen_st = st.from_regex(
    r"[a-z][a-z0-9]{2,10}\.(com|co|net|org)",
    fullmatch=True,
)


@st.composite
def distinct_codigos(draw, min_size=2, max_size=8):
    """Generate a list of distinct codigo_inmueble values."""
    n = draw(st.integers(min_value=min_size, max_value=max_size))
    codes = set()
    while len(codes) < n:
        codes.add(draw(codigo_inmueble_st))
    return list(codes)


# ---------------------------------------------------------------------------
# Property 20: Deactivation and reactivation by Sitio_Origen
# ---------------------------------------------------------------------------


class TestProperty20DeactivationReactivation:
    """**Validates: Requirements 11**

    Property 20: For any sitio_origen with active records:
    - Records NOT in found_keys are deactivated (Estado_Activo=false, Fecha_Desactivacion set)
    - Previously deactivated records IN found_keys are reactivated (Estado_Activo=true, Fecha_Desactivacion=null)
    - Records from OTHER sitio_origen are never affected (scope isolation)
    """

    @pytest.mark.asyncio
    @settings(max_examples=10)
    @given(
        sitio_origen=sitio_origen_st,
        all_codigos=distinct_codigos(min_size=3, max_size=6),
    )
    async def test_missing_records_are_deactivated(self, db_session, sitio_origen, all_codigos):
        """Records not in found_keys should be marked inactive."""
        # Insert all records as active
        for codigo in all_codigos:
            record = EsquemaInmueble(
                codigo_inmueble=codigo,
                sitio_origen=sitio_origen,
                estado_activo=True,
            )
            db_session.add(record)
        await db_session.flush()

        # Only keep first half as "found"
        found_keys = set(all_codigos[: len(all_codigos) // 2])
        missing_keys = set(all_codigos) - found_keys

        assume(len(found_keys) > 0)
        assume(len(missing_keys) > 0)

        detector = DeactivationDetector()
        result = await detector.detect(db_session, sitio_origen, found_keys)

        assert result["deactivated"] == len(missing_keys)

        # Verify deactivated records
        for codigo in missing_keys:
            stmt = select(EsquemaInmueble).where(
                EsquemaInmueble.codigo_inmueble == codigo,
                EsquemaInmueble.sitio_origen == sitio_origen,
            )
            res = await db_session.execute(stmt)
            record = res.scalar_one()
            assert record.estado_activo is False
            assert record.fecha_desactivacion is not None

    @pytest.mark.asyncio
    @settings(max_examples=10)
    @given(
        sitio_origen=sitio_origen_st,
        all_codigos=distinct_codigos(min_size=3, max_size=6),
    )
    async def test_reappearing_records_are_reactivated(self, db_session, sitio_origen, all_codigos):
        """Previously deactivated records that reappear should be reactivated."""
        from datetime import datetime

        # Insert all records as INACTIVE (previously deactivated)
        for codigo in all_codigos:
            record = EsquemaInmueble(
                codigo_inmueble=codigo,
                sitio_origen=sitio_origen,
                estado_activo=False,
                fecha_desactivacion=datetime.utcnow(),
            )
            db_session.add(record)
        await db_session.flush()

        # All codes reappear
        found_keys = set(all_codigos)

        detector = DeactivationDetector()
        result = await detector.detect(db_session, sitio_origen, found_keys)

        assert result["reactivated"] == len(all_codigos)

        # Verify reactivated records
        for codigo in all_codigos:
            stmt = select(EsquemaInmueble).where(
                EsquemaInmueble.codigo_inmueble == codigo,
                EsquemaInmueble.sitio_origen == sitio_origen,
            )
            res = await db_session.execute(stmt)
            record = res.scalar_one()
            assert record.estado_activo is True
            assert record.fecha_desactivacion is None

    @pytest.mark.asyncio
    @settings(max_examples=10)
    @given(
        sitio_a=sitio_origen_st,
        sitio_b=sitio_origen_st,
        codigos_a=distinct_codigos(min_size=2, max_size=4),
        codigos_b=distinct_codigos(min_size=2, max_size=4),
    )
    async def test_scope_isolation_between_sitios(
        self, db_session, sitio_a, sitio_b, codigos_a, codigos_b
    ):
        """Deactivation for sitio_a should NOT affect records from sitio_b."""
        assume(sitio_a != sitio_b)

        # Insert records for sitio_a
        for codigo in codigos_a:
            db_session.add(EsquemaInmueble(
                codigo_inmueble=codigo,
                sitio_origen=sitio_a,
                estado_activo=True,
            ))

        # Insert records for sitio_b
        for codigo in codigos_b:
            db_session.add(EsquemaInmueble(
                codigo_inmueble=codigo,
                sitio_origen=sitio_b,
                estado_activo=True,
            ))
        await db_session.flush()

        # Deactivate with empty found_keys for sitio_a
        # (but we need at least one found key for safety)
        found_keys_a = {codigos_a[0]}

        detector = DeactivationDetector()
        await detector.detect(db_session, sitio_a, found_keys_a)

        # Verify sitio_b records are UNTOUCHED
        for codigo in codigos_b:
            stmt = select(EsquemaInmueble).where(
                EsquemaInmueble.codigo_inmueble == codigo,
                EsquemaInmueble.sitio_origen == sitio_b,
            )
            res = await db_session.execute(stmt)
            record = res.scalar_one()
            assert record.estado_activo is True
            assert record.fecha_desactivacion is None

    @pytest.mark.asyncio
    @settings(max_examples=10)
    @given(
        sitio_origen=sitio_origen_st,
        all_codigos=distinct_codigos(min_size=2, max_size=5),
    )
    async def test_found_active_records_remain_active(self, db_session, sitio_origen, all_codigos):
        """Records that are found and already active should remain unchanged."""
        # Insert all as active
        for codigo in all_codigos:
            db_session.add(EsquemaInmueble(
                codigo_inmueble=codigo,
                sitio_origen=sitio_origen,
                estado_activo=True,
            ))
        await db_session.flush()

        # All found
        found_keys = set(all_codigos)

        detector = DeactivationDetector()
        result = await detector.detect(db_session, sitio_origen, found_keys)

        assert result["deactivated"] == 0
        assert result["reactivated"] == 0

        # All still active
        for codigo in all_codigos:
            stmt = select(EsquemaInmueble).where(
                EsquemaInmueble.codigo_inmueble == codigo,
                EsquemaInmueble.sitio_origen == sitio_origen,
            )
            res = await db_session.execute(stmt)
            record = res.scalar_one()
            assert record.estado_activo is True
