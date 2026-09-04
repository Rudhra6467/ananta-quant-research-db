from pathlib import Path
import pytest
from research_db.ingest.orchestrator import INGESTION_ENABLED
from research_db.lab.engine import Laboratory
from research_db.persist import LiveQueryDenied, open_shift_store
from research_db.shift.engine import ShiftDenied, fixture_shift_demo
ROOT = Path(__file__).resolve().parents[1]

def test_fixture_scan_is_not_certainty_or_live() -> None:
    reg, ctx = fixture_shift_demo()
    assert ctx["found"]
    assert all(c["certainty"] is False and c["live_claim"] is False for c in ctx["found"])
    assert {c["event_code"] for c in ctx["found"]} <= {"E_BREAK_T20", "E_SHIFT_T24"}

def test_early_as_of_cannot_see_later_event() -> None:
    _, ctx = fixture_shift_demo()
    assert ctx["early_found"] == []

def test_review_keeps_false_positive_and_inconclusive() -> None:
    reg, ctx = fixture_shift_demo()
    cand = ctx["found"][0]
    reg.review(cand["candidate_code"], "inconclusive", "fixture n too small", ctx["as_of"])
    if len(ctx["found"]) > 1:
        other = ctx["found"][1]
        reg.review(other["candidate_code"], "false_positive", "annotation only", ctx["as_of"])
    assert any(r["status"] == "inconclusive" for r in reg.reviews)
    with pytest.raises(ShiftDenied):
        reg.review(cand["candidate_code"], "win", "no", ctx["as_of"])

def test_versioned_spec_and_rerun_digest() -> None:
    reg, ctx = fixture_shift_demo()
    assert reg.versions("DET_ANNOTATED_SHIFT") == ["v1"]
    nxt = reg.rerun(ctx["run"]["run_code"], ctx["events"])
    assert nxt["run_code"] != ctx["run"]["run_code"]
    assert nxt["input_digest"] == ctx["run"]["input_digest"]

def test_lab_can_evaluate_without_embedding_stats() -> None:
    reg, ctx = fixture_shift_demo()
    lab = Laboratory()
    lab.define("EXP_SHIFT_ANNOTATION", "v1", "Does annotated fixture shift imply a durable regime change?", snapshot=ctx["snapshot"], hypothesis="H_SHIFT_NOT_CERTAIN")
    lab.add_cohort("COHORT_SHIFT_A", "EXP_SHIFT_ANNOTATION", "v1")
    run = lab.start_run(experiment="EXP_SHIFT_ANNOTATION", version="v1", cohort="COHORT_SHIFT_A", snapshot=ctx["snapshot"], as_of=ctx["as_of"])
    lab.attach(run["run_code"], "regime", ctx["found"][0]["event_code"], ctx["as_of"])
    result = lab.complete(run["run_code"], "inconclusive", "detection is not confirmation")
    assert result["status"] == "inconclusive"

def test_persist_and_live_path_and_no_phase21() -> None:
    reg, ctx = fixture_shift_demo()
    reg.review(ctx["found"][0]["candidate_code"], "inconclusive", "kept", ctx["as_of"])
    store = open_shift_store()
    stats = store.persist_shift_registry(reg)
    assert stats["candidates"] >= 1
    row = store.conn.execute("SELECT live_claim, certainty FROM research__shift_candidate").fetchone()
    assert int(row["live_claim"]) == 0 and int(row["certainty"]) == 0
    gate = store.conn.execute("SELECT ingestion_enabled FROM ops__schema_gate WHERE phase='activation_c'").fetchone()
    assert int(gate["ingestion_enabled"]) == 0
    with pytest.raises(Exception):
        store.conn.execute("DELETE FROM research__shift_candidate")
    with pytest.raises(LiveQueryDenied):
        store.live().execute("SELECT event_code FROM research__shift_candidate")
    assert INGESTION_ENABLED is False
    assert list((ROOT / "sql").glob("021*")) == []
