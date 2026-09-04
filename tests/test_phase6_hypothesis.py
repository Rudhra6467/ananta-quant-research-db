from pathlib import Path

import pytest

from research_db.lifecycle.engine import run_fixture_lifecycle
from research_db.memory.engine import HYPOTHESIS_STATES, HypothesisDenied, HypothesisEngine
from research_db.observe.engine import ObservationEngine
from research_db.persist import LiveQueryDenied, open_hypothesis_store
from research_db.state.engine import StateCompiler

ROOT = Path(__file__).resolve().parents[1]


def _prep():
    memory = run_fixture_lifecycle()
    engine = ObservationEngine()
    engine.compute(memory.canonical_bars)
    last = memory.canonical_bars[-1]
    compiler = StateCompiler()
    compiler.compile(last, [row for row in engine.observations if row["event_time"] == last["event_time"]])
    store = open_hypothesis_store()
    store.persist_memory(memory)
    store.persist_evidence(memory)
    store.persist_observation_engine(memory, engine)
    store.persist_state_compiler(compiler)
    return memory, last, store


def test_memory_as_of_reads_existing_state_facts() -> None:
    memory, last, store = _prep()
    rows = store.memory_as_of(last["as_of_time"])
    assert rows["market_states"]
    assert rows["regime_states"]
    assert rows["market_states"][-1]["event_time"] == last["event_time"]


def test_hypothesis_lifecycle_is_append_only() -> None:
    memory, last, store = _prep()
    hyp = HypothesisEngine()
    code = "H_RSI14_OVERSOLD_4H"
    hyp.register(code, "R_RSI14_OVERSOLD_4H", last["event_time"], last["as_of_time"])
    hyp.apply_evidence(code, "supports", last["event_time"], last["as_of_time"], evidence_key="ev-hist")
    hyp.apply_evidence(code, "contradicts", last["event_time"], last["as_of_time"] + "Z", evidence_key="ev-oos")
    hyp.apply_evidence(code, "invalidated", last["event_time"], last["as_of_time"] + "ZZ", evidence_key="ev-inv")
    hyp.link_state(code, "regime_state", "rsi_region", last["event_time"], last["as_of_time"])
    hyp.define_analogue()
    assert hyp.current_status(code) == "invalidated"
    assert {e["status"] for e in hyp.status_events} >= {"proposed", "supported", "contradicted", "invalidated"}
    stats = store.persist_hypotheses(hyp)
    assert stats["hypotheses"] == 1
    assert stats["status_events"] >= 4
    assert stats["analogues"] == 1
    with pytest.raises(Exception):
        store.conn.execute("UPDATE research__hypothesis_status_event SET status='supported'")
    with pytest.raises(Exception):
        store.conn.execute("DELETE FROM research__hypothesis_status_event")
    kinds = {r["source_kind"] for r in store.conn.execute("SELECT source_kind FROM research__hypothesis_support_link")}
    assert "evidence" in kinds and "regime_state" in kinds
    claim = store.conn.execute("SELECT claim_kind FROM research__hypothesis").fetchone()["claim_kind"]
    assert claim == "system_hypothesis"


def test_all_lifecycle_states_are_legal() -> None:
    assert HYPOTHESIS_STATES == (
        "proposed",
        "under_test",
        "supported",
        "contradicted",
        "inconclusive",
        "invalidated",
        "decayed",
    )
    hyp = HypothesisEngine()
    with pytest.raises(HypothesisDenied):
        hyp.apply_evidence("x", "magic", "t", "t")


def test_live_path_does_not_read_hypothesis_history() -> None:
    memory, last, store = _prep()
    hyp = HypothesisEngine()
    hyp.register("H_RSI14_OVERSOLD_4H", "R_RSI14_OVERSOLD_4H", last["event_time"], last["as_of_time"])
    store.persist_hypotheses(hyp)
    live = store.live()
    live.execute("SELECT event_time FROM ops__current_regime_state")
    with pytest.raises(LiveQueryDenied):
        live.execute("SELECT status FROM research__hypothesis_status_event")
    with pytest.raises(LiveQueryDenied):
        live.execute("SELECT status FROM analytics__hypothesis_current_status")


def test_phase6_sql_stays_narrow() -> None:
    text = (ROOT / "sql" / "006_phase6_hypothesis.sql").read_text(encoding="utf-8").lower()
    assert "ingestion_enabled" in text and "false" in text
    assert "binance" not in text
    assert "ranking" not in text
    assert "grouping" not in text
    assert "create_hypertable" not in text
