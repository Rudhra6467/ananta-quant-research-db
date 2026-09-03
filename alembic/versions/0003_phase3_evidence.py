"""Phase 3 fixture evidence contracts.

Revision ID: 0003_phase3
Revises: 0002_phase2
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0003_phase3"
down_revision = "0002_phase2"
branch_labels = None
depends_on = None

SQL = Path(__file__).resolve().parents[2] / "sql" / "003_phase3_evidence.sql"


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute(SQL.read_text(encoding="utf-8"))


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("DELETE FROM ops.schema_gate WHERE phase = 'phase3'")
