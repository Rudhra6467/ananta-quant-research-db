"""Phase 11 event representation."""
from pathlib import Path
from alembic import op
revision = "0011_phase11"
down_revision = "0010_phase10"
branch_labels = None
depends_on = None
SQL = Path(__file__).resolve().parents[2] / "sql" / "011_phase11_events.sql"
def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(SQL.read_text(encoding="utf-8"))
def downgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DELETE FROM ops.schema_gate WHERE phase='phase11'")
