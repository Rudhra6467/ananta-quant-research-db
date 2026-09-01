"""Phase 0 foundation schemas and stubs.

Revision ID: 0001_phase0
Revises:
Create Date: 2026-09-01
"""

from __future__ import annotations

from alembic import op

from research_db.models.base import SCHEMAS, metadata

revision = "0001_phase0"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    for schema in SCHEMAS:
        op.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    bind = op.get_bind()
    metadata.create_all(bind=bind)
    op.execute(
        """
        INSERT INTO research.validation_stage (id, code, sort_order)
        VALUES
          (gen_random_uuid(), 'HISTORICAL', 1),
          (gen_random_uuid(), 'OOS', 2),
          (gen_random_uuid(), 'FORWARD', 3),
          (gen_random_uuid(), 'PAPER', 4),
          (gen_random_uuid(), 'CURRENT', 5)
        ON CONFLICT (code) DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
        VALUES (
          gen_random_uuid(),
          'phase0',
          true,
          false,
          'Foundation approved. Full market ingestion remains forbidden.'
        )
        ON CONFLICT (phase) DO NOTHING
        """
    )


def downgrade() -> None:
    bind = op.get_bind()
    metadata.drop_all(bind=bind)
    for schema in reversed(SCHEMAS):
        op.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
