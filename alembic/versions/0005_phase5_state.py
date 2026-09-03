"""Phase 5 current-state / regime contracts.

Revision ID: 0005_phase5
Revises: 0004_phase4
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0005_phase5"
down_revision = "0004_phase4"
branch_labels = None
depends_on = None

SQL = Path(__file__).resolve().parents[2] / "sql" / "005_phase5_state.sql"


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute(SQL.read_text(encoding="utf-8"))


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("DELETE FROM ops.schema_gate WHERE phase = 'phase5'")
