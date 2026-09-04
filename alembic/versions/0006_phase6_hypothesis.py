"""Phase 6 hypothesis lifecycle contracts.

Revision ID: 0006_phase6
Revises: 0005_phase5
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0006_phase6"
down_revision = "0005_phase5"
branch_labels = None
depends_on = None

SQL = Path(__file__).resolve().parents[2] / "sql" / "006_phase6_hypothesis.sql"


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute(SQL.read_text(encoding="utf-8"))


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("DELETE FROM ops.schema_gate WHERE phase = 'phase6'")
