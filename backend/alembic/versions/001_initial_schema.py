"""Initial schema - all tables and indexes.

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables and indexes."""

    # --- USUARIO ---
    op.create_table(
        "usuario",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )

    # --- CONFIGURACION_SCRAPING ---
    op.create_table(
        "configuracion_scraping",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("url_base", sa.String(length=2048), nullable=False),
        sa.Column("profundidad_navegacion", sa.Integer(), nullable=False),
        sa.Column("tipo_operacion", sa.String(length=50), nullable=False),
        sa.Column("modo_ejecucion", sa.String(length=50), nullable=False),
        sa.Column("cron_expression", sa.String(length=100), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("last_execution_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- MAPA_SELECTORES ---
    op.create_table(
        "mapa_selectores",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("sitio_origen", sa.String(length=255), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("mappings", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- TAREA_SCRAPING ---
    op.create_table(
        "tarea_scraping",
        sa.Column(
            "task_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("config_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("correlation_id", sa.String(length=100), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("pages_processed", sa.Integer(), nullable=False),
        sa.Column("records_extracted", sa.Integer(), nullable=False),
        sa.Column("records_inserted", sa.Integer(), nullable=False),
        sa.Column("records_updated", sa.Integer(), nullable=False),
        sa.Column("records_skipped", sa.Integer(), nullable=False),
        sa.Column(
            "errors_by_type",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["config_id"], ["configuracion_scraping.id"]),
        sa.PrimaryKeyConstraint("task_id"),
    )

    # --- ESQUEMA_INMUEBLE ---
    op.create_table(
        "esquema_inmueble",
        sa.Column(
            "id_interno", sa.BigInteger(), autoincrement=True, nullable=False
        ),
        sa.Column("codigo_inmueble", sa.String(length=100), nullable=False),
        sa.Column("sitio_origen", sa.String(length=255), nullable=False),
        sa.Column("tipo_inmueble", sa.String(length=100), nullable=True),
        sa.Column("habitaciones", sa.Integer(), nullable=True),
        sa.Column("banos", sa.Integer(), nullable=True),
        sa.Column("operacion", sa.String(length=50), nullable=True),
        sa.Column("estacionamiento", sa.Integer(), nullable=True),
        sa.Column("administracion_valor", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("antiguedad_detalle", sa.String(length=255), nullable=True),
        sa.Column("rango_antiguedad", sa.String(length=100), nullable=True),
        sa.Column("tipo_estudio", sa.Boolean(), nullable=True),
        sa.Column("es_loft", sa.Boolean(), nullable=True),
        sa.Column("dueno_anuncio", sa.String(length=255), nullable=True),
        sa.Column("telefono_principal", sa.String(length=50), nullable=True),
        sa.Column("telefono_opcional", sa.String(length=50), nullable=True),
        sa.Column("correo_contacto", sa.String(length=255), nullable=True),
        sa.Column("tipo_publicador", sa.String(length=100), nullable=True),
        sa.Column("descripcion_anuncio", sa.Text(), nullable=True),
        sa.Column("fecha_control", sa.DateTime(), nullable=True),
        sa.Column("fecha_actualizacion", sa.DateTime(), nullable=True),
        sa.Column("municipio", sa.String(length=255), nullable=True),
        sa.Column("amoblado", sa.Boolean(), nullable=True),
        sa.Column("titulo_anuncio", sa.String(length=500), nullable=True),
        sa.Column("metros_utiles", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("metros_totales", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("orientacion", sa.String(length=50), nullable=True),
        sa.Column("latitud", sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column("longitud", sa.Numeric(precision=11, scale=7), nullable=True),
        sa.Column("url_anuncio", sa.String(length=2048), nullable=True),
        sa.Column("url_imagen_principal", sa.String(length=2048), nullable=True),
        sa.Column("sector", sa.String(length=255), nullable=True),
        sa.Column("barrio", sa.String(length=255), nullable=True),
        sa.Column("estrato", sa.Integer(), nullable=True),
        sa.Column("fecha_publicacion", sa.DateTime(), nullable=True),
        sa.Column("direccion", sa.String(length=500), nullable=True),
        sa.Column("estado_activo", sa.Boolean(), nullable=True),
        sa.Column("fecha_desactivacion", sa.DateTime(), nullable=True),
        sa.Column("precio_usd", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("precio_local", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("simbolo_moneda", sa.String(length=10), nullable=True),
        sa.Column("piso_propiedad", sa.Integer(), nullable=True),
        sa.Column("tiene_ascensores", sa.Boolean(), nullable=True),
        sa.Column("tiene_balcones", sa.Boolean(), nullable=True),
        sa.Column("tiene_seguridad", sa.Boolean(), nullable=True),
        sa.Column("tiene_bodega_deposito", sa.Boolean(), nullable=True),
        sa.Column("tiene_terraza", sa.Boolean(), nullable=True),
        sa.Column("cuarto_servicio", sa.Boolean(), nullable=True),
        sa.Column("bano_servicio", sa.Boolean(), nullable=True),
        sa.Column("tiene_calefaccion", sa.Boolean(), nullable=True),
        sa.Column("tiene_alarma", sa.Boolean(), nullable=True),
        sa.Column("acceso_controlado", sa.Boolean(), nullable=True),
        sa.Column("circuito_cerrado", sa.Boolean(), nullable=True),
        sa.Column("estacionamiento_visita", sa.Boolean(), nullable=True),
        sa.Column("cocina_americana", sa.Boolean(), nullable=True),
        sa.Column("tiene_gimnasio", sa.Boolean(), nullable=True),
        sa.Column("tiene_bbq", sa.Boolean(), nullable=True),
        sa.Column("tiene_piscina", sa.Boolean(), nullable=True),
        sa.Column("en_conjunto_residencial", sa.Boolean(), nullable=True),
        sa.Column("uso_comercial", sa.Boolean(), nullable=True),
        sa.Column("cambio_precio_valor", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("precio_bajo", sa.Boolean(), nullable=True),
        sa.Column("tipo_empresa", sa.String(length=100), nullable=True),
        sa.Column("glosa_administracion", sa.String(length=255), nullable=True),
        sa.Column("area_privada", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("area_construida", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.PrimaryKeyConstraint("id_interno"),
        sa.UniqueConstraint("codigo_inmueble", "sitio_origen", name="uq_clave_upsert"),
    )

    # --- LOG_ERROR ---
    op.create_table(
        "log_error",
        sa.Column(
            "id", sa.BigInteger(), autoincrement=True, nullable=False
        ),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sitio_origen", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=True),
        sa.Column("error_type", sa.String(length=50), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "error_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("correlation_id", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["tarea_scraping.task_id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- EXPORTACION ---
    op.create_table(
        "exportacion",
        sa.Column(
            "export_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("format", sa.String(length=20), nullable=False),
        sa.Column(
            "filters", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("record_count", sa.Integer(), nullable=False),
        sa.Column("file_path", sa.String(length=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["usuario.id"]),
        sa.PrimaryKeyConstraint("export_id"),
    )

    # ===== INDEXES =====

    # --- ESQUEMA_INMUEBLE indexes ---
    op.create_index(
        "idx_inmueble_sitio_origen",
        "esquema_inmueble",
        ["sitio_origen"],
    )
    op.create_index(
        "idx_inmueble_operacion",
        "esquema_inmueble",
        ["operacion"],
    )
    op.create_index(
        "idx_inmueble_tipo",
        "esquema_inmueble",
        ["tipo_inmueble"],
    )
    op.create_index(
        "idx_inmueble_municipio",
        "esquema_inmueble",
        ["municipio"],
    )
    op.create_index(
        "idx_inmueble_precio_local",
        "esquema_inmueble",
        ["precio_local"],
    )
    op.create_index(
        "idx_inmueble_estado_activo",
        "esquema_inmueble",
        ["estado_activo"],
    )
    op.create_index(
        "idx_inmueble_fecha_control",
        "esquema_inmueble",
        ["fecha_control"],
    )
    # Partial index for active properties
    op.create_index(
        "idx_inmueble_activos",
        "esquema_inmueble",
        ["sitio_origen", "operacion"],
        postgresql_where=sa.text("estado_activo = true"),
    )

    # --- LOG_ERROR indexes ---
    op.create_index("idx_error_task", "log_error", ["task_id"])
    op.create_index("idx_error_type", "log_error", ["error_type"])
    op.create_index("idx_error_sitio", "log_error", ["sitio_origen"])
    op.create_index("idx_error_created", "log_error", ["created_at"])
    op.create_index("idx_error_correlation", "log_error", ["correlation_id"])

    # --- TAREA_SCRAPING indexes ---
    op.create_index("idx_tarea_status", "tarea_scraping", ["status"])
    op.create_index("idx_tarea_config", "tarea_scraping", ["config_id"])
    op.create_index("idx_tarea_started", "tarea_scraping", ["started_at"])
    op.create_index("idx_tarea_correlation", "tarea_scraping", ["correlation_id"])

    # --- MAPA_SELECTORES index ---
    op.create_index(
        "idx_mapa_sitio_version",
        "mapa_selectores",
        [sa.text("sitio_origen"), sa.text("version DESC")],
    )


def downgrade() -> None:
    """Drop all tables and indexes (reverse order)."""

    # Drop indexes first
    op.drop_index("idx_mapa_sitio_version", table_name="mapa_selectores")
    op.drop_index("idx_tarea_correlation", table_name="tarea_scraping")
    op.drop_index("idx_tarea_started", table_name="tarea_scraping")
    op.drop_index("idx_tarea_config", table_name="tarea_scraping")
    op.drop_index("idx_tarea_status", table_name="tarea_scraping")
    op.drop_index("idx_error_correlation", table_name="log_error")
    op.drop_index("idx_error_created", table_name="log_error")
    op.drop_index("idx_error_sitio", table_name="log_error")
    op.drop_index("idx_error_type", table_name="log_error")
    op.drop_index("idx_error_task", table_name="log_error")
    op.drop_index("idx_inmueble_activos", table_name="esquema_inmueble")
    op.drop_index("idx_inmueble_fecha_control", table_name="esquema_inmueble")
    op.drop_index("idx_inmueble_estado_activo", table_name="esquema_inmueble")
    op.drop_index("idx_inmueble_precio_local", table_name="esquema_inmueble")
    op.drop_index("idx_inmueble_municipio", table_name="esquema_inmueble")
    op.drop_index("idx_inmueble_tipo", table_name="esquema_inmueble")
    op.drop_index("idx_inmueble_operacion", table_name="esquema_inmueble")
    op.drop_index("idx_inmueble_sitio_origen", table_name="esquema_inmueble")

    # Drop tables (reverse dependency order)
    op.drop_table("exportacion")
    op.drop_table("log_error")
    op.drop_table("esquema_inmueble")
    op.drop_table("tarea_scraping")
    op.drop_table("mapa_selectores")
    op.drop_table("configuracion_scraping")
    op.drop_table("usuario")
