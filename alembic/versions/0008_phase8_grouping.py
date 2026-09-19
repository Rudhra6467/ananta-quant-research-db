"""Phase 8 grouping contracts.

Revision ID: 0008_phase8
Revises: 0007_phase7
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0008_phase8"
down_revision = "0007_phase7"
branch_labels = None
depends_on = None

SQL = Path(__file__).resolve().parents[2] / "sql" / "008_phase8_grouping.sql"


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute(SQL.read_text(encoding="utf-8"))


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("DELETE FROM ops.schema_gate WHERE phase = 'phase8'")
