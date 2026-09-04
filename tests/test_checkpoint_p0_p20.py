from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_no_phase_21_invented() -> None:
    sql = list((ROOT / "sql").glob("021*")) + list((ROOT / "sql").glob("*phase21*"))
    alembic = list((ROOT / "alembic" / "versions").glob("0021*"))
    assert sql == []
    assert alembic == []


def test_checkpoint_documents_exist() -> None:
    text = (ROOT / "docs" / "CHECKPOINT_P0_P20.md").read_text()
    assert "0871b49" in text
    assert "No live ingestion" in text
    program = (ROOT / "docs" / "ACTIVATION_PROGRAM.md").read_text()
    assert "INGESTION_ENABLED=false" in program
    assert "Phase 21+" in program
    const = (ROOT / "docs" / "DATABASE_CONSTITUTION.md").read_text()
    assert "0871b49" in const


def test_constitution_conflict_rule_present() -> None:
    const = (ROOT / "docs" / "DATABASE_CONSTITUTION.md").read_text()
    assert "Do not rewrite the constitution" in const
