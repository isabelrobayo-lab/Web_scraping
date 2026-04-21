# Feature: web-scraping-platform, Property 5: Concurrent Execution Guard
"""Property test for concurrent execution guard.

**Validates: Requirements 2.4**

Property 5: For any Configuración_Scraping that has a Tarea_Scraping with
status 'queued' or 'running', attempting to enqueue a new execution SHALL
be rejected.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from hypothesis import given, settings, strategies as st
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service import UserClaims
from app.core.database import get_db
from app.main import app
from app.models.configuracion_scraping import ConfiguracionScraping
from app.models.tarea_scraping import TareaScraping


def _mock_admin_user() -> UserClaims:
    """Create a mock admin user for auth bypass."""
    return UserClaims(user_id=1, username="admin", role="administrador")


# Strategies for generating test data
config_id_strategy = st.integers(min_value=1, max_value=1000)
blocking_status_strategy = st.sampled_from(["queued", "running"])


@pytest.mark.property
class TestConcurrentExecutionGuard:
    """Property tests for the concurrent execution guard (Property 5)."""

    @given(blocking_status=blocking_status_strategy)
    @settings(max_examples=20)
    @pytest.mark.asyncio
    async def test_reject_when_task_active(
        self,
        db_session: AsyncSession,
        blocking_status: str,
    ) -> None:
        """For any config with a queued/running task, new execution is rejected (409).

        **Validates: Requirements 2.4**
        """
        # Create a configuration
        config = ConfiguracionScraping(
            url_base="https://example.com",
            profundidad_navegacion=3,
            tipo_operacion="Venta",
            modo_ejecucion="Manual",
            active=True,
        )
        db_session.add(config)
        await db_session.flush()
        await db_session.refresh(config)

        # Create an existing task with blocking status
        existing_task = TareaScraping(
            task_id=uuid.uuid4(),
            config_id=config.id,
            status=blocking_status,
            correlation_id=str(uuid.uuid4()),
        )
        db_session.add(existing_task)
        await db_session.flush()

        # Override dependencies
        async def _override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = _override_get_db

        # Mock auth to return admin user
        with patch(
            "app.auth.dependencies.get_current_user",
            new_callable=AsyncMock,
            return_value=_mock_admin_user(),
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.post(
                    f"/api/v1/tasks/{config.id}/execute",
                    headers={"Authorization": "Bearer fake-token"},
                )

                # Should be rejected with 409
                assert response.status_code == 409
                body = response.json()
                assert "ya existe" in body["detail"].lower() or "ejecución" in body["detail"].lower()

        app.dependency_overrides.clear()
        await db_session.rollback()

    @given(
        completed_status=st.sampled_from(
            ["success", "partial_success", "failure"]
        )
    )
    @settings(max_examples=15)
    @pytest.mark.asyncio
    async def test_allow_when_no_active_task(
        self,
        db_session: AsyncSession,
        completed_status: str,
    ) -> None:
        """For any config with only completed tasks, new execution is allowed (202).

        **Validates: Requirements 2.4** (inverse — guard does not block completed tasks)
        """
        # Create a configuration
        config = ConfiguracionScraping(
            url_base="https://example.com",
            profundidad_navegacion=3,
            tipo_operacion="Venta",
            modo_ejecucion="Manual",
            active=True,
        )
        db_session.add(config)
        await db_session.flush()
        await db_session.refresh(config)

        # Create a completed task (should NOT block)
        completed_task = TareaScraping(
            task_id=uuid.uuid4(),
            config_id=config.id,
            status=completed_status,
            correlation_id=str(uuid.uuid4()),
        )
        db_session.add(completed_task)
        await db_session.flush()

        # Override dependencies
        async def _override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = _override_get_db

        # Mock auth and Celery task
        with (
            patch(
                "app.auth.dependencies.get_current_user",
                new_callable=AsyncMock,
                return_value=_mock_admin_user(),
            ),
            patch(
                "app.tasks.router.execute_scraping"
            ) as mock_celery,
        ):
            mock_celery.apply_async = lambda **kwargs: None

            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.post(
                    f"/api/v1/tasks/{config.id}/execute",
                    headers={"Authorization": "Bearer fake-token"},
                )

                # Should be accepted with 202
                assert response.status_code == 202
                body = response.json()
                assert body["status"] == "queued"
                assert "task_id" in body
                assert "correlation_id" in body

        app.dependency_overrides.clear()
        await db_session.rollback()
