"""Pydantic schemas for Dashboard API responses.

Covers properties, summary, errors, and tasks endpoints.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------


class PropertyListItem(BaseModel):
    """Lightweight property item for paginated list."""

    model_config = ConfigDict(from_attributes=True)

    id_interno: int
    codigo_inmueble: str
    sitio_origen: str
    tipo_inmueble: str | None = None
    operacion: str | None = None
    municipio: str | None = None
    sector: str | None = None
    barrio: str | None = None
    estrato: int | None = None
    precio_local: Decimal | None = None
    precio_usd: Decimal | None = None
    metros_utiles: Decimal | None = None
    metros_totales: Decimal | None = None
    habitaciones: int | None = None
    banos: int | None = None
    estado_activo: bool | None = None
    fecha_control: datetime | None = None
    titulo_anuncio: str | None = None
    url_anuncio: str | None = None


class PropertyDetail(BaseModel):
    """Full 66-field property detail."""

    model_config = ConfigDict(from_attributes=True)

    id_interno: int
    codigo_inmueble: str
    sitio_origen: str
    tipo_inmueble: str | None = None
    habitaciones: int | None = None
    banos: int | None = None
    operacion: str | None = None
    estacionamiento: int | None = None
    administracion_valor: Decimal | None = None
    antiguedad_detalle: str | None = None
    rango_antiguedad: str | None = None
    tipo_estudio: bool | None = None
    es_loft: bool | None = None
    dueno_anuncio: str | None = None
    telefono_principal: str | None = None
    telefono_opcional: str | None = None
    correo_contacto: str | None = None
    tipo_publicador: str | None = None
    descripcion_anuncio: str | None = None
    fecha_control: datetime | None = None
    fecha_actualizacion: datetime | None = None
    municipio: str | None = None
    amoblado: bool | None = None
    titulo_anuncio: str | None = None
    metros_utiles: Decimal | None = None
    metros_totales: Decimal | None = None
    orientacion: str | None = None
    latitud: Decimal | None = None
    longitud: Decimal | None = None
    url_anuncio: str | None = None
    url_imagen_principal: str | None = None
    sector: str | None = None
    barrio: str | None = None
    estrato: int | None = None
    fecha_publicacion: datetime | None = None
    direccion: str | None = None
    estado_activo: bool | None = None
    fecha_desactivacion: datetime | None = None
    precio_usd: Decimal | None = None
    precio_local: Decimal | None = None
    simbolo_moneda: str | None = None
    piso_propiedad: int | None = None
    tiene_ascensores: bool | None = None
    tiene_balcones: bool | None = None
    tiene_seguridad: bool | None = None
    tiene_bodega_deposito: bool | None = None
    tiene_terraza: bool | None = None
    cuarto_servicio: bool | None = None
    bano_servicio: bool | None = None
    tiene_calefaccion: bool | None = None
    tiene_alarma: bool | None = None
    acceso_controlado: bool | None = None
    circuito_cerrado: bool | None = None
    estacionamiento_visita: bool | None = None
    cocina_americana: bool | None = None
    tiene_gimnasio: bool | None = None
    tiene_bbq: bool | None = None
    tiene_piscina: bool | None = None
    en_conjunto_residencial: bool | None = None
    uso_comercial: bool | None = None
    cambio_precio_valor: Decimal | None = None
    precio_bajo: bool | None = None
    tipo_empresa: str | None = None
    glosa_administracion: str | None = None
    area_privada: Decimal | None = None
    area_construida: Decimal | None = None


class PaginatedPropertyResponse(BaseModel):
    """Paginated list of properties."""

    items: list[PropertyListItem]
    total: int
    page: int
    pages: int


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


class CountByField(BaseModel):
    """Count grouped by a field value."""

    value: str
    count: int


class SummaryResponse(BaseModel):
    """Dashboard summary with totals."""

    total_active: int
    by_sitio_origen: list[CountByField]
    by_operacion: list[CountByField]
    last_successful_task: datetime | None = None


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ErrorListItem(BaseModel):
    """Error log entry for listing."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: str
    sitio_origen: str
    url: str | None = None
    error_type: str
    error_message: str | None = None
    error_metadata: dict[str, Any] | None = None
    correlation_id: str | None = None
    created_at: datetime


class PaginatedErrorResponse(BaseModel):
    """Paginated list of errors."""

    items: list[ErrorListItem]
    total: int
    page: int
    pages: int


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------


class TaskListItem(BaseModel):
    """Task entry for listing."""

    model_config = ConfigDict(from_attributes=True)

    task_id: str
    config_id: int
    status: str
    started_at: datetime | None = None
    ended_at: datetime | None = None
    duration_seconds: float | None = None
    pages_processed: int
    records_extracted: int
    records_inserted: int
    records_updated: int
    records_skipped: int
    correlation_id: str | None = None


class PaginatedTaskResponse(BaseModel):
    """Paginated list of tasks."""

    items: list[TaskListItem]
    total: int
    page: int
    pages: int


class TaskDetail(BaseModel):
    """Full task execution summary."""

    model_config = ConfigDict(from_attributes=True)

    task_id: str
    config_id: int
    status: str
    started_at: datetime | None = None
    ended_at: datetime | None = None
    duration_seconds: float | None = None
    pages_processed: int
    records_extracted: int
    records_inserted: int
    records_updated: int
    records_skipped: int
    errors_by_type: dict[str, int] | None = None
    correlation_id: str | None = None


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------


class ExportRequest(BaseModel):
    """Request body for creating an export."""

    format: str  # csv, excel, json
    filters: dict[str, Any] | None = None


class ExportStatusResponse(BaseModel):
    """Export status response."""

    export_id: str
    status: str
    record_count: int


class ExportCreateResponse(BaseModel):
    """Response after creating an export."""

    export_id: str
    status: str
