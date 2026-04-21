"""FastAPI dependencies for authentication and RBAC.

Provides get_current_user dependency and RBACMiddleware (as a dependency)
for role-based permission enforcement.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service import AuthService, UserClaims
from app.core.database import get_db

# Bearer token scheme for OpenAPI docs
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ] = None,
    db: AsyncSession = Depends(get_db),
) -> UserClaims:
    """Extract and validate JWT access token from Authorization header.

    Also checks session inactivity (30 minutes).
    Raises HTTP 401 if token is missing, invalid, or session expired.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso requerido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_service = AuthService(db)
    user_claims = auth_service.verify_token(credentials.credentials)

    if user_claims is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check session inactivity
    session_active = await auth_service.check_session_activity(user_claims.user_id)
    if not session_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada por inactividad",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_claims


class RBACMiddleware:
    """Role-Based Access Control implemented as a FastAPI dependency.

    Usage:
        @router.get("/configs", dependencies=[Depends(RBACMiddleware("configs:read"))])
        async def list_configs(...):
            ...
    """

    ROLE_PERMISSIONS: dict[str, list[str]] = {
        "administrador": [
            "configs:read",
            "configs:write",
            "dashboard:read",
            "dashboard:export",
            "tasks:execute",
            "tasks:read",
            "users:manage",
        ],
        "operador": [
            "configs:read",
            "dashboard:read",
            "dashboard:export",
            "tasks:read",
        ],
    }

    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    async def __call__(
        self, current_user: UserClaims = Depends(get_current_user)
    ) -> UserClaims:
        """Check if the current user's role has the required permission."""
        role = current_user.role.lower()
        permissions = self.ROLE_PERMISSIONS.get(role, [])

        if self.required_permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos insuficientes",
            )

        return current_user

    @classmethod
    def has_permission(cls, role: str, permission: str) -> bool:
        """Check if a role has a specific permission (utility method)."""
        permissions = cls.ROLE_PERMISSIONS.get(role.lower(), [])
        return permission in permissions
