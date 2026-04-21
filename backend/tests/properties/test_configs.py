"""Property-based tests for Configuration CRUD API (Req 1).

Tests:
- Property 1: URL Validation — accepts only well-formed HTTP/HTTPS URLs
- Property 2: Depth Range — accepts only integers [1, 10]
- Property 3: Cron Validation — accepts only valid cron expressions, produces non-empty preview
- Property 4: Soft Delete — performing soft delete sets active=false, record remains queryable
"""

import pytest
from hypothesis import given, assume, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from app.configs.schemas import ConfigCreate, ModoEjecucion, TipoOperacion
from app.configs.cron_utils import validate_cron_expression, get_cron_preview
from tests.properties.conftest import (
    cron_expression_strategy,
    profundidad_strategy,
    tipo_operacion_strategy,
    urls,
)


# ---------------------------------------------------------------------------
# Strategies for invalid inputs
# ---------------------------------------------------------------------------

# URLs that are NOT valid HTTP/HTTPS
invalid_url_strategy = st.one_of(
    # No scheme
    st.from_regex(r"[a-z]{3,10}\.[a-z]{2,4}", fullmatch=True),
    # FTP scheme
    st.from_regex(r"ftp://[a-z]{3,10}\.[a-z]{2,4}", fullmatch=True),
    # Missing domain
    st.just("http://"),
    st.just("https://"),
    # Random text
    st.text(min_size=1, max_size=50).filter(
        lambda s: not s.startswith("http://") and not s.startswith("https://")
    ),
)

# Depth values outside [1, 10]
invalid_depth_strategy = st.one_of(
    st.integers(max_value=0),
    st.integers(min_value=11),
)

# Invalid cron expressions
invalid_cron_strategy = st.one_of(
    # Too few fields
    st.just("* *"),
    st.just("* * *"),
    st.just("* * * *"),
    # Too many fields
    st.just("* * * * * *"),
    st.just("* * * * * * *"),
    # Invalid values
    st.just("60 * * * *"),
    st.just("* 25 * * *"),
    st.just("* * 32 * *"),
    st.just("* * * 13 *"),
    st.just("* * * * 8"),
    # Non-numeric garbage
    st.just("abc def ghi jkl mno"),
)


# ---------------------------------------------------------------------------
# Property 1: URL Validation
# ---------------------------------------------------------------------------


class TestURLValidation:
    """**Validates: Requirements 1.2**

    URL validation accepts only well-formed HTTP/HTTPS URLs, rejects all others.
    """

    @given(url=urls)
    @settings(max_examples=50)
    def test_valid_http_https_urls_accepted(self, url: str):
        """Valid HTTP/HTTPS URLs should be accepted by the schema."""
        config = ConfigCreate(
            url_base=url,
            profundidad_navegacion=1,
            tipo_operacion=TipoOperacion.VENTA,
            modo_ejecucion=ModoEjecucion.MANUAL,
        )
        assert config.url_base == url

    @given(url=invalid_url_strategy)
    @settings(max_examples=50)
    def test_invalid_urls_rejected(self, url: str):
        """Non-HTTP/HTTPS URLs and malformed URLs should be rejected."""
        assume(len(url) > 0 and len(url) <= 2048)
        with pytest.raises(ValidationError) as exc_info:
            ConfigCreate(
                url_base=url,
                profundidad_navegacion=1,
                tipo_operacion=TipoOperacion.VENTA,
                modo_ejecucion=ModoEjecucion.MANUAL,
            )
        # Verify the error is about URL validation
        errors = exc_info.value.errors()
        url_errors = [e for e in errors if "url_base" in str(e.get("loc", []))]
        assert len(url_errors) > 0


# ---------------------------------------------------------------------------
# Property 2: Depth Range
# ---------------------------------------------------------------------------


