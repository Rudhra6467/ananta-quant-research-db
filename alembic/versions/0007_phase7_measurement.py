"""Phase 7 measurement contracts.

Revision ID: 0007_phase7
Revises: 0006_phase6
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0007_phase7"
down_revision = "0006_phase6"
branch_labels = None
depends_on = None

SQL = Path(__file__).resolve().parents[2] / "sql" / "007_phase7_measurement.sql"


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute(SQL.read_text(encoding="utf-8"))


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("DELETE FROM ops.schema_gate WHERE phase = 'phase7'")
