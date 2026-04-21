"""AuthService — Authentication and token management.

Handles login with bcrypt password verification, JWT access token generation
(30min expiry), refresh token in httpOnly cookie, and session inactivity checks.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.usuario import Usuario


class TokenPair:
    """Represents an access token + refresh token pair."""

    def __init__(self, access_token: str, refresh_token: str, expires_in: int):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in


class UserClaims:
    """Decoded JWT claims for an authenticated user."""

    def __init__(self, user_id: int, username: str, role: str):
        self.user_id = user_id
        self.username = username
        self.role = role


class AuthService:
    """Authentication and authorization service."""

    ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
    SESSION_INACTIVITY_MINUTES = settings.SESSION_INACTIVITY_MINUTES

    def __init__(self, db: AsyncSession):
        self.db = db

    async def login(self, username: str, password: str) -> TokenPair | None:
        """Authenticate user with bcrypt, return JWT access token (30min)
        and refresh token. Returns None if credentials are invalid."""
        stmt = select(Usuario).where(
            Usuario.username == username, Usuario.active.is_(True)
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        if not self._verify_password(password, user.password_hash):
            return None

        # Update last_login timestamp
        await self.db.execute(
            update(Usuario)
            .where(Usuario.id == user.id)
            .values(last_login=datetime.utcnow())
        )
        await self.db.commit()

        access_token = self._create_access_token(user)
        refresh_token = self._create_refresh_token(user)

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh(self, refresh_token: str) -> dict[str, Any] | None:
        """Renew access token using refresh token without re-authentication.
        Returns None if refresh token is invalid or expired."""
        claims = self._decode_token(refresh_token)
        if claims is None:
            return None

        if claims.get("type") != "refresh":
            return None

        user_id = claims.get("sub")
        if user_id is None:
            return None

        # Verify user still exists and is active
        stmt = select(Usuario).where(
            Usuario.id == int(user_id), Usuario.active.is_(True)
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        access_token = self._create_access_token(user)
        return {
            "access_token": access_token,
            "expires_in": self.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    def verify_token(self, token: str) -> UserClaims | None:
        """Verify and decode a JWT access token. Returns None if invalid."""
        claims = self._decode_token(token)
        if claims is None:
            return None

        if claims.get("type") != "access":
            return None

        return UserClaims(
            user_id=int(claims["sub"]),
            username=claims["username"],
            role=claims["role"],
        )

    async def check_session_activity(self, user_id: int) -> bool:
        """Check if user session is still active (not inactive > 30 minutes).
        Returns True if session is valid, False if expired."""
        stmt = select(Usuario).where(Usuario.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return False

        if user.last_login is None:
            return False

        last_activity = user.last_login
        # Ensure timezone-aware comparison
        if last_activity.tzinfo is None:
            last_activity = last_activity.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        inactivity = now - last_activity

        if inactivity > timedelta(minutes=self.SESSION_INACTIVITY_MINUTES):
            return False

        return True

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def _verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a bcrypt hash."""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def _create_access_token(self, user: Usuario) -> str:
        """Create a JWT access token with 30-minute expiry."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES),
            "jti": str(uuid.uuid4()),
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def _create_refresh_token(self, user: Usuario) -> str:
        """Create a JWT refresh token with configurable expiry."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user.id),
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS),
            "jti": str(uuid.uuid4()),
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def _decode_token(token: str) -> dict[str, Any] | None:
        """Decode and verify a JWT token. Returns None if invalid/expired."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None
