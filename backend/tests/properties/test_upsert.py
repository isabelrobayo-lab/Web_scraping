"""Property-based tests for UpsertService.

Tests Properties 14, 15, and 16 from the design document:
- Property 14: Upsert insert/update/skip behavior
- Property 15: Price change calculation
- Property 16: Upsert round-trip (insert then query returns equivalent)
"""

import string
from decimal import Decimal

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from sqlalchemy import select

from app.data_logic.upsert_service import UpsertAction, UpsertResult, UpsertService
from app.models.esquema_inmueble import EsquemaInmueble

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

codigo_inmueble_st = st.text(
    alphabet=string.ascii_uppercase + string.digits,
    min_size=4,
    max_size=20,
)

sitio_origen_st = st.from_regex(
    r"[a-z][a-z0-9\-]{2,15}\.(com|co|net|org)",
    fullmatch=True,
)

precio_st = st.decimals(
    min_value=Decimal("100.00"),
    max_value=Decimal("9999999.99"),
    places=2,
    allow_nan=False,
    allow_infinity=False,
)


@st.composite
def record_data_strategy(draw):
    """Generate a valid record_data dictionary for upsert."""
    return {
        "codigo_inmueble": draw(codigo_inmueble_st),
        "sitio_origen": draw(sitio_origen_st),
        "tipo_inmueble": draw(st.sampled_from(["Casa", "Apartamento", "Oficina", "Local"])),
        "habitaciones": draw(st.integers(min_value=1, max_value=10)),
        "banos": draw(st.integers(min_value=1, max_value=6)),
        "operacion": draw(st.sampled_from(["Venta", "Arriendo"])),
        "precio_local": draw(precio_st),
        "municipio": draw(st.text(min_size=3, max_size=30, alphabet=string.ascii_letters)),
    }


# ---------------------------------------------------------------------------
# Property 14: Upsert insert/update/skip behavior
# ---------------------------------------------------------------------------


class TestProperty14UpsertBehavior:
    """**Validates: Requirements 6**

    Property 14: For any valid record:
    - First upsert -> INSERTED
    - Upsert with changed data -> UPDATED
    - Upsert with same data -> SKIPPED
    """

    @pytest.mark.asyncio
    @settings(max_examples=10)
    @given(data=record_data_strategy())
    async def test_first_upsert_inserts(self, db_session, data):
        """First upsert of a new record should always result in INSERTED."""
        service = UpsertService()
        result = await service.upsert(db_session, data)

        assert result.action == UpsertAction.INSERTED
        assert result.codigo_inmueble == data["codigo_inmueble"]
        assert result.sitio_origen == data["sitio_origen"]

    @pytest.mark.asyncio
    @settings(max_examples=10)
    @given(data=record_data_strategy())
    async def test_unchanged_upsert_skips(self, db_session, data):
        """Upserting the same data twice should SKIP on the second call."""
        service = UpsertService()

        # First insert
        await service.upsert(db_session, data.copy())

        # Second upsert with same data
        result = await service.upsert(db_session, data.copy())

        assert result.action == UpsertAction.SKIPPED

    @pytest.mark.asyncio
    @settings(max_examples=10)
    @given(data=record_data_strategy())
    async def test_changed_upsert_updates(self, db_session, data):
        """Upserting with changed data should result in UPDATED."""
        service = UpsertService()

        # First insert
        await service.upsert(db_session, data.copy())

        # Modify a field
        modified_data = data.copy()
        modified_data["habitaciones"] = (data["habitaciones"] % 10) + 1

        result = await service.upsert(db_session, modified_data)

        assert result.action == UpsertAction.UPDATED

    @pytest.mark.asyncio
    @settings(max_examples=10)
    @given(data=record_data_strategy())
    async def test_insert_sets_estado_activo_and_fecha_control(self, db_session, data):
        """Inserted records should have Estado_Activo=true and Fecha_Control set."""
        service = UpsertService()
        await service.upsert(db_session, data)

        stmt = select(EsquemaInmueble).where(
            EsquemaInmueble.codigo_inmueble == data["codigo_inmueble"],
            EsquemaInmueble.sitio_origen == data["sitio_origen"],
        )
        result = await db_session.execute(stmt)
        record = result.scalar_one()

        assert record.estado_activo is True
        assert record.fecha_control is not None

    @pytest.mark.asyncio
    @settings(max_examples=10)
    @given(data=record_data_strategy())
    async def test_update_sets_fecha_actualizacion(self, db_session, data):
        """Updated records should have Fecha_Actualizacion set."""
        service = UpsertService()

        # Insert
        await service.upsert(db_session, data.copy())

        # Modify and update
        modified_data = data.copy()
        modified_data["banos"] = (data["banos"] % 6) + 1
        await service.upsert(db_session, modified_data)

        stmt = select(EsquemaInmueble).where(
            EsquemaInmueble.codigo_inmueble == data["codigo_inmueble"],
            EsquemaInmueble.sitio_origen == data["sitio_origen"],
        )
        result = await db_session.execute(stmt)
        record = result.scalar_one()

        assert record.fecha_actualizacion is not None


