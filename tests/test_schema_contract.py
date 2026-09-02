from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PHASE0 = (ROOT / "research_db" / "models" / "phase0.py").read_text(encoding="utf-8")

EXPECTED_TABLES = [
    "data_source",
    "venue",
    "asset",
    "instrument",
    "timeframe",
    "market_universe",
    "dataset_snapshot",
    "ingestion_run",
    "canonicalization_run",
    "schema_gate",
    "current_market_state",
    "current_feature_value",
    "current_regime_state",
    "operational_relationship_applicability",
    "indicator_definition",
    "feature_definition",
    "feature_version",
    "parameter_definition",
    "parameter_set",
    "outcome_definition",
    "validation_stage",
    "relationship_definition",
    "relationship_term",
    "experiment_run",
    "experiment_trial",
    "relationship_evidence",
    "ranking_snapshot",
    "decision_event",
    "counterfactual_outcome",
    "relationship_current_summary",
]


def test_ingestion_disabled_in_settings_source() -> None:
    text = (ROOT / "research_db" / "config.py").read_text(encoding="utf-8")
    assert "ingestion_enabled: bool = False" in text


def test_schemas_declared_in_base() -> None:
    text = (ROOT / "research_db" / "models" / "base.py").read_text(encoding="utf-8")
    assert "world" in text and "market" in text and "feature" in text


def test_phase0_tables_declared() -> None:
    missing = [name for name in EXPECTED_TABLES if f'__tablename__ = "{name}"' not in PHASE0]
    assert missing == []


def test_phase0_has_no_observation_hypertable() -> None:
    assert "feature_observation" not in PHASE0
    phase2_sql = (ROOT / "sql" / "002_phase2_market_truth.sql").read_text(encoding="utf-8")
    assert "feature.observation" in phase2_sql


def test_decision_actions_locked() -> None:
    assert "ENTER" in PHASE0 and "WAIT" in PHASE0 and "SKIP" in PHASE0


def test_orm_import_when_sqlalchemy_present() -> None:
    pytest.importorskip("sqlalchemy")
    from research_db.config import Settings
    from research_db.models.base import SCHEMAS, metadata

    assert Settings().ingestion_enabled is False
    assert SCHEMAS[0] == "ref"
    present = {t.name for t in metadata.tables.values()}
    assert "decision_event" in present
