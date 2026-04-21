# Tasks — Plataforma Paramétrica de Web Scraping Inmobiliario

## Task 1: Project Setup and Infrastructure

- [x] 1.1 Initialize Python backend project with FastAPI 0.115+, Poetry, and project structure (app/, tests/, alembic/)
- [x] 1.2 Initialize React 18 + TypeScript + Vite 5.x frontend project with Tailwind CSS 3.x and Shadcn UI
- [x] 1.3 Configure PostgreSQL 15.4+ database connection with SQLAlchemy 2.0+ async and asyncpg
- [x] 1.4 Configure Celery + Redis as task queue with Celery Beat for scheduled tasks
- [x] 1.5 Configure pytest 8.0+ with Hypothesis for property-based testing and Vitest 3.x for frontend
- [x] 1.6 Create Docker Compose configuration for local development (FastAPI, PostgreSQL, Redis, Celery worker, Celery Beat)
- [x] 1.7 Configure Alembic for database migrations

## Task 2: Database Schema and Models

- [x] 2.1 Create SQLAlchemy model for USUARIO table (id, username, password_hash, role, created_at, last_login, active)
- [x] 2.2 Create SQLAlchemy model for CONFIGURACION_SCRAPING table (id, url_base, profundidad_navegacion, tipo_operacion, modo_ejecucion, cron_expression, active, created_at, updated_at, last_execution_at)
- [x] 2.3 Create SQLAlchemy model for MAPA_SELECTORES table (id, sitio_origen, version, mappings as JSONB, created_at)
- [x] 2.4 Create SQLAlchemy model for TAREA_SCRAPING table (task_id UUID, config_id FK, status, correlation_id, started_at, ended_at, duration_seconds, pages_processed, records_extracted, records_inserted, records_updated, records_skipped, errors_by_type JSONB)
- [x] 2.5 Create SQLAlchemy model for ESQUEMA_INMUEBLE table with all 66 fields including correct types (boolean for Tipo_Estudio, Es_Loft, etc.; timestamp for Fecha_Publicacion; unique constraint on codigo_inmueble + sitio_origen)
- [x] 2.6 Create SQLAlchemy model for LOG_ERROR table (id, task_id FK, sitio_origen, url, error_type, error_message, error_metadata JSONB, correlation_id, created_at)
- [x] 2.7 Create SQLAlchemy model for EXPORTACION table (export_id UUID, user_id FK, format, filters JSONB, status, record_count, file_path, created_at, completed_at)
- [x] 2.8 Create Alembic migration with all indexes (upsert unique constraint, dashboard query indexes, error indexes, task indexes, selector map version index)

## Task 3: Observability Layer (Req 14)

- [x] 3.1 Implement CorrelationIDMiddleware for FastAPI that generates UUID Correlation_ID per request, injects into context, and adds to response headers
- [x] 3.2 Implement StructuredLogger using structlog that emits JSON logs with timestamp, level, service, correlation_id, and message fields
- [x] 3.3 Implement Correlation_ID propagation to Celery tasks via task headers
- [x] 3.4 Implement RateLimitMiddleware using slowapi with 100 req/min per authenticated user, returning HTTP 429 with Retry-After header
- [x] 3.5 Write property tests for Correlation_ID propagation (Property 22) and structured log format (Property 23)

## Task 4: Authentication and Authorization (Req 12)

- [x] 4.1 Implement AuthService with login (bcrypt password verification, JWT access token 30min, refresh token in httpOnly cookie)
- [x] 4.2 Implement token refresh endpoint using httpOnly cookie refresh token
- [x] 4.3 Implement logout endpoint that clears httpOnly cookie
- [x] 4.4 Implement session inactivity check (invalidate after 30 minutes)
- [x] 4.5 Implement RBACMiddleware with Administrador and Operador role permissions
- [x] 4.6 Implement auth API endpoints: POST /api/v1/auth/login, POST /api/v1/auth/refresh, POST /api/v1/auth/logout
- [x] 4.7 Write property test for RBAC enforcement (Property 21) and unit tests for auth flows

## Task 5: Configuration CRUD API (Req 1)

- [x] 5.1 Implement Pydantic schemas for Configuracion_Scraping with URL validation, depth range [1-10], and cron expression validation
- [x] 5.2 Implement CRUD endpoints: GET/POST /api/v1/configs, GET/PUT/DELETE /api/v1/configs/{id} with soft delete
- [x] 5.3 Implement cron expression validation with human-readable preview generation
- [x] 5.4 Implement paginated list response including last_execution_at field
- [x] 5.5 Write property tests for URL validation (Property 1), depth range (Property 2), cron validation (Property 3), and soft delete (Property 4)

## Task 6: Selector Map Management (Req 4)

- [x] 6.1 Implement Pydantic schemas for Mapa_Selectores with CSS selector syntax validation
- [x] 6.2 Implement API endpoints: GET/PUT /api/v1/selector-maps/{sitio_origen} with automatic version increment and previous version preservation
- [x] 6.3 Write property tests for CSS selector validation (Property 9) and selector map versioning (Property 11)

