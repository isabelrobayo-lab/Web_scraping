"""SQLAlchemy model for ESQUEMA_INMUEBLE table with all 66 fields."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EsquemaInmueble(Base):
    """Real estate property model with 66 fields.

    Unique constraint: uq_clave_upsert ON (codigo_inmueble, sitio_origen)
    Used for UPSERT operations via ON CONFLICT.
    """

    __tablename__ = "esquema_inmueble"
    __table_args__ = (
        UniqueConstraint(
            "codigo_inmueble", "sitio_origen", name="uq_clave_upsert"
        ),
    )

    # Primary key
    id_interno: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )

    # Identification fields
    codigo_inmueble: Mapped[str] = mapped_column(String(100), nullable=False)
    sitio_origen: Mapped[str] = mapped_column(String(255), nullable=False)

    # Property characteristics
    tipo_inmueble: Mapped[str | None] = mapped_column(String(100), nullable=True)
    habitaciones: Mapped[int | None] = mapped_column(Integer, nullable=True)
    banos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    operacion: Mapped[str | None] = mapped_column(String(50), nullable=True)
    estacionamiento: Mapped[int | None] = mapped_column(Integer, nullable=True)
    administracion_valor: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    antiguedad_detalle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rango_antiguedad: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Boolean characteristics
    tipo_estudio: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    es_loft: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Contact information
    dueno_anuncio: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefono_principal: Mapped[str | None] = mapped_column(String(50), nullable=True)
    telefono_opcional: Mapped[str | None] = mapped_column(String(50), nullable=True)
    correo_contacto: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tipo_publicador: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Description
    descripcion_anuncio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Dates
    fecha_control: Mapped[datetime | None] = mapped_column(nullable=True)
    fecha_actualizacion: Mapped[datetime | None] = mapped_column(nullable=True)

    # Location
    municipio: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # More characteristics
    amoblado: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    titulo_anuncio: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Measurements
    metros_utiles: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    metros_totales: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )

    # Orientation and coordinates
    orientacion: Mapped[str | None] = mapped_column(String(50), nullable=True)
    latitud: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitud: Mapped[Decimal | None] = mapped_column(Numeric(11, 7), nullable=True)

    # URLs
    url_anuncio: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    url_imagen_principal: Mapped[str | None] = mapped_column(
        String(2048), nullable=True
    )

    # Location details
    sector: Mapped[str | None] = mapped_column(String(255), nullable=True)
    barrio: Mapped[str | None] = mapped_column(String(255), nullable=True)
    estrato: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Publication date
    fecha_publicacion: Mapped[datetime | None] = mapped_column(nullable=True)

    # Address and status
    direccion: Mapped[str | None] = mapped_column(String(500), nullable=True)
    estado_activo: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, default=True
    )
    fecha_desactivacion: Mapped[datetime | None] = mapped_column(nullable=True)

    # Pricing
    precio_usd: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    precio_local: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    simbolo_moneda: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Building details
    piso_propiedad: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Amenities (boolean fields)
    tiene_ascensores: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    tiene_balcones: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    tiene_seguridad: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    tiene_bodega_deposito: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    tiene_terraza: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    cuarto_servicio: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    bano_servicio: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    tiene_calefaccion: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    tiene_alarma: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    acceso_controlado: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    circuito_cerrado: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    estacionamiento_visita: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    cocina_americana: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    tiene_gimnasio: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    tiene_bbq: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    tiene_piscina: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    en_conjunto_residencial: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )
    uso_comercial: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Price change tracking
    cambio_precio_valor: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    precio_bajo: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Additional fields
    tipo_empresa: Mapped[str | None] = mapped_column(String(100), nullable=True)
    glosa_administracion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    area_privada: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    area_construida: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
