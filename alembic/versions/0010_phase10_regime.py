"""Phase 10 regime definitions.\n\nRevision ID: 0010_phase10\nRevises: 0009_phase9\n"""
from pathlib import Path
from alembic import op
revision = "0010_phase10"
down_revision = "0009_phase9"
branch_labels = None
depends_on = None
SQL = Path(__file__).resolve().parents[2] / "sql" / "010_phase10_regime.sql"
def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(SQL.read_text(encoding="utf-8"))
def downgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DELETE FROM ops.schema_gate WHERE phase='phase10'")
