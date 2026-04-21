"""Auth API endpoints.

POST /api/v1/auth/login   — Authenticate and get access token
POST /api/v1/auth/refresh — Refresh access token using httpOnly cookie
POST /api/v1/auth/logout  — Clear session and httpOnly cookie
"""

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service import AuthService
from app.core.config import settings
from app.core.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# Request/Response schemas
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    """Login request body."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Access token response."""

    access_token: str
    expires_in: int


class MessageResponse(BaseModel):
    """Generic message response."""

    detail: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={401: {"model": MessageResponse}},
)
async def login(
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate user and return access token.

    Sets refresh token in httpOnly cookie (Secure; SameSite=Strict).
    Returns generic error message on failure (does not reveal if username
    or password is wrong).
    """
    auth_service = AuthService(db)
    token_pair = await auth_service.login(body.username, body.password)

    if token_pair is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    # Set refresh token in httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=token_pair.refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/v1/auth",
    )

    return TokenResponse(
        access_token=token_pair.access_token,
        expires_in=token_pair.expires_in,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    responses={401: {"model": MessageResponse}},
)
async def refresh_token(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Refresh access token using httpOnly cookie refresh token.

    Does not require re-authentication.
    """
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
        )

    auth_service = AuthService(db)
    result = await auth_service.refresh(refresh_token)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
        )

    return TokenResponse(
        access_token=result["access_token"],
        expires_in=result["expires_in"],
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
)
async def logout(response: Response) -> MessageResponse:
    """Logout user by clearing the httpOnly refresh token cookie."""
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="strict",
        path="/api/v1/auth",
    )

    return MessageResponse(detail="Sesión cerrada")
