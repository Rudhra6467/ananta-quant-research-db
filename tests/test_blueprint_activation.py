from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BP = (ROOT / "docs" / "MASTER_BLUEPRINT.md").read_text(encoding="utf-8")


def test_blueprint_current_command_is_activation_not_phase8() -> None:
    assert "0871b49" in BP
    assert "Do not add fixture phases" in BP
    assert "Next code = P8 slice only" not in BP
    assert "INGESTION_ENABLED=false" in BP


def test_activation_gate_docs_exist() -> None:
    for name in (
        "GATE_A_INGESTION_DESIGN.md",
        "GATE_B_LABORATORY_DESIGN.md",
        "GATE_C_SHIFT_DESIGN.md",
        "GATE_D_AGENT_DESIGN.md",
        "GATE_E_PAPER_DESIGN.md",
        "GATE_F_SCALEOUT_DESIGN.md",
    ):
        assert (ROOT / "docs" / name).is_file()


def test_no_phase_21() -> None:
    assert list((ROOT / "sql").glob("021*")) == []
