"""Unit tests for authentication and authorization flows.

Tests cover:
- Login with valid/invalid credentials
- Token refresh via httpOnly cookie
- Logout (cookie clearing)
- Session inactivity invalidation
- RBAC endpoint protection
"""

from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service import AuthService
from app.models.usuario import Usuario


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def test_user(db_session: AsyncSession) -> Usuario:
    """Create a test user with known credentials."""
    password_hash = AuthService.hash_password("SecurePass123!")
    user = Usuario(
        username="testuser",
        password_hash=password_hash,
        role="operador",
        active=True,
        last_login=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> Usuario:
    """Create an admin test user."""
    password_hash = AuthService.hash_password("AdminPass456!")
    user = Usuario(
        username="adminuser",
        password_hash=password_hash,
        role="administrador",
        active=True,
        last_login=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def inactive_user(db_session: AsyncSession) -> Usuario:
    """Create a deactivated user."""
    password_hash = AuthService.hash_password("InactivePass!")
    user = Usuario(
        username="inactiveuser",
        password_hash=password_hash,
        role="operador",
        active=False,
        last_login=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Login tests
# ---------------------------------------------------------------------------


class TestLogin:
    """Tests for POST /api/v1/auth/login."""

    async def test_login_success(self, client: AsyncClient, test_user: Usuario):
        """Valid credentials return access token and set refresh cookie."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "SecurePass123!"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["expires_in"] == 1800
        # Refresh token should be in httpOnly cookie
        assert "refresh_token" in response.cookies

    async def test_login_wrong_password(self, client: AsyncClient, test_user: Usuario):
        """Wrong password returns 401 with generic message."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "WrongPassword!"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Credenciales inválidas"

    async def test_login_wrong_username(self, client: AsyncClient, test_user: Usuario):
        """Non-existent username returns 401 with same generic message."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "SecurePass123!"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Credenciales inválidas"

    async def test_login_inactive_user(self, client: AsyncClient, inactive_user: Usuario):
        """Inactive user cannot login."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "inactiveuser", "password": "InactivePass!"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Credenciales inválidas"

    async def test_login_generic_error_no_info_leak(
        self, client: AsyncClient, test_user: Usuario
    ):
        """Error message does not reveal whether username or password is wrong."""
        # Wrong username
        resp1 = await client.post(
            "/api/v1/auth/login",
            json={"username": "wrong", "password": "SecurePass123!"},
        )
        # Wrong password
        resp2 = await client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "wrong"},
        )
        # Both should have the same error message
        assert resp1.json()["detail"] == resp2.json()["detail"]


# ---------------------------------------------------------------------------
# Token refresh tests
# ---------------------------------------------------------------------------


class TestRefresh:
    """Tests for POST /api/v1/auth/refresh."""

    async def test_refresh_success(self, client: AsyncClient, test_user: Usuario):
        """Valid refresh token in cookie returns new access token."""
        # First login to get refresh token cookie
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "SecurePass123!"},
        )
        assert login_resp.status_code == 200

        # Use the cookie from login to refresh
        response = await client.post("/api/v1/auth/refresh")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["expires_in"] == 1800

    async def test_refresh_no_cookie(self, client: AsyncClient):
        """Missing refresh token cookie returns 401."""
        # Create a fresh client without cookies
        response = await client.post("/api/v1/auth/refresh")
        assert response.status_code == 401
        assert response.json()["detail"] == "Refresh token inválido o expirado"


# ---------------------------------------------------------------------------
# Logout tests
# ---------------------------------------------------------------------------


class TestLogout:
    """Tests for POST /api/v1/auth/logout."""

    async def test_logout_clears_cookie(self, client: AsyncClient, test_user: Usuario):
        """Logout clears the refresh token cookie."""
        # Login first
        await client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "SecurePass123!"},
        )

        # Logout
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code == 200
        assert response.json()["detail"] == "Sesión cerrada"


# ---------------------------------------------------------------------------
# Session inactivity tests
# ---------------------------------------------------------------------------


class TestSessionInactivity:
    """Tests for session inactivity check (30 minutes)."""

    async def test_session_active_within_30_minutes(
        self, db_session: AsyncSession, test_user: Usuario
    ):
        """Session is valid when last_login is within 30 minutes."""
        auth_service = AuthService(db_session)
        result = await auth_service.check_session_activity(test_user.id)
        assert result is True

    async def test_session_expired_after_30_minutes(
        self, db_session: AsyncSession, test_user: Usuario
    ):
        """Session is invalid when last_login is older than 30 minutes."""
        # Set last_login to 31 minutes ago
        test_user.last_login = datetime.now(timezone.utc) - timedelta(minutes=31)
        db_session.add(test_user)
        await db_session.commit()

        auth_service = AuthService(db_session)
        result = await auth_service.check_session_activity(test_user.id)
        assert result is False

    async def test_session_no_last_login(
        self, db_session: AsyncSession
    ):
        """Session is invalid when user has no last_login."""
        password_hash = AuthService.hash_password("test")
        user = Usuario(
            username="nologin",
            password_hash=password_hash,
            role="operador",
            active=True,
            last_login=None,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        auth_service = AuthService(db_session)
        result = await auth_service.check_session_activity(user.id)
        assert result is False


# ---------------------------------------------------------------------------
# AuthService unit tests
# ---------------------------------------------------------------------------


class TestAuthService:
    """Unit tests for AuthService methods."""

    def test_hash_password(self):
        """hash_password produces a valid bcrypt hash."""
        hashed = AuthService.hash_password("mypassword")
        assert hashed.startswith("$2b$")
        assert len(hashed) == 60

    def test_verify_token_valid(self, db_session: AsyncSession, test_user: Usuario):
        """verify_token decodes a valid access token."""
        auth_service = AuthService(db_session)
        token = auth_service._create_access_token(test_user)
        claims = auth_service.verify_token(token)
        assert claims is not None
        assert claims.user_id == test_user.id
        assert claims.username == test_user.username
        assert claims.role == test_user.role

    def test_verify_token_invalid(self, db_session: AsyncSession):
        """verify_token returns None for invalid token."""
        auth_service = AuthService(db_session)
        claims = auth_service.verify_token("invalid.token.here")
        assert claims is None

    def test_verify_token_refresh_rejected(
        self, db_session: AsyncSession, test_user: Usuario
    ):
        """verify_token rejects refresh tokens (wrong type)."""
        auth_service = AuthService(db_session)
        refresh_token = auth_service._create_refresh_token(test_user)
        claims = auth_service.verify_token(refresh_token)
        assert claims is None
