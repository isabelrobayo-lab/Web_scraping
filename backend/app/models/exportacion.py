"""SQLAlchemy model for EXPORTACION table."""

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Exportacion(Base):
    """Data export model.

    Status values: processing, ready, failed
    Format values: csv, excel, json
    """

    __tablename__ = "exportacion"

    export_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("usuario.id"), nullable=False
    )
    format: Mapped[str] = mapped_column(String(20), nullable=False)
    filters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="processing"
    )
    record_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
