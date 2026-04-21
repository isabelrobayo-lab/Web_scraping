"""CorrelationIDMiddleware for FastAPI.

Generates a UUID Correlation_ID per request, injects it into a context variable
(accessible from anywhere in the request lifecycle), and adds it to response headers.

Usage:
    from app.middleware.correlation_id import correlation_id_ctx, CorrelationIDMiddleware

    app.add_middleware(CorrelationIDMiddleware)

    # Access from anywhere during a request:
    from app.middleware.correlation_id import correlation_id_ctx
    current_id = correlation_id_ctx.get()
"""

import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

HEADER_NAME = "X-Correlation-ID"

# Context variable for propagating correlation_id within a request lifecycle
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Middleware that generates and propagates a Correlation_ID per request.

    - If the incoming request has an X-Correlation-ID header, it is reused.
    - Otherwise, a new UUID4 is generated.
    - The Correlation_ID is stored in a contextvars.ContextVar for access
      anywhere in the request lifecycle.
    - The Correlation_ID is added to the response headers.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Extract or generate correlation_id
        incoming_id = request.headers.get(HEADER_NAME)
        cid = incoming_id if incoming_id else str(uuid.uuid4())

        # Set in context variable
        token = correlation_id_ctx.set(cid)

        try:
            response: Response = await call_next(request)
            # Add correlation_id to response headers
            response.headers[HEADER_NAME] = cid
            return response
        finally:
            # Reset context variable
            correlation_id_ctx.reset(token)
