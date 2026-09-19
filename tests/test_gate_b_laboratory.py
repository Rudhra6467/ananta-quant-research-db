from pathlib import Path
import pytest
from research_db.ingest.orchestrator import INGESTION_ENABLED
from research_db.lab.engine import LaboratoryDenied, fixture_rsi_experiment
from research_db.lifecycle.fixture import FIXTURE_CODE
from research_db.persist import LiveQueryDenied, open_laboratory_store
ROOT = Path(__file__).resolve().parents[1]

def test_end_to_end_fixture_experiment_inconclusive() -> None:
    lab, ctx = fixture_rsi_experiment()
    assert ctx["snapshot"] == FIXTURE_CODE
    assert lab.versions("EXP_RSI14_FWD_RET") == ["v1"]
    assert ctx["result"]["status"] == "inconclusive"
    assert ctx["result"]["input_digest"]
    assert ctx["run"]["tape"] == "fixture"

def test_pit_violation_rejected() -> None:
    lab, ctx = fixture_rsi_experiment()
    with pytest.raises(LaboratoryDenied, match="PIT"):
        lab.attach(ctx["run"]["run_code"], "bar", "future-bar", ctx["future"])

def test_new_cohort_does_not_erase_old() -> None:
    lab, ctx = fixture_rsi_experiment()
    lab.add_cohort("COHORT_BTC_1H_B", "EXP_RSI14_FWD_RET", "v1", "second cohort")
    assert {c["code"] for c in lab.cohorts} == {"COHORT_BTC_1H_A", "COHORT_BTC_1H_B"}
    assert any(r["status"] == "inconclusive" for r in lab.results_for("EXP_RSI14_FWD_RET"))

def test_definitions_are_versioned() -> None:
    lab, _ = fixture_rsi_experiment()
    lab.define("EXP_RSI14_FWD_RET", "v2", "same question, tightened cohort", snapshot=FIXTURE_CODE)
    assert lab.versions("EXP_RSI14_FWD_RET") == ["v1", "v2"]
    with pytest.raises(LaboratoryDenied):
        lab.define("EXP_RSI14_FWD_RET", "v1", "dup", snapshot=FIXTURE_CODE)

def test_rerun_is_new_identity_same_digest() -> None:
    lab, ctx = fixture_rsi_experiment()
    nxt = lab.rerun(ctx["run"]["run_code"])
    assert nxt["run_code"] != ctx["run"]["run_code"]
    assert nxt["input_digest"] == ctx["run"]["input_digest"]
    assert len(lab.results_for("EXP_RSI14_FWD_RET")) == 2

def test_persist_traces_inputs_and_keeps_inconclusive() -> None:
    lab, ctx = fixture_rsi_experiment()
    store = open_laboratory_store()
    stats = store.persist_laboratory(lab)
    assert stats["results"] == 1
    row = store.conn.execute("SELECT status, snapshot_code, input_digest FROM research__lab_result").fetchone()
    assert row["status"] == "inconclusive" and row["snapshot_code"] == FIXTURE_CODE
    assert row["input_digest"] == ctx["result"]["input_digest"]
    n_links = store.conn.execute("SELECT COUNT(*) AS n FROM research__lab_input_link").fetchone()["n"]
    assert n_links >= 4
    gate = store.conn.execute("SELECT ingestion_enabled FROM ops__schema_gate WHERE phase='activation_b'").fetchone()
    assert int(gate["ingestion_enabled"]) == 0
    with pytest.raises(Exception):
        store.conn.execute("DELETE FROM research__lab_result")
    with pytest.raises(LiveQueryDenied):
        store.live().execute("SELECT status FROM research__lab_result")

def test_no_live_ingest_or_phase_21() -> None:
    assert INGESTION_ENABLED is False
    assert list((ROOT / "sql").glob("021*")) == []
    assert list((ROOT / "alembic" / "versions").glob("0021*")) == []
