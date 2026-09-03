"""Phase 2 market-truth tables.

Revision ID: 0002_phase2
Revises: 0001_phase0
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0002_phase2"
down_revision = "0001_phase0"
branch_labels = None
depends_on = None

SQL = Path(__file__).resolve().parents[2] / "sql" / "002_phase2_market_truth.sql"
CONTRACTS = Path(__file__).resolve().parents[2] / "sql" / "002b_foundation_contracts.sql"


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute(SQL.read_text(encoding="utf-8"))
    op.execute(CONTRACTS.read_text(encoding="utf-8"))


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("DROP TABLE IF EXISTS feature.observation CASCADE")
    op.execute("DROP TABLE IF EXISTS market.ohlcv_bar CASCADE")
    op.execute("DROP TABLE IF EXISTS raw.market_event CASCADE")
    op.execute("DROP TABLE IF EXISTS research.parameter_region_member CASCADE")
    op.execute("DROP TABLE IF EXISTS research.parameter_region CASCADE")
    op.execute("DROP TABLE IF EXISTS research.combination_request CASCADE")
    op.execute("DROP TABLE IF EXISTS ops.persist_watermark CASCADE")