## Task 7: Data Validation and Field Parsing (Req 8)

- [x] 7.1 Implement FieldValidator with NUMERIC_FIELDS, BOOLEAN_FIELDS, and DATE_FIELDS lists matching the Diccionario de Datos
- [x] 7.2 Implement parse_numeric that extracts numeric portion from strings, returns None on failure with warning
- [x] 7.3 Implement parse_boolean that interprets Si/No, True/False, 1/0 values, returns None for unrecognizable with warning
- [x] 7.4 Implement parse_date that parses multiple date formats, returns None on failure with warning
- [x] 7.5 Implement latitude [-90, 90] and longitude [-180, 180] range validation
- [x] 7.6 Implement URL validation for Url_Anuncio and Url_Imagen_Principal fields
- [x] 7.7 Write property test for field type parsing (Property 17) covering numeric, boolean, date, and coordinate validation

## Task 8: Serialization and Deserialization (Req 9)

- [x] 8.1 Implement Serializer.to_json that preserves all 66 fields including nulls with correct JSON types
- [x] 8.2 Implement Serializer.from_json that restores all field types (strings, numbers, booleans, dates, nulls)
- [x] 8.3 Implement extra field handling (ignore with warning) and missing required field validation (Codigo_Inmueble, Sitio_Origen)
- [x] 8.4 Write property tests for serialization round-trip (Property 18) and deserialization robustness (Property 19)

## Task 9: Upsert Logic (Req 6)

- [x] 9.1 Implement UpsertService with Clave_Upsert computation (Codigo_Inmueble + Sitio_Origen)
- [x] 9.2 Implement insert logic with Estado_Activo=true and Fecha_Control=now for new records
- [x] 9.3 Implement update logic with Fecha_Actualizacion=now for changed records, skip for unchanged (idempotence)
- [x] 9.4 Implement price change detection with Cambio_Precio_Valor = new - old and Precio_Bajo = (new < old)
- [x] 9.5 Implement transactional upsert using PostgreSQL ON CONFLICT within database transaction
- [x] 9.6 Write property tests for upsert behavior (Property 14), price change (Property 15), and upsert round-trip (Property 16)

## Task 10: Error Logging (Req 7)

- [x] 10.1 Implement ErrorLogger with error type classification (Timeout, CAPTCHA, Estructura, Conexion) and Correlation_ID
- [x] 10.2 Implement error metadata recording per type (timeout threshold/elapsed, CAPTCHA url/title, Estructura field/selector, Conexion url/details)
- [x] 10.3 Implement execution summary generation with detailed counts (pages_processed, records_extracted/inserted/updated/skipped, errors_by_type, duration_seconds)
- [x] 10.4 Write unit tests for each error type classification and summary generation

## Task 11: Deactivation Detection (Req 11)

- [x] 11.1 Implement DeactivationDetector.detect that marks missing records as inactive (Estado_Activo=false, Fecha_Desactivacion=now)
- [x] 11.2 Implement reactivation logic for previously deactivated records that reappear (Estado_Activo=true, Fecha_Desactivacion=null)
- [x] 11.3 Implement Sitio_Origen scope isolation (only evaluate deactivation for current sitio_origen)
- [x] 11.4 Write property test for deactivation and reactivation (Property 20)

## Task 12: Scraping Engine Core (Req 3, 5)

- [x] 12.1 Implement BrowserManager with Playwright stealth configuration (webdriver=false, random viewport, plugins emulation)
- [x] 12.2 Implement StealthConfig with User-Agent pool (20+), random delay [2-7s], and session rotation every 50 requests
- [x] 12.3 Implement CrawlQueue with depth control, URL deduplication, and visited URL tracking
- [x] 12.4 Implement DataExtractor that extracts 66 fields using Mapa_Selectores with selector priority order (first match wins)
- [x] 12.5 Implement backoff exponencial for HTTP 429 responses (30s base, doubling, max 600s)
- [x] 12.6 Implement CAPTCHA detection heuristics and skip-with-log behavior
- [x] 12.7 Implement ScrapingEngine.execute orchestrator with fail-safe error handling (log error, skip URL, continue)
- [x] 12.8 Implement progress publishing via Redis Pub/Sub during execution
- [x] 12.9 Write property tests for crawl queue (Property 6), 66-field extraction (Property 7), fail-safe (Property 8), selector priority (Property 10), delay range (Property 12), backoff (Property 13)

## Task 13: Task Scheduling and Execution (Req 2)

