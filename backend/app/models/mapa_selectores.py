"""SQLAlchemy model for MAPA_SELECTORES table."""

from datetime import datetime

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MapaSelectores(Base):
    """Selector map model for CSS selectors per site.

    Stores versioned CSS selector mappings as JSONB for each sitio_origen.
    Index: idx_mapa_sitio_version ON (sitio_origen, version DESC)
    """

    __tablename__ = "mapa_selectores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sitio_origen: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    mappings: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )
