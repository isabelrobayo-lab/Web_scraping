"""ScrapingEngine orchestrator with fail-safe error handling.

Orchestrates the full scraping process:
1. Load selector map for the sitio_origen
2. Initialize browser with stealth config
3. Process URLs from crawl queue (with pagination discovery)
4. Extract data from detail pages
5. Validate and persist data via UpsertService + FieldValidator
6. Handle errors gracefully (log, skip, continue)
7. Publish progress via Redis Pub/Sub
8. Rotate sessions every 50 requests
9. Detect deactivated properties after completion

Fail-safe: errors on individual URLs don't stop execution.
"""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass, field
from typing import Any, Optional
from urllib.parse import urljoin, urlparse

import structlog

from app.engine.backoff import ExponentialBackoff
from app.engine.browser_manager import BrowserManager
from app.engine.captcha_detector import CaptchaDetector
from app.engine.crawl_queue import CrawlQueue
from app.engine.data_extractor import DataExtractor
from app.engine.progress_publisher import ProgressPublisher
from app.engine.stealth_config import StealthConfig

logger = structlog.get_logger(__name__)


# Common pagination URL patterns for real estate sites
_PAGINATION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"/pagina\d+", re.IGNORECASE),
    re.compile(r"/page/\d+", re.IGNORECASE),
    re.compile(r"\?page=\d+", re.IGNORECASE),
    re.compile(r"\?pagina=\d+", re.IGNORECASE),
]

# URLs that are never property detail pages — skip them to save time
_ALWAYS_SKIP_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"/inmobiliarias/", re.IGNORECASE),
    re.compile(r"/constructoras/", re.IGNORECASE),
    re.compile(r"/perfil/", re.IGNORECASE),
    re.compile(r"/informacion$", re.IGNORECASE),
    re.compile(r"/blog/", re.IGNORECASE),
    re.compile(r"/noticias/", re.IGNORECASE),
    re.compile(r"/login$", re.IGNORECASE),
    re.compile(r"/registro$", re.IGNORECASE),
    re.compile(r"/favoritos$", re.IGNORECASE),
    re.compile(r"/contacto$", re.IGNORECASE),
    re.compile(r"/ayuda$", re.IGNORECASE),
    re.compile(r"/terminos", re.IGNORECASE),
    re.compile(r"/privacidad", re.IGNORECASE),
    re.compile(r"/politica", re.IGNORECASE),
    re.compile(r"\.(jpg|jpeg|png|gif|svg|pdf|css|js)$", re.IGNORECASE),
]


@dataclass
class ExecutionResult:
    """Result of a scraping engine execution."""

    task_id: str
    pages_processed: int = 0
    records_extracted: int = 0
    records_inserted: int = 0
    records_updated: int = 0
    records_skipped: int = 0
    found_property_keys: set[str] = field(default_factory=set)
    errors: list[dict[str, Any]] = field(default_factory=list)
    status: str = "success"