# ---------------------------------------------------------------------------
# Property 15: Price change calculation
# ---------------------------------------------------------------------------


class TestProperty15PriceChange:
    """**Validates: Requirements 6**

    Property 15: When precio_local changes:
    - Cambio_Precio_Valor = new_precio - old_precio
    - Precio_Bajo = (new_precio < old_precio)
    """

    @pytest.mark.asyncio
    @settings(max_examples=10)
    @given(
        data=record_data_strategy(),
        new_precio=precio_st,
    )
    async def test_price_change_calculation(self, db_session, data, new_precio):
        """Price change should compute correct Cambio_Precio_Valor and Precio_Bajo."""
        service = UpsertService()

        # Insert with original price
        await service.upsert(db_session, data.copy())

        old_precio = data["precio_local"]

        # Skip if prices are equal (no change to detect)
        if new_precio == old_precio:
            return

        # Update with new price
        modified_data = data.copy()
        modified_data["precio_local"] = new_precio
        result = await service.upsert(db_session, modified_data)

        assert result.action == UpsertAction.UPDATED

        # Verify price change fields
        expected_cambio = new_precio - old_precio
        expected_bajo = new_precio < old_precio

        assert result.cambio_precio_valor == expected_cambio
        assert result.precio_bajo == expected_bajo

    @pytest.mark.asyncio
    @settings(max_examples=10)
    @given(data=record_data_strategy())
    async def test_no_price_change_when_same_price(self, db_session, data):
        """When price doesn't change, Cambio_Precio_Valor should be None."""
        service = UpsertService()

        # Insert
        await service.upsert(db_session, data.copy())

        # Update with different non-price field
        modified_data = data.copy()
        modified_data["habitaciones"] = (data["habitaciones"] % 10) + 1

        result = await service.upsert(db_session, modified_data)

        assert result.cambio_precio_valor is None
        assert result.precio_bajo is None


# ---------------------------------------------------------------------------
# Property 16: Upsert round-trip
# ---------------------------------------------------------------------------


class TestProperty16UpsertRoundTrip:
    """**Validates: Requirements 6**

    Property 16: After inserting a record via upsert, querying by
    (codigo_inmueble, sitio_origen) returns an equivalent record.
    """

    @pytest.mark.asyncio
    @settings(max_examples=10)
    @given(data=record_data_strategy())
    async def test_insert_then_query_returns_equivalent(self, db_session, data):
        """Inserted record should be retrievable with equivalent field values."""
        service = UpsertService()

        # Insert
        await service.upsert(db_session, data)

        # Query back
        stmt = select(EsquemaInmueble).where(
            EsquemaInmueble.codigo_inmueble == data["codigo_inmueble"],
            EsquemaInmueble.sitio_origen == data["sitio_origen"],
        )
        result = await db_session.execute(stmt)
        record = result.scalar_one()

        # Verify key fields match
        assert record.codigo_inmueble == data["codigo_inmueble"]
        assert record.sitio_origen == data["sitio_origen"]
        assert record.tipo_inmueble == data["tipo_inmueble"]
        assert record.habitaciones == data["habitaciones"]
        assert record.banos == data["banos"]
        assert record.operacion == data["operacion"]
        assert record.municipio == data["municipio"]

        # Verify precio_local (Decimal comparison)
        if data["precio_local"] is not None:
            assert record.precio_local == data["precio_local"]
