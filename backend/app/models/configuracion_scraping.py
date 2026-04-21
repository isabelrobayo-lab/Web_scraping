"""SQLAlchemy model for CONFIGURACION_SCRAPING table."""

from datetime import datetime

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ConfiguracionScraping(Base):
    """Scraping configuration model.

    Defines URL, depth, operation type, execution mode, and cron schedule.
    """

    __tablename__ = "configuracion_scraping"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url_base: Mapped[str] = mapped_column(String(2048), nullable=False)
    profundidad_navegacion: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )
    tipo_operacion: Mapped[str] = mapped_column(String(50), nullable=False)
    modo_ejecucion: Mapped[str] = mapped_column(String(50), nullable=False)
    cron_expression: Mapped[str | None] = mapped_column(String(100), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_execution_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Relationships
    tareas: Mapped[list["TareaScraping"]] = relationship(  # noqa: F821
        back_populates="configuracion", lazy="selectin"
    )