class TestDepthRange:
    """**Validates: Requirements 1.3**

    Depth range validation accepts only integers [1, 10], rejects all others.
    """

    @given(depth=profundidad_strategy)
    @settings(max_examples=50)
    def test_valid_depth_accepted(self, depth: int):
        """Depth values in [1, 10] should be accepted."""
        config = ConfigCreate(
            url_base="https://www.example.com",
            profundidad_navegacion=depth,
            tipo_operacion=TipoOperacion.VENTA,
            modo_ejecucion=ModoEjecucion.MANUAL,
        )
        assert config.profundidad_navegacion == depth
        assert 1 <= config.profundidad_navegacion <= 10

    @given(depth=invalid_depth_strategy)
    @settings(max_examples=50)
    def test_invalid_depth_rejected(self, depth: int):
        """Depth values outside [1, 10] should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ConfigCreate(
                url_base="https://www.example.com",
                profundidad_navegacion=depth,
                tipo_operacion=TipoOperacion.VENTA,
                modo_ejecucion=ModoEjecucion.MANUAL,
            )
        errors = exc_info.value.errors()
        depth_errors = [
            e for e in errors if "profundidad_navegacion" in str(e.get("loc", []))
        ]
        assert len(depth_errors) > 0


# ---------------------------------------------------------------------------
# Property 3: Cron Validation
# ---------------------------------------------------------------------------


class TestCronValidation:
    """**Validates: Requirements 1.4**

    Cron validation accepts only valid cron expressions and produces
    non-empty human-readable preview.
    """

    @given(cron=cron_expression_strategy())
    @settings(max_examples=50)
    def test_valid_cron_accepted_and_preview_generated(self, cron: str):
        """Valid cron expressions should be accepted and produce a non-empty preview."""
        # Validation should not raise
        result = validate_cron_expression(cron)
        assert result == cron

        # Preview should be non-empty
        preview = get_cron_preview(cron)
        assert preview is not None
        assert len(preview) > 0

    @given(cron=cron_expression_strategy())
    @settings(max_examples=50)
    def test_valid_cron_in_programado_mode(self, cron: str):
        """Valid cron with Programado mode should create a valid config."""
        config = ConfigCreate(
            url_base="https://www.example.com",
            profundidad_navegacion=5,
            tipo_operacion=TipoOperacion.VENTA,
            modo_ejecucion=ModoEjecucion.PROGRAMADO,
            cron_expression=cron,
        )
        assert config.cron_expression == cron

    @given(cron=invalid_cron_strategy)
    @settings(max_examples=30)
    def test_invalid_cron_rejected(self, cron: str):
        """Invalid cron expressions should be rejected."""
        with pytest.raises((ValueError, ValidationError)):
            ConfigCreate(
                url_base="https://www.example.com",
                profundidad_navegacion=5,
                tipo_operacion=TipoOperacion.VENTA,
                modo_ejecucion=ModoEjecucion.PROGRAMADO,
                cron_expression=cron,
            )

    def test_cron_required_when_programado(self):
        """Cron expression must be provided when mode is Programado."""
        with pytest.raises(ValidationError) as exc_info:
            ConfigCreate(
                url_base="https://www.example.com",
                profundidad_navegacion=5,
                tipo_operacion=TipoOperacion.VENTA,
                modo_ejecucion=ModoEjecucion.PROGRAMADO,
                cron_expression=None,
            )
        assert "cron_expression" in str(exc_info.value)

    def test_cron_cleared_when_manual(self):
        """Cron expression should be cleared when mode is Manual."""
        config = ConfigCreate(
            url_base="https://www.example.com",
            profundidad_navegacion=5,
            tipo_operacion=TipoOperacion.VENTA,
            modo_ejecucion=ModoEjecucion.MANUAL,
            cron_expression="0 3 * * *",
        )
        assert config.cron_expression is None


# ---------------------------------------------------------------------------
# Property 4: Soft Delete
# ---------------------------------------------------------------------------


class TestSoftDelete:
    """**Validates: Requirements 1.7**

    Performing soft delete sets active=false, record remains queryable.
    """

    @given(
        url=urls,
        depth=profundidad_strategy,
        tipo=tipo_operacion_strategy,
    )
    @settings(max_examples=30)
    @pytest.mark.asyncio
    async def test_soft_delete_sets_active_false(
        self, url: str, depth: int, tipo: str, db_session
    ):
        """Soft deleting a config sets active=false without removing the record."""
        from sqlalchemy import select
        from app.models.configuracion_scraping import ConfiguracionScraping

        # Create a config
        config = ConfiguracionScraping(
            url_base=url,
            profundidad_navegacion=depth,
            tipo_operacion=tipo,
            modo_ejecucion="Manual",
            active=True,
        )
        db_session.add(config)
        await db_session.flush()
        config_id = config.id

        # Perform soft delete
        config.active = False
        await db_session.flush()

        # Verify record still exists and is inactive
        result = await db_session.execute(
            select(ConfiguracionScraping).where(
                ConfiguracionScraping.id == config_id
            )
        )
        deleted_config = result.scalar_one_or_none()
        assert deleted_config is not None, "Record should still exist after soft delete"
        assert deleted_config.active is False, "active should be False after soft delete"
        assert deleted_config.url_base == url
        assert deleted_config.profundidad_navegacion == depth

        # Cleanup for next hypothesis iteration
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_soft_deleted_record_queryable_with_filter(self, db_session):
        """Soft-deleted records can be found when querying without active filter."""
        from sqlalchemy import select
        from app.models.configuracion_scraping import ConfiguracionScraping

        # Create active and inactive configs
        active_config = ConfiguracionScraping(
            url_base="https://www.active.com",
            profundidad_navegacion=3,
            tipo_operacion="Venta",
            modo_ejecucion="Manual",
            active=True,
        )
        inactive_config = ConfiguracionScraping(
            url_base="https://www.inactive.com",
            profundidad_navegacion=5,
            tipo_operacion="Arriendo",
            modo_ejecucion="Manual",
            active=False,
        )
        db_session.add_all([active_config, inactive_config])
        await db_session.flush()

        # Query all (no filter) — both should be returned
        result = await db_session.execute(select(ConfiguracionScraping))
        all_configs = result.scalars().all()
        assert len(all_configs) == 2

        # Query only active — only one should be returned
        result = await db_session.execute(
            select(ConfiguracionScraping).where(
                ConfiguracionScraping.active == True  # noqa: E712
            )
        )
        active_configs = result.scalars().all()
        assert len(active_configs) == 1
        assert active_configs[0].url_base == "https://www.active.com"

        # Query only inactive — only one should be returned
        result = await db_session.execute(
            select(ConfiguracionScraping).where(
                ConfiguracionScraping.active == False  # noqa: E712
            )
        )
        inactive_configs = result.scalars().all()
        assert len(inactive_configs) == 1
        assert inactive_configs[0].url_base == "https://www.inactive.com"
