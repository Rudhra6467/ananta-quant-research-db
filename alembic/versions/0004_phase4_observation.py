"""Phase 4 observation-engine contracts.

Revision ID: 0004_phase4
Revises: 0003_phase3
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0004_phase4"
down_revision = "0003_phase3"
branch_labels = None
depends_on = None

SQL = Path(__file__).resolve().parents[2] / "sql" / "004_phase4_observation.sql"


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute(SQL.read_text(encoding="utf-8"))


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("DELETE FROM ops.schema_gate WHERE phase = 'phase4'")
