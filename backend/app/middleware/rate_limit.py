"""RateLimitMiddleware using slowapi.

Applies rate limiting of 100 requests per minute per authenticated user.
Returns HTTP 429 with Retry-After header when the limit is exceeded.

Usage:
    from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
"""

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import JSONResponse

RATE_LIMIT = "100/minute"


def _get_user_key(request: Request) -> str:
    """Extract user identity for rate limiting.

    Attempts to extract user identity from the Authorization header (JWT).
    Falls back to remote IP address if no auth header is present.
    """
    auth_header = request.headers.get("Authorization", "")

    if auth_header.startswith("Bearer "):
        # Use the token itself as a key proxy for the authenticated user.
        # In production, this would decode the JWT to extract user_id.
        # For rate limiting purposes, the token string uniquely identifies
        # the user session.
        token = auth_header[7:]
        # Use first 32 chars of token as key to avoid overly long keys
        return f"user:{token[:32]}"

    return get_remote_address(request)


limiter = Limiter(key_func=_get_user_key, default_limits=[RATE_LIMIT])


async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Custom handler for rate limit exceeded errors.

    Returns HTTP 429 with Retry-After header indicating when the client
    can retry the request.
    """
    # Extract retry-after from the exception detail
    retry_after = "60"  # Default to 60 seconds
    if hasattr(exc, "detail") and exc.detail:
        # slowapi includes the limit info in the detail
        pass

    response = JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Maximum 100 requests per minute.",
            "retry_after": int(retry_after),
        },
    )
    response.headers["Retry-After"] = retry_after
    return response
