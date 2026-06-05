"""Celery task for auto-discovering CSS selectors.

Runs SelectorAutoDiscoverer in background, saves the discovered
selector map, and updates the config's selector_status.
"""

from __future__ import annotations

import asyncio

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.celery_app import celery_app
from app.core.config import settings

logger = structlog.get_logger(__name__)


def _get_session_factory() -> async_sessionmaker:
    """Create an async session factory for Celery workers."""
    engine = create_async_engine(settings.DATABASE_URL, pool_size=3, max_overflow=1)
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def _run_auto_discover(config_id: int, url: str, sitio_origen: str) -> dict:
    """Async implementation of auto-discovery."""
    from app.models.configuracion_scraping import ConfiguracionScraping
    from app.models.mapa_selectores import MapaSelectores
    from app.selectors.auto_discover import SelectorAutoDiscoverer

    session_factory = _get_session_factory()

    async with session_factory() as db:
        # Update status to discovering
        await db.execute(
            update(ConfiguracionScraping)
            .where(ConfiguracionScraping.id == config_id)
            .values(selector_status="discovering")
        )
        await db.commit()

        # Check if a selector map already exists for this sitio_origen
        result = await db.execute(
            select(MapaSelectores)
            .where(MapaSelectores.sitio_origen == sitio_origen)
            .order_by(MapaSelectores.version.desc())
            .limit(1)
        )
        existing_map = result.scalar_one_or_none()

        if existing_map:
            await db.execute(
                update(ConfiguracionScraping)
                .where(ConfiguracionScraping.id == config_id)
                .values(selector_status="ready")
            )
            await db.commit()
            logger.info(
                "Selector map already exists, marked as ready",
                config_id=config_id, sitio_origen=sitio_origen,
                version=existing_map.version,
            )
            return {"status": "ready", "existing_version": existing_map.version}

        # Run auto-discovery
        discoverer = SelectorAutoDiscoverer()
        discovery_result = await discoverer.discover(url, sitio_origen)

        if discovery_result["status"] == "error":
            await db.execute(
                update(ConfiguracionScraping)
                .where(ConfiguracionScraping.id == config_id)
                .values(selector_status="error")
            )
            await db.commit()
            return discovery_result

        # Save discovered selector map
        selector_map = discovery_result["selector_map"]
        if selector_map:
            new_map = MapaSelectores(
                sitio_origen=sitio_origen, version=1, mappings=selector_map,
            )
            db.add(new_map)

        final_status = discovery_result["status"]
        await db.execute(
            update(ConfiguracionScraping)
            .where(ConfiguracionScraping.id == config_id)
            .values(selector_status=final_status)
        )
        await db.commit()

        logger.info(
            "Auto-discovery completed and saved",
            config_id=config_id, sitio_origen=sitio_origen,
            status=final_status, fields_found=discovery_result["fields_found"],
        )
        return discovery_result


@celery_app.task(name="tasks.auto_discover_selectors", bind=True, max_retries=1, acks_late=True)
def auto_discover_selectors(self, config_id: int, url: str, sitio_origen: str) -> dict:
    """Celery task that auto-discovers CSS selectors for a URL."""
    logger.info("Auto-discover task started", config_id=config_id, url=url)
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_run_auto_discover(config_id, url, sitio_origen))
    except Exception as e:
        logger.error("Auto-discover task failed", config_id=config_id, error=str(e))
        loop.run_until_complete(_mark_error(config_id))
        return {"status": "error", "error": str(e)}
    finally:
        loop.close()


async def _mark_error(config_id: int) -> None:
    """Mark config selector_status as error."""
    from app.models.configuracion_scraping import ConfiguracionScraping

    session_factory = _get_session_factory()
    async with session_factory() as db:
        await db.execute(
            update(ConfiguracionScraping)
            .where(ConfiguracionScraping.id == config_id)
            .values(selector_status="error")
        )
        await db.commit()
