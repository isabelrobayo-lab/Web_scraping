"""Add selector_status to configuracion_scraping.

Revision ID: 003_add_selector_status
Revises: 002_add_url_patterns
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa

revision = "003_add_selector_status"
down_revision = "002_add_url_patterns"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add selector_status column with default 'ready' for existing rows."""
    op.add_column(
        "configuracion_scraping",
        sa.Column("selector_status", sa.String(20), nullable=False, server_default="ready"),
    )


def downgrade() -> None:
    """Remove selector_status column."""
    op.drop_column("configuracion_scraping", "selector_status")
