"""Add include_patterns and exclude_patterns to configuracion_scraping.

Revision ID: 002_add_url_patterns
Revises: 001_initial_schema
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = "002_add_url_patterns"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add include_patterns and exclude_patterns columns."""
    op.add_column(
        "configuracion_scraping",
        sa.Column("include_patterns", JSONB, nullable=True),
    )
    op.add_column(
        "configuracion_scraping",
        sa.Column("exclude_patterns", JSONB, nullable=True),
    )


def downgrade() -> None:
    """Remove include_patterns and exclude_patterns columns."""
    op.drop_column("configuracion_scraping", "exclude_patterns")
    op.drop_column("configuracion_scraping", "include_patterns")
