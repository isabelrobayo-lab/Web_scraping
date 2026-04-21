"""Root conftest for the scraping platform test suite.

Provides:
- Async SQLite in-memory database session for unit tests (no PostgreSQL required)
- Table creation/teardown per test session
- AsyncClient (httpx) fixture for API integration tests
- Hypothesis settings profiles (CI vs dev)
"""

import os

import pytest
from hypothesis import HealthCheck, Phase, settings as hypothesis_settings
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.database import Base, get_db
from app.main import app

# Import all models so Base.metadata knows about all tables
import app.models  # noqa: F401

# ---------------------------------------------------------------------------
# Hypothesis profiles
# ---------------------------------------------------------------------------

# Development profile: fast feedback loop
hypothesis_settings.register_profile(
    "dev",
    max_examples=10,
    phases=[Phase.explicit, Phase.generate, Phase.target],
    suppress_health_check=[HealthCheck.too_slow],
)

# CI profile: thorough testing
hypothesis_settings.register_profile(
    "ci",
    max_examples=100,
    phases=[Phase.explicit, Phase.reuse, Phase.generate, Phase.target, Phase.shrink],
)

# Load profile from environment variable HYPOTHESIS_PROFILE, default to "dev"
hypothesis_settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))

# ---------------------------------------------------------------------------
# Database fixtures (SQLite in-memory for unit tests)
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio as the async backend for tests."""
    return "asyncio"


@pytest.fixture(scope="session")
async def test_engine():
    """Create an async SQLite engine for the test session."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )
    # Create all tables at session start
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables at session end
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncSession:
    """Provide a transactional database session that rolls back after each test.

    This ensures test isolation without needing to recreate tables per test.
    """
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session
        await session.rollback()


# ---------------------------------------------------------------------------
# API client fixture
# ---------------------------------------------------------------------------


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """Provide an httpx AsyncClient configured to test the FastAPI app.

    Overrides the database dependency to use the test SQLite session.
    """

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
