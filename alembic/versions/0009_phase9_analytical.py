"""Phase 9 analytical feature gate.\n\nRevision ID: 0009_phase9\nRevises: 0008_phase8\n"""
from pathlib import Path
from alembic import op
revision = "0009_phase9"
down_revision = "0008_phase8"
branch_labels = None
depends_on = None
SQL = Path(__file__).resolve().parents[2] / "sql" / "009_phase9_analytical.sql"
def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(SQL.read_text(encoding="utf-8"))
def downgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DELETE FROM ops.schema_gate WHERE phase='phase9'")
