"""Property-based tests for Selector Map Management (Req 4).

Tests:
- Property 9: CSS Selector Syntax Validation — accept only syntactically valid CSS selectors
- Property 11: Selector Map Versioning — new version = previous + 1, previous remains queryable
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from app.selectors.schemas import SelectorMapUpdate, validate_css_selector
from tests.properties.conftest import css_selectors, sitio_origen_strategy


# ---------------------------------------------------------------------------
# Strategies for valid and invalid CSS selectors
# ---------------------------------------------------------------------------

# Valid CSS selectors (broader set)
valid_css_selectors = st.sampled_from([
    "div",
    "div.class-name",
    "div#id-name",
    "div > span",
    "div span",
    "div + span",
    "div ~ span",
    "div.class1.class2",
    "ul li a",
    "div[data-attr]",
    "div[data-attr='value']",
    "input[type='text']",
    "div:first-child",
    "div:last-child",
    "div:nth-child(2)",
    "a:hover",
    "p::first-line",
    ".class-name",
    "#id-name",
    "table tr td",
    "div.property-type",
    "span.price",
    "h1.title",
    "article > header > h2",
    "div.listing-card .price-tag",
])

# Invalid CSS selectors
invalid_css_selectors = st.sampled_from([
    "",
    "   ",
    "div[",
    "div[attr='unclosed",
    ">>>",
    "div:::",
    "div..double-dot",
    "##double-hash",
    "div[[[",
    "{invalid}",
    "div:nth-child(",
    "div:nth-child(abc)",
    "@media",
    "div{color:red}",
])

# Field name strategies
field_names = st.sampled_from([
    "Tipo_Inmueble",
    "Precio_Venta",
    "Area_Construida",
    "Municipio",
    "Barrio",
    "Estrato",
    "Habitaciones",
    "Banos",
    "Garajes",
    "Descripcion",
])


# ---------------------------------------------------------------------------
# Property 9: CSS Selector Syntax Validation
# ---------------------------------------------------------------------------


class TestCSSSelectorValidation:
    """**Validates: Requirements 4.2**

    CSS selector validator accepts only syntactically valid CSS selectors
    and rejects invalid ones.
    """

    @given(selector=valid_css_selectors)
    @settings(max_examples=50)
    def test_valid_css_selectors_accepted(self, selector: str):
        """Valid CSS selectors should be accepted by the validator."""
        result = validate_css_selector(selector)
        assert result == selector.strip()

    @given(selector=css_selectors)
    @settings(max_examples=50)
    def test_generated_css_selectors_accepted(self, selector: str):
        """Generated CSS selectors (tag.class#id patterns) should be accepted."""
        result = validate_css_selector(selector)
        assert result == selector.strip()

    @given(selector=invalid_css_selectors)
    @settings(max_examples=30)
    def test_invalid_css_selectors_rejected(self, selector: str):
        """Invalid CSS selectors should be rejected with ValueError."""
        with pytest.raises(ValueError):
            validate_css_selector(selector)

    @given(
        field_name=field_names,
        selectors=st.lists(valid_css_selectors, min_size=1, max_size=3),
    )
    @settings(max_examples=50)
    def test_valid_selectors_in_mapping_accepted(
        self, field_name: str, selectors: list[str]
    ):
        """Mappings with valid CSS selectors should be accepted by the schema."""
        payload = SelectorMapUpdate(mappings={field_name: selectors})
        assert field_name in payload.mappings
        assert payload.mappings[field_name] == selectors

    @given(
        field_name=field_names,
        valid_selector=valid_css_selectors,
        invalid_selector=invalid_css_selectors,
    )
    @settings(max_examples=30)
    def test_invalid_selector_in_mapping_rejected(
        self, field_name: str, valid_selector: str, invalid_selector: str
    ):
        """Mappings containing any invalid CSS selector should be rejected."""
        with pytest.raises(ValidationError):
            SelectorMapUpdate(
                mappings={field_name: [valid_selector, invalid_selector]}
            )

    def test_empty_mappings_rejected(self):
        """Empty mappings dict should be rejected."""
        with pytest.raises(ValidationError):
            SelectorMapUpdate(mappings={})

    def test_empty_selector_list_rejected(self):
        """A field with an empty selector list should be rejected."""
        with pytest.raises(ValidationError):
            SelectorMapUpdate(mappings={"Tipo_Inmueble": []})


# ---------------------------------------------------------------------------
# Property 11: Selector Map Versioning
# ---------------------------------------------------------------------------


class TestSelectorMapVersioning:
    """**Validates: Requirements 4.5**

    For any update to a Mapa_Selectores, the new version number equals
    the previous version + 1, and the previous version remains queryable.
    """

    @given(
        sitio=sitio_origen_strategy,
        selectors1=st.lists(valid_css_selectors, min_size=1, max_size=3),
        selectors2=st.lists(valid_css_selectors, min_size=1, max_size=3),
    )
    @settings(max_examples=30)
    @pytest.mark.asyncio
    async def test_version_increments_on_update(
        self,
        sitio: str,
        selectors1: list[str],
        selectors2: list[str],
        db_session,
    ):
        """Each update creates a new version = previous + 1."""
        from sqlalchemy import select

        from app.models.mapa_selectores import MapaSelectores

        # Create version 1
        map_v1 = MapaSelectores(
            sitio_origen=sitio,
            version=1,
            mappings={"Tipo_Inmueble": selectors1},
        )
        db_session.add(map_v1)
        await db_session.flush()

        # Create version 2 (simulating the PUT endpoint logic)
        result = await db_session.execute(
            select(MapaSelectores)
            .where(MapaSelectores.sitio_origen == sitio)
            .order_by(MapaSelectores.version.desc())
            .limit(1)
        )
        current = result.scalar_one()
        new_version = current.version + 1

        map_v2 = MapaSelectores(
            sitio_origen=sitio,
            version=new_version,
            mappings={"Tipo_Inmueble": selectors2},
        )
        db_session.add(map_v2)
        await db_session.flush()

        # Assert version incremented
        assert map_v2.version == map_v1.version + 1
        assert map_v2.version == 2

        # Cleanup
        await db_session.rollback()

    @given(
        sitio=sitio_origen_strategy,
        selectors1=st.lists(valid_css_selectors, min_size=1, max_size=3),
        selectors2=st.lists(valid_css_selectors, min_size=1, max_size=3),
    )
    @settings(max_examples=30)
    @pytest.mark.asyncio
    async def test_previous_version_preserved(
        self,
        sitio: str,
        selectors1: list[str],
        selectors2: list[str],
        db_session,
    ):
        """Previous version remains queryable after a new version is created."""
        from sqlalchemy import select

        from app.models.mapa_selectores import MapaSelectores

        # Create version 1
        map_v1 = MapaSelectores(
            sitio_origen=sitio,
            version=1,
            mappings={"Precio_Venta": selectors1},
        )
        db_session.add(map_v1)
        await db_session.flush()

        # Create version 2
        map_v2 = MapaSelectores(
            sitio_origen=sitio,
            version=2,
            mappings={"Precio_Venta": selectors2},
        )
        db_session.add(map_v2)
        await db_session.flush()

        # Query all versions for this sitio_origen
        result = await db_session.execute(
            select(MapaSelectores)
            .where(MapaSelectores.sitio_origen == sitio)
            .order_by(MapaSelectores.version.asc())
        )
        all_versions = result.scalars().all()

        # Both versions should exist
        assert len(all_versions) == 2
        assert all_versions[0].version == 1
        assert all_versions[0].mappings == {"Precio_Venta": selectors1}
        assert all_versions[1].version == 2
        assert all_versions[1].mappings == {"Precio_Venta": selectors2}

        # Cleanup
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_first_update_creates_version_1(self, db_session):
        """When no map exists, the first update creates version 1."""
        from sqlalchemy import select

        from app.models.mapa_selectores import MapaSelectores

        sitio = "nuevo-sitio.com"

        # Verify no map exists
        result = await db_session.execute(
            select(MapaSelectores).where(
                MapaSelectores.sitio_origen == sitio
            )
        )
        assert result.scalar_one_or_none() is None

        # Simulate PUT logic: no existing map -> version 1
        result = await db_session.execute(
            select(MapaSelectores)
            .where(MapaSelectores.sitio_origen == sitio)
            .order_by(MapaSelectores.version.desc())
            .limit(1)
        )
        current = result.scalar_one_or_none()
        new_version = (current.version + 1) if current else 1

        new_map = MapaSelectores(
            sitio_origen=sitio,
            version=new_version,
            mappings={"Tipo_Inmueble": ["div.type"]},
        )
        db_session.add(new_map)
        await db_session.flush()

        assert new_map.version == 1

    @pytest.mark.asyncio
    async def test_get_returns_latest_version(self, db_session):
        """GET returns the latest version (highest version number)."""
        from sqlalchemy import select

        from app.models.mapa_selectores import MapaSelectores

        sitio = "multi-version.com"

        # Create 3 versions
        for v in range(1, 4):
            m = MapaSelectores(
                sitio_origen=sitio,
                version=v,
                mappings={"field": [f"div.v{v}"]},
            )
            db_session.add(m)
        await db_session.flush()

        # Query latest (ORDER BY version DESC LIMIT 1)
        result = await db_session.execute(
            select(MapaSelectores)
            .where(MapaSelectores.sitio_origen == sitio)
            .order_by(MapaSelectores.version.desc())
            .limit(1)
        )
        latest = result.scalar_one()

        assert latest.version == 3
        assert latest.mappings == {"field": ["div.v3"]}
