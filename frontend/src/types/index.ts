/**
 * TypeScript types for the web scraping platform frontend.
 *
 * Mirrors backend Pydantic schemas for type-safe API communication.
 */

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export type UserRole = 'administrador' | 'operador';

export interface User {
  id: number;
  username: string;
  role: UserRole;
}

export interface TokenResponse {
  access_token: string;
  expires_in: number;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

// ---------------------------------------------------------------------------
// Configurations
// ---------------------------------------------------------------------------

export type TipoOperacion = 'Venta' | 'Arriendo';
export type ModoEjecucion = 'Manual' | 'Programado';

export interface ConfigCreate {
  url_base: string;
  profundidad_navegacion: number;
  tipo_operacion: TipoOperacion;
  modo_ejecucion: ModoEjecucion;
  cron_expression?: string | null;
}

export interface ConfigUpdate {
  url_base?: string;
  profundidad_navegacion?: number;
  tipo_operacion?: TipoOperacion;
  modo_ejecucion?: ModoEjecucion;
  cron_expression?: string | null;
}

export interface ConfigResponse {
  id: number;
  url_base: string;
  profundidad_navegacion: number;
  tipo_operacion: string;
  modo_ejecucion: string;
  cron_expression: string | null;
  cron_preview: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
  last_execution_at: string | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
}

// ---------------------------------------------------------------------------
// Selector Maps
// ---------------------------------------------------------------------------

export interface SelectorMapUpdate {
  mappings: Record<string, string[]>;
}

export interface SelectorMapResponse {
  sitio_origen: string;
  version: number;
  mappings: Record<string, string[]>;
  created_at: string;
}

// ---------------------------------------------------------------------------
// Properties (Dashboard)
// ---------------------------------------------------------------------------

export interface PropertyListItem {
  id_interno: number;
  codigo_inmueble: string;
  sitio_origen: string;
  tipo_inmueble: string | null;
  operacion: string | null;
  municipio: string | null;
  sector: string | null;
  barrio: string | null;
  estrato: number | null;
  precio_local: number | null;
  precio_usd: number | null;
  metros_utiles: number | null;
  metros_totales: number | null;
  habitaciones: number | null;
  banos: number | null;
  estado_activo: boolean | null;
  fecha_control: string | null;
  titulo_anuncio: string | null;
  url_anuncio: string | null;
}

export interface PropertyDetail extends PropertyListItem {
  estacionamiento: number | null;
  administracion_valor: number | null;
  antiguedad_detalle: string | null;
  rango_antiguedad: string | null;
  tipo_estudio: boolean | null;
  es_loft: boolean | null;
  dueno_anuncio: string | null;
  telefono_principal: string | null;
  telefono_opcional: string | null;
  correo_contacto: string | null;
  tipo_publicador: string | null;
  descripcion_anuncio: string | null;
  fecha_actualizacion: string | null;
  amoblado: boolean | null;
  orientacion: string | null;
  latitud: number | null;
  longitud: number | null;
  url_imagen_principal: string | null;
  fecha_publicacion: string | null;
  direccion: string | null;
  fecha_desactivacion: string | null;
  simbolo_moneda: string | null;
  piso_propiedad: number | null;
  tiene_ascensores: boolean | null;
  tiene_balcones: boolean | null;
  tiene_seguridad: boolean | null;
  tiene_bodega_deposito: boolean | null;
  tiene_terraza: boolean | null;
  cuarto_servicio: boolean | null;
  bano_servicio: boolean | null;
  tiene_calefaccion: boolean | null;
  tiene_alarma: boolean | null;
  acceso_controlado: boolean | null;
  circuito_cerrado: boolean | null;
  estacionamiento_visita: boolean | null;
  cocina_americana: boolean | null;
  tiene_gimnasio: boolean | null;
  tiene_bbq: boolean | null;
  tiene_piscina: boolean | null;
  en_conjunto_residencial: boolean | null;
  uso_comercial: boolean | null;
  cambio_precio_valor: number | null;
  precio_bajo: boolean | null;
  tipo_empresa: string | null;
  glosa_administracion: string | null;
  area_privada: number | null;
  area_construida: number | null;
}

// ---------------------------------------------------------------------------
// Summary
// ---------------------------------------------------------------------------

export interface CountByField {
  value: string;
  count: number;
}

export interface SummaryResponse {
  total_active: number;
  by_sitio_origen: CountByField[];
  by_operacion: CountByField[];
  last_successful_task: string | null;
}

// ---------------------------------------------------------------------------
// Errors
// ---------------------------------------------------------------------------

export type ErrorType = 'Timeout' | 'CAPTCHA' | 'Estructura' | 'Conexion';

export interface ErrorListItem {
  id: number;
  task_id: string;
  sitio_origen: string;
  url: string | null;
  error_type: string;
  error_message: string | null;
  error_metadata: Record<string, unknown> | null;
  correlation_id: string | null;
  created_at: string;
}

// ---------------------------------------------------------------------------
// Tasks
// ---------------------------------------------------------------------------

export type TaskStatus = 'queued' | 'running' | 'success' | 'partial_success' | 'failure';

export interface TaskListItem {
  task_id: string;
  config_id: number;
  status: string;
  started_at: string | null;
  ended_at: string | null;
  duration_seconds: number | null;
  pages_processed: number;
  records_extracted: number;
  records_inserted: number;
  records_updated: number;
  records_skipped: number;
  correlation_id: string | null;
}

export interface TaskDetail extends TaskListItem {
  errors_by_type: Record<string, number> | null;
}

// ---------------------------------------------------------------------------
// Exports
// ---------------------------------------------------------------------------

export type ExportFormat = 'csv' | 'excel' | 'json';

export interface ExportRequest {
  format: ExportFormat;
  filters?: Record<string, unknown> | null;
}

export interface ExportCreateResponse {
  export_id: string;
  status: string;
}

export interface ExportStatusResponse {
  export_id: string;
  status: string;
  record_count: number;
}

// ---------------------------------------------------------------------------
// WebSocket
// ---------------------------------------------------------------------------

export type WsMessageType = 'task_status' | 'task_progress' | 'export_ready';

export interface WsMessage {
  type: WsMessageType;
  payload: Record<string, unknown>;
}

// ---------------------------------------------------------------------------
// Filters
// ---------------------------------------------------------------------------

export interface PropertyFilters {
  sitio_origen?: string;
  tipo_inmueble?: string;
  operacion?: string;
  municipio?: string;
  sector?: string;
  barrio?: string;
  estrato?: number;
  precio_min?: number;
  precio_max?: number;
  metros_min?: number;
  metros_max?: number;
  estado_activo?: boolean;
  fecha_control_desde?: string;
  fecha_control_hasta?: string;
}

export interface ErrorFilters {
  error_type?: string;
  sitio_origen?: string;
  task_id?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
}

export interface TaskFilters {
  status?: string;
  config_id?: number;
  sitio_origen?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
}
