from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = (ROOT / "docs" / "ARCHITECTURE_LOCK_AUDIT.md").read_text(encoding="utf-8")
PHASE0 = (ROOT / "research_db" / "models" / "phase0.py").read_text(encoding="utf-8")
BASE = (ROOT / "research_db" / "models" / "base.py").read_text(encoding="utf-8")


def test_audit_covers_requested_capabilities() -> None:
    required = [
        "World / external conditions",
        "Shock → path",
        "Scenario / counterfactual",
        "Portfolio exposure",
        "Prediction → outcome → error",
        "Uncertainty / confidence",
        "Model disagreement",
        "Reliability ≠ prediction value",
        "Multi-factor ranking",
        "Decay / invalidation",
        "Experiment isolation and reset",
        "Negative knowledge",
        "PIT reconstruction",
        "Reproducibility",
        "Multi-market expansion",
    ]
    missing = [item for item in required if item not in AUDIT]
    assert missing == []


def test_locked_epistemic_and_reset_laws() -> None:
    for token in (
        "UNKNOWN",
        "INSUFFICIENT_EVIDENCE",
        "HIGH_UNCERTAINTY",
        "OUT_OF_DISTRIBUTION",
        "MODEL_DISAGREEMENT",
        "Reset means a new experiment cohort",
        "Prediction value ≠ prediction reliability ≠ knowledge ranking",
    ):
        assert token in AUDIT


def test_asset_identity_is_class_scoped() -> None:
    assert "uq_asset_class_symbol" in PHASE0
    assert "symbol: Mapped[str] = mapped_column(Text, nullable=False, unique=True)" not in PHASE0


def test_evidence_states_include_negative_knowledge() -> None:
    for state in ("untested", "supports", "contradicts", "inconclusive", "invalidated", "decayed"):
        assert f"'{state}'" in PHASE0


def test_reserved_future_schemas_exist() -> None:
    for schema in ("world", "prediction", "portfolio"):
        assert f'"{schema}"' in BASE


def test_phase2_not_expanded_into_predictions() -> None:
    sql = (ROOT / "sql" / "002_phase2_market_truth.sql").read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS prediction." not in sql
    assert "CREATE TABLE IF NOT EXISTS portfolio." not in sql
