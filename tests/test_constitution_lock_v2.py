from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONST = (ROOT / "docs" / "DATABASE_CONSTITUTION.md").read_text(encoding="utf-8")
LOCK = (ROOT / "docs" / "ARCHITECTURE_LOCK_V2.md").read_text(encoding="utf-8")


def test_constitution_locks_lineage_and_cohort() -> None:
    assert "ops.lineage_edge" in CONST
    assert "Conditional empirical knowledge" in CONST
    assert "Cartesian" in CONST or "cube" in CONST.lower()


def test_constitution_locks_grouping() -> None:
    assert "Hierarchical / group reasoning" in CONST
    assert "many-to-many" in CONST.lower()
    assert "time-dependent knowledge" in CONST


def test_prediction_and_uncertainty_invariants() -> None:
    assert "Prediction value ≠ uncertainty ≠ reliability ≠ ranking" in CONST
    for token in (
        "UNKNOWN",
        "INSUFFICIENT_EVIDENCE",
        "HIGH_UNCERTAINTY",
        "OUT_OF_DISTRIBUTION",
        "MODEL_DISAGREEMENT",
    ):
        assert token in CONST


def test_scenario_kinds_separated() -> None:
    for kind in ("REALIZED HISTORY", "HISTORICAL REPLAY", "COUNTERFACTUAL", "SYNTHETIC SIMULATION"):
        assert kind in CONST


def test_phase5_not_expanded_in_lock_doc() -> None:
    assert "Not Phase 5" in LOCK or "not Phase 5" in LOCK
    assert "Phase 4 unchanged" in LOCK


def test_lock_semantics_not_physical_tables() -> None:
    assert "Lock **semantics and invariants**" in CONST or "Lock semantics" in CONST
