from pathlib import Path
from alembic import op
revision = "0019_phase19"
down_revision = "0018_phase18"
branch_labels = None
depends_on = None
SQL = Path(__file__).resolve().parents[2] / "sql" / "019_phase19_expansion.sql"
def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(SQL.read_text(encoding="utf-8"))
def downgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DELETE FROM ops.schema_gate WHERE phase='phase19'")
