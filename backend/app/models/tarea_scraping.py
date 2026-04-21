"""SQLAlchemy model for TAREA_SCRAPING table."""

import uuid
from datetime import datetime

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TareaScraping(Base):
    """Scraping task execution model.

    Tracks execution status, timing, and result counts.
    Status values: queued, running, success, partial_success, failure
    """

    __tablename__ = "tarea_scraping"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    config_id: Mapped[int] = mapped_column(
        ForeignKey("configuracion_scraping.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued")
    correlation_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    pages_processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_extracted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_inserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_skipped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    errors_by_type: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    configuracion: Mapped["ConfiguracionScraping"] = relationship(  # noqa: F821
        back_populates="tareas"
    )
    errores: Mapped[list["LogError"]] = relationship(  # noqa: F821
        back_populates="tarea", lazy="selectin"
    )