- [x] 13.1 Implement Celery task for scraping execution with Correlation_ID propagation
- [x] 13.2 Implement manual execution endpoint POST /api/v1/tasks/{config_id}/execute with concurrent execution guard
- [x] 13.3 Implement Celery Beat scheduled execution based on cron expressions from Configuracion_Scraping
- [x] 13.4 Implement task status recording (queued, running, success, partial_success, failure) with detailed counts (inserted/updated/skipped)
- [x] 13.5 Implement ENGINE start logging with config_id, sitio_origen, profundidad, and selector map version (Req 14.3)
- [x] 13.6 Write property test for concurrent execution guard (Property 5)

## Task 14: WebSocket Notifications (Req 2.7, 13.3)

- [x] 14.1 Implement FastAPI WebSocket endpoint /api/v1/ws/tasks with JWT authentication
- [x] 14.2 Implement Redis Pub/Sub listener that forwards task status changes and progress updates to connected WebSocket clients
- [x] 14.3 Implement WebSocket message types: task_status, task_progress, export_ready
- [x] 14.4 Write integration tests for WebSocket connection, message delivery, and disconnection handling

## Task 15: Dashboard API (Req 10, 13)

- [x] 15.1 Implement property search endpoint GET /api/v1/properties with combinable filters (Sitio_Origen, Tipo_Inmueble, Operacion, Municipio, Sector, Barrio, Estrato, precio range, metros range, Estado_Activo, Fecha_Control range) and pagination
- [x] 15.2 Implement property detail endpoint GET /api/v1/properties/{id} returning all 66 fields
- [x] 15.3 Implement summary endpoint GET /api/v1/summary with totals by Sitio_Origen, Operacion, active records, and last successful task timestamp
- [x] 15.4 Implement error listing endpoint GET /api/v1/errors with filters for error_type, sitio_origen, task_id, and date range
- [x] 15.5 Implement task listing endpoint GET /api/v1/tasks with filters for status, config_id, sitio_origen, and date range (Req 13.4)
- [x] 15.6 Implement task detail endpoint GET /api/v1/tasks/{task_id} with full execution summary including correlation_id

## Task 16: Export System (Req 10.3, 10.7)

- [x] 16.1 Implement synchronous export for small datasets in CSV, Excel, and JSON formats using Pandas + openpyxl
- [x] 16.2 Implement asynchronous export via Celery worker for large datasets (>100k records)
- [x] 16.3 Implement export API endpoints: POST /api/v1/exports, GET /api/v1/exports/{id}/status, GET /api/v1/exports/{id}/download
- [x] 16.4 Implement export completion notification via WebSocket (export_ready message)
- [x] 16.5 Write unit tests for export generation in each format

## Task 17: Frontend — PARAM_FRONT (Req 1, 4)

- [x] 17.1 Implement ConfigList component with paginated table showing URL, tipo_operacion, modo_ejecucion, estado_activo, and last_execution_at
- [x] 17.2 Implement ConfigForm component with Zod validation (URL, depth 1-10, cron when Programado) and React Hook Form
- [x] 17.3 Implement CronScheduleInput component with human-readable preview of cron expression
- [x] 17.4 Implement SelectorMapEditor component for creating/editing CSS selector mappings per Sitio_Origen
- [x] 17.5 Implement soft delete confirmation dialog and manual execution trigger button
- [x] 17.6 Write Vitest unit tests for form validation schemas and component rendering

## Task 18: Frontend — DASHBOARD (Req 10, 13)

- [x] 18.1 Implement FilterPanel component with all combinable filters (Sitio_Origen, Tipo_Inmueble, Operacion, Municipio, Sector, Barrio, Estrato, precio range, metros range, Estado_Activo, Fecha_Control range)
- [x] 18.2 Implement DataTable component with configurable columns and pagination
- [x] 18.3 Implement RecordDetail component showing all 66 fields
- [x] 18.4 Implement SummaryPanel component with totals by Sitio_Origen and Operacion
- [x] 18.5 Implement ErrorLogViewer component with filters for error type, Sitio_Origen, Tarea_Scraping, and date range
- [x] 18.6 Implement ExportDialog component with format selection and async progress tracking
- [x] 18.7 Implement TaskMonitorList component with paginated task list and filters (status, config, date, Sitio_Origen)
- [x] 18.8 Implement TaskMonitorDetail component with execution counts (inserted/updated/skipped) and errors by type
- [x] 18.9 Implement TaskProgressBar component with real-time WebSocket progress updates (page count, record count)
- [x] 18.10 Write Vitest unit tests for dashboard components

## Task 19: Frontend — Auth and WebSocket (Req 12, 2.7)

- [x] 19.1 Implement login page with username/password form and error handling (generic error message)
- [x] 19.2 Implement JWT token management (access token in memory, refresh via httpOnly cookie)
- [x] 19.3 Implement WebSocketProvider context that manages connection lifecycle and distributes events to subscribed components
- [x] 19.4 Implement RBAC-based UI rendering (hide/show elements based on user role)
- [x] 19.5 Implement automatic token refresh on 401 responses and session timeout handling
- [x] 19.6 Write Vitest unit tests for auth flows and WebSocket message handling