class ScrapingEngine:
    """Main orchestrator for the scraping process.

    Coordinates all engine components to execute a scraping task:
    - BrowserManager for browser lifecycle
    - CrawlQueue for URL management with pagination discovery
    - DataExtractor for field extraction
    - CaptchaDetector for CAPTCHA detection
    - ExponentialBackoff for 429 handling
    - ProgressPublisher for real-time updates

    Supports URL include/exclude patterns to control which URLs are crawled.

    Fail-safe: errors on individual URLs are logged and skipped,
    never halting the entire execution.
    """

    def __init__(
        self,
        stealth_config: Optional[StealthConfig] = None,
        progress_publisher: Optional[ProgressPublisher] = None,
    ) -> None:
        """Initialize the scraping engine.

        Args:
            stealth_config: Stealth configuration. Uses defaults if not provided.
            progress_publisher: Progress publisher for Redis Pub/Sub.
        """
        self._stealth_config = stealth_config or StealthConfig()
        self._browser_manager = BrowserManager(self._stealth_config)
        self._data_extractor = DataExtractor()
        self._captcha_detector = CaptchaDetector()
        self._backoff = ExponentialBackoff(
            base=self._stealth_config.backoff_initial,
            max_delay=self._stealth_config.backoff_max,
        )
        self._progress_publisher = progress_publisher or ProgressPublisher()
        self._playwright_ctx: Any = None
        self._include_patterns: list[re.Pattern[str]] = []
        self._exclude_patterns: list[re.Pattern[str]] = []

    async def execute(
        self,
        task_id: str,
        base_url: str,
        max_depth: int,
        selector_map: dict[str, list[str]],
        sitio_origen: str,
        correlation_id: str,
        playwright: Optional[Any] = None,
        include_patterns: Optional[list[str]] = None,
        exclude_patterns: Optional[list[str]] = None,
        db_session: Optional[Any] = None,
    ) -> ExecutionResult:
        """Execute a complete scraping task.

        Orchestrates the full scraping process with fail-safe error handling.
        Errors on individual URLs are logged and skipped.

        Args:
            task_id: Unique task identifier.
            base_url: The starting URL to crawl.
            max_depth: Maximum crawl depth (Profundidad_Navegacion).
            selector_map: CSS selector mappings for field extraction.
            sitio_origen: The site origin identifier.
            correlation_id: Correlation ID for traceability.
            playwright: Optional Playwright instance (for testing).
            include_patterns: Regex patterns for URLs to include.
            exclude_patterns: Regex patterns for URLs to exclude.
            db_session: Optional async DB session for persisting data.

        Returns:
            ExecutionResult with counts and status.
        """
        result = ExecutionResult(task_id=task_id)

        # Compile include/exclude patterns
        self._include_patterns = [
            re.compile(p) for p in (include_patterns or [])
        ]
        self._exclude_patterns = [
            re.compile(p) for p in (exclude_patterns or [])
        ]

        logger.info(
            "Scraping engine started",
            task_id=task_id,
            base_url=base_url,
            max_depth=max_depth,
            sitio_origen=sitio_origen,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            correlation_id=correlation_id,
        )

        # Initialize crawl queue with seed URL
        crawl_queue = CrawlQueue(max_depth=max_depth)
        crawl_queue.add(base_url, depth=0)

        try:
            # Launch browser — auto-start Playwright if no instance provided
            if playwright is not None:
                await self._browser_manager.launch(playwright)
            else:
                from playwright.async_api import async_playwright

                self._playwright_ctx = async_playwright()
                pw_instance = await self._playwright_ctx.start()
                await self._browser_manager.launch(pw_instance)

            # Process URLs from the queue
            while not crawl_queue.is_empty:
                item = crawl_queue.next()
                if item is None:
                    break

                try:
                    await self._process_url(
                        item.url,
                        item.depth,
                        crawl_queue,
                        selector_map,
                        sitio_origen,
                        result,
                        correlation_id,
                        db_session,
                    )
                except Exception as e:
                    # Fail-safe: log error, skip URL, continue
                    error_info = {
                        "url": item.url,
                        "depth": item.depth,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    }
                    result.errors.append(error_info)

                    logger.error(
                        "Error processing URL, skipping",
                        url=item.url,
                        error=str(e),
                        error_type=type(e).__name__,
                        correlation_id=correlation_id,
                    )

                result.pages_processed += 1

                # Publish progress
                await self._progress_publisher.publish_progress(
                    task_id=task_id,
                    pages_processed=result.pages_processed,
                    records_extracted=result.records_extracted,
                )

                # Update DB counters every 5 pages for real-time visibility
                if db_session is not None and result.pages_processed % 5 == 0:
                    await self._update_task_progress(
                        db_session, task_id, result
                    )

                # Check if session rotation is needed
                if self._browser_manager.should_rotate():
                    await self._browser_manager.rotate_session()

                # Apply random delay between requests
                delay = self._stealth_config.get_random_delay()
                await asyncio.sleep(delay)

        except Exception as e:
            # Critical error that stops execution
            logger.error(
                "Critical engine error",
                task_id=task_id,
                error=str(e),
                correlation_id=correlation_id,
            )
            result.status = "failure"
            result.errors.append({
                "url": None,
                "error": str(e),
                "error_type": "CriticalError",
            })
        finally:
            # Always close the browser and Playwright context
            await self._browser_manager.close()
            if self._playwright_ctx is not None:
                await self._playwright_ctx.__aexit__(None, None, None)

        # Determine final status
        if result.status != "failure":
            if result.errors:
                result.status = "partial_success"
            else:
                result.status = "success"

        # Publish completion
        await self._progress_publisher.publish_completion(
            task_id=task_id,
            status=result.status,
            pages_processed=result.pages_processed,
            records_extracted=result.records_extracted,
        )

        logger.info(
            "Scraping engine completed",
            task_id=task_id,
            status=result.status,
            pages_processed=result.pages_processed,
            records_extracted=result.records_extracted,
            records_inserted=result.records_inserted,
            records_updated=result.records_updated,
            records_skipped=result.records_skipped,
            errors_count=len(result.errors),
            correlation_id=correlation_id,
        )

        return result

    async def _process_url(
        self,
        url: str,
        depth: int,
        crawl_queue: CrawlQueue,
        selector_map: dict[str, list[str]],
        sitio_origen: str,
        result: ExecutionResult,
        correlation_id: str,
        db_session: Optional[Any] = None,
    ) -> None:
        """Process a single URL: navigate, detect CAPTCHA, extract and persist.

        Args:
            url: The URL to process.
            depth: Current depth level.
            crawl_queue: The crawl queue for adding discovered links.
            selector_map: CSS selector mappings.
            sitio_origen: Site origin identifier.
            result: Execution result to update.
            correlation_id: Correlation ID for traceability.
            db_session: Optional async DB session for persisting data.
        """
        # Navigate to the URL
        response = await self._browser_manager.navigate(url)

        # Check for HTTP 429
        if response is not None and hasattr(response, "status"):
            if response.status == 429:
                delay = self._backoff.record_429()
                logger.warning(
                    "HTTP 429 received, applying backoff",
                    url=url,
                    delay_seconds=delay,
                    correlation_id=correlation_id,
                )
                await asyncio.sleep(delay)
                # Retry once after backoff
                response = await self._browser_manager.navigate(url)
            else:
                self._backoff.reset()

        # Get the page
        page = await self._browser_manager.get_page()

        # Check for CAPTCHA
        captcha_detected = await self._captcha_detector.detect(page)
        if captcha_detected:
            result.errors.append({
                "url": url,
                "error": "CAPTCHA detected",
                "error_type": "CAPTCHA",
            })
            logger.warning(
                "CAPTCHA detected, skipping page",
                url=url,
                correlation_id=correlation_id,
            )
            return

        # Extract data from the page
        extracted = await self._data_extractor.extract(page, selector_map)

        # Check if this is a detail page (has Codigo_Inmueble)
        codigo = extracted.get("Codigo_Inmueble")
        if codigo is not None:
            result.records_extracted += 1
            result.found_property_keys.add(str(codigo))

            logger.info(
                "Property detail found",
                url=url,
                codigo_inmueble=codigo,
                titulo=extracted.get("Titulo_Anuncio", "")[:50],
                correlation_id=correlation_id,
            )

            # Set sitio_origen and url_anuncio if not extracted
            if not extracted.get("Sitio_Origen"):
                extracted["Sitio_Origen"] = sitio_origen
            if not extracted.get("Url_Anuncio"):
                extracted["Url_Anuncio"] = url

            # Persist data if db_session is available
            if db_session is not None:
                await self._persist_record(
                    db_session, extracted, sitio_origen, url,
                    result, correlation_id,
                )

        # Discover links for further crawling (if not at max depth)
        if depth < crawl_queue.max_depth:
            await self._discover_links(page, url, depth, crawl_queue)

    async def _update_task_progress(
        self,
        db_session: Any,
        task_id: str,
        result: ExecutionResult,
    ) -> None:
        """Update task counters in the DB and commit pending records.

        Called every N pages so the API shows live progress
        and persisted records are committed to the DB.
        """
        import uuid

        from sqlalchemy import update

        from app.models.tarea_scraping import TareaScraping

        try:
            # Commit any pending upserted records first
            await db_session.commit()

            await db_session.execute(
                update(TareaScraping)
                .where(TareaScraping.task_id == uuid.UUID(task_id))
                .values(
                    pages_processed=result.pages_processed,
                    records_extracted=result.records_extracted,
                    records_inserted=result.records_inserted,
                    records_updated=result.records_updated,
                    records_skipped=result.records_skipped,
                )
            )
            await db_session.commit()
            logger.info(
                "Progress committed to DB",
                task_id=task_id,
                pages=result.pages_processed,
                extracted=result.records_extracted,
                inserted=result.records_inserted,
            )
        except Exception as e:
            logger.error("Failed to update task progress", error=str(e))
            try:
                await db_session.rollback()
            except Exception:
                pass

    async def _persist_record(
        self,
        db_session: Any,
        extracted: dict[str, Any],
        sitio_origen: str,
        url: str,
        result: ExecutionResult,
        correlation_id: str,
    ) -> None:
        """Validate and persist an extracted record via UpsertService.

        Args:
            db_session: Active async database session.
            extracted: Raw extracted data dictionary.
            sitio_origen: Site origin identifier.
            url: Source URL of the record.
            result: Execution result to update counters.
            correlation_id: Correlation ID for traceability.
        """
        from app.data_logic.field_validator import FieldValidator
        from app.data_logic.upsert_service import UpsertAction, UpsertService

        try:
            # Validate and normalize fields
            validator = FieldValidator()
            validation = validator.validate(extracted)

            for warning in validation.warnings:
                logger.warning(
                    "Field validation warning",
                    warning=warning,
                    url=url,
                    correlation_id=correlation_id,
                )

            # Map extracted field names to DB column names (snake_case)
            record_data = self._map_to_db_columns(validation.data)

            # Clean numeric fields - remove non-numeric characters
            numeric_cols = [
                "habitaciones", "banos", "estacionamiento",
                "administracion_valor", "metros_utiles", "metros_totales",
                "latitud", "longitud", "estrato", "precio_usd",
                "precio_local", "piso_propiedad", "area_privada",
                "area_construida",
            ]
            for col in numeric_cols:
                val = record_data.get(col)
                if val is not None and isinstance(val, str):
                    import re as _re
                    nums = _re.findall(r"[\d.,]+", val.replace(".", "").replace(",", "."))
                    if nums:
                        try:
                            record_data[col] = float(nums[0].replace(",", "."))
                        except (ValueError, IndexError):
                            record_data[col] = None
                    else:
                        record_data[col] = None

            # Ensure required fields
            if not record_data.get("codigo_inmueble"):
                logger.warning(
                    "Record missing codigo_inmueble, skipping persist",
                    url=url,
                    correlation_id=correlation_id,
                )
                return

            if not record_data.get("sitio_origen"):
                record_data["sitio_origen"] = sitio_origen

            # Upsert the record
            upsert_service = UpsertService()
            upsert_result = await upsert_service.upsert(db_session, record_data)
            await db_session.commit()

            if upsert_result.action == UpsertAction.INSERTED:
                result.records_inserted += 1
            elif upsert_result.action == UpsertAction.UPDATED:
                result.records_updated += 1
            elif upsert_result.action == UpsertAction.SKIPPED:
                result.records_skipped += 1

            logger.debug(
                "Record persisted",
                action=upsert_result.action.value,
                codigo_inmueble=upsert_result.codigo_inmueble,
                sitio_origen=upsert_result.sitio_origen,
                correlation_id=correlation_id,
            )

        except Exception as e:
            import traceback
            logger.error(
                "Failed to persist record",
                url=url,
                error=str(e),
                error_type=type(e).__name__,
                traceback=traceback.format_exc()[:500],
                correlation_id=correlation_id,
            )
            result.errors.append({
                "url": url,
                "error": f"Persist failed: {e}",
                "error_type": "Estructura",
            })
            # Rollback the failed transaction but don't stop execution
            try:
                await db_session.rollback()
            except Exception:
                pass

    @staticmethod
    def _map_to_db_columns(data: dict[str, Any]) -> dict[str, Any]:
        """Map extracted field names to database column names.

        Converts PascalCase/MixedCase field names from the selector map
        to snake_case column names used in the SQLAlchemy model.

        Args:
            data: Dictionary with extracted field names.

        Returns:
            Dictionary with snake_case column names.
        """
        mapping: dict[str, str] = {
            "Id_Interno": "id_interno",
            "Codigo_Inmueble": "codigo_inmueble",
            "Tipo_Inmueble": "tipo_inmueble",
            "Habitaciones": "habitaciones",
            "Banos": "banos",
            "Operacion": "operacion",
            "Estacionamiento": "estacionamiento",
            "Administracion_Valor": "administracion_valor",
            "Antiguedad_Detalle": "antiguedad_detalle",
            "Rango_Antiguedad": "rango_antiguedad",
            "Tipo_Estudio": "tipo_estudio",
            "Es_Loft": "es_loft",
            "Dueno_Anuncio": "dueno_anuncio",
            "Telefono_Principal": "telefono_principal",
            "Telefono_Opcional": "telefono_opcional",
            "Correo_Contacto": "correo_contacto",
            "Tipo_Publicador": "tipo_publicador",
            "Descripcion_Anuncio": "descripcion_anuncio",
            "Fecha_Control": "fecha_control",
            "Fecha_Actualizacion": "fecha_actualizacion",
            "Municipio": "municipio",
            "Amoblado": "amoblado",
            "Titulo_Anuncio": "titulo_anuncio",
            "Metros_Utiles": "metros_utiles",
            "Metros_Totales": "metros_totales",
            "Orientacion": "orientacion",
            "Latitud": "latitud",
            "Longitud": "longitud",
            "Url_Anuncio": "url_anuncio",
            "Url_Imagen_Principal": "url_imagen_principal",
            "Sector": "sector",
            "Barrio": "barrio",
            "Estrato": "estrato",
            "Sitio_Origen": "sitio_origen",
            "Fecha_Publicacion": "fecha_publicacion",
            "Direccion": "direccion",
            "Estado_Activo": "estado_activo",
            "Fecha_Desactivacion": "fecha_desactivacion",
            "Precio_USD": "precio_usd",
            "Precio_Local": "precio_local",
            "Simbolo_Moneda": "simbolo_moneda",
            "Piso_Propiedad": "piso_propiedad",
            "Tiene_Ascensores": "tiene_ascensores",
            "Tiene_Balcones": "tiene_balcones",
            "Tiene_Seguridad": "tiene_seguridad",
            "Tiene_Bodega_Deposito": "tiene_bodega_deposito",
            "Tiene_Terraza": "tiene_terraza",
            "Cuarto_Servicio": "cuarto_servicio",
            "Bano_Servicio": "bano_servicio",
            "Tiene_Calefaccion": "tiene_calefaccion",
            "Tiene_Alarma": "tiene_alarma",
            "Acceso_Controlado": "acceso_controlado",
            "Circuito_Cerrado": "circuito_cerrado",
            "Estacionamiento_Visita": "estacionamiento_visita",
            "Cocina_Americana": "cocina_americana",
            "Tiene_Gimnasio": "tiene_gimnasio",
            "Tiene_BBQ": "tiene_bbq",
            "Tiene_Piscina": "tiene_piscina",
            "En_Conjunto_Residencial": "en_conjunto_residencial",
            "Uso_Comercial": "uso_comercial",
            "Cambio_Precio_Valor": "cambio_precio_valor",
            "Precio_Bajo": "precio_bajo",
            "Tipo_Empresa": "tipo_empresa",
            "Glosa_Administracion": "glosa_administracion",
            "Area_Privada": "area_privada",
            "Area_Construida": "area_construida",
        }

        result: dict[str, Any] = {}
        for key, value in data.items():
            db_col = mapping.get(key)
            if db_col:
                result[db_col] = value
        return result

    def _url_passes_filters(self, url: str) -> bool:
        """Check if a URL passes include/exclude pattern filters.

        Args:
            url: The URL to check.

        Returns:
            True if the URL should be crawled.
        """
        # If include patterns are set, URL must match at least one
        if self._include_patterns:
            if not any(p.search(url) for p in self._include_patterns):
                return False

        # If exclude patterns are set, URL must NOT match any
        if self._exclude_patterns:
            if any(p.search(url) for p in self._exclude_patterns):
                return False

        return True

    async def _discover_links(
        self,
        page: Any,
        current_url: str,
        current_depth: int,
        crawl_queue: CrawlQueue,
    ) -> None:
        """Discover internal links and pagination on the page.

        Discovers both regular links and pagination URLs.
        Applies include/exclude filters before adding to queue.

        Args:
            page: The current Playwright page.
            current_url: The current page URL.
            current_depth: The current depth level.
            crawl_queue: The crawl queue to add discovered links to.
        """
        try:
            links = await page.query_selector_all("a[href]")
            for link in links:
                href = await link.get_attribute("href")
                if not href:
                    continue
                # Convert relative URLs to absolute
                absolute_url = urljoin(current_url, href)
                # Strip fragments for cleaner dedup
                parsed = urlparse(absolute_url)
                # Keep query params for pagination URLs
                if parsed.query:
                    clean_url = (
                        f"{parsed.scheme}://{parsed.netloc}"
                        f"{parsed.path}?{parsed.query}"
                    )
                else:
                    clean_url = (
                        f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    )

                if not self._is_internal_link(clean_url, current_url):
                    continue

                # Skip URLs that are never property pages
                if any(p.search(clean_url) for p in _ALWAYS_SKIP_PATTERNS):
                    continue

                if not self._url_passes_filters(clean_url):
                    logger.debug(
                        "URL excluded by filter",
                        url=clean_url,
                    )
                    continue

                # Pagination URLs are treated as same depth (not deeper)
                if self._is_pagination_url(clean_url):
                    crawl_queue.add(clean_url, current_depth)
                else:
                    crawl_queue.add(clean_url, current_depth + 1)

        except Exception as e:
            logger.debug(
                "Link discovery failed",
                url=current_url,
                error=str(e),
            )

    @staticmethod
    def _is_pagination_url(url: str) -> bool:
        """Check if a URL is a pagination URL.

        Pagination URLs should be crawled at the same depth level
        as the current page, not deeper.

        Args:
            url: The URL to check.

        Returns:
            True if the URL matches a known pagination pattern.
        """
        for pattern in _PAGINATION_PATTERNS:
            if pattern.search(url):
                return True
        return False

    @staticmethod
    def _is_internal_link(href: str, base_url: str) -> bool:
        """Check if a link is internal to the same domain.

        Args:
            href: The href attribute value.
            base_url: The base URL to compare against.

        Returns:
            True if the link is internal.
        """
        if not href or href.startswith("#") or href.startswith("javascript:"):
            return False

        try:
            base_parsed = urlparse(base_url)
            href_parsed = urlparse(href)

            # Relative URLs are internal
            if not href_parsed.netloc:
                return True

            # Same domain (with or without www)
            base_domain = base_parsed.netloc.removeprefix("www.")
            href_domain = href_parsed.netloc.removeprefix("www.")
            return href_domain == base_domain
        except Exception:
            return False
