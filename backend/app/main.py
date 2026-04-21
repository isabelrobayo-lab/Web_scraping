"""FastAPI application entry point."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

from app.auth.router import router as auth_router
from app.configs.router import router as configs_router
from app.dashboard.router import router as dashboard_router
from app.exports.router import router as exports_router
from app.selectors.router import router as selectors_router
from app.tasks.router import router as tasks_router
from app.websocket.router import router as ws_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.middleware.correlation_id import CorrelationIDMiddleware
from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler

# Configure structured logging at startup
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — start/stop background tasks."""
    # Start Redis Pub/Sub listener as a background task
    from app.websocket.hub import redis_pubsub_listener

    pubsub_task = asyncio.create_task(redis_pubsub_listener())
    yield
    # Cancel the background task on shutdown
    pubsub_task.cancel()
    try:
        await pubsub_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "API REST para gestión de configuraciones de scraping, "
        "ejecución de tareas y consulta de datos inmobiliarios."
    ),
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# --- Middleware registration (order matters: last added = first executed) ---

# Rate limiting via slowapi
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Correlation ID middleware — generates/propagates X-Correlation-ID
app.add_middleware(CorrelationIDMiddleware)


@app.get("/api/v1/health", tags=["health"])
async def health_check() -> dict:
    """Health check endpoint to verify the API is running."""
    return {
        "status": "healthy",
        "service": "scraping-platform-backend",
        "version": settings.APP_VERSION,
    }


# --- Router registration ---
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(configs_router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_V1_PREFIX)
app.include_router(exports_router, prefix=settings.API_V1_PREFIX)
app.include_router(selectors_router, prefix=settings.API_V1_PREFIX)
app.include_router(tasks_router, prefix=settings.API_V1_PREFIX)
app.include_router(ws_router, prefix=settings.API_V1_PREFIX)
