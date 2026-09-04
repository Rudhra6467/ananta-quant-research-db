from pathlib import Path

import pytest

from research_db.analyze.engine import ALLOWED, AnalyticalDenied, AnalyticalEngine
from research_db.lifecycle.engine import run_fixture_lifecycle
from research_db.observe.engine import ObservationEngine
from research_db.persist import LiveQueryDenied, open_analytical_store
from research_db.state.engine import StateCompiler

ROOT = Path(__file__).resolve().parents[1]


def test_unrequested_analytical_feature_refused() -> None:
    engine = AnalyticalEngine()
    with pytest.raises(AnalyticalDenied):
        engine.request("MACD(12,26)")
    engine.request("RET(1)")
    engine.request("RANGE_VOL(1)")
    assert set(engine.requests) == ALLOWED


def test_computes_only_requested_and_does_not_break_phase5() -> None:
    memory = run_fixture_lifecycle()
    engine = AnalyticalEngine()
    engine.request("RET(1)")
    rows = engine.compute(memory.canonical_bars)
    assert rows
    assert all(r["parameter_set"] == "RET(1)" for r in rows)
    obs = ObservationEngine()
    obs.compute(memory.canonical_bars)
    last = memory.canonical_bars[-1]
    rsi_only = [r for r in obs.observations if r["event_time"] == last["event_time"]]
    compiler = StateCompiler()
    compiler.compile(last, rsi_only)
    assert compiler.regime_states[-1]["regime_family"] == "rsi_region"


def test_persists_into_feature_observation_not_live() -> None:
    memory = run_fixture_lifecycle()
    store = open_analytical_store()
    store.persist_memory(memory)
    engine = AnalyticalEngine()
    engine.request("RET(1)")
    engine.request("RANGE_VOL(1)")
    engine.compute(memory.canonical_bars)
    stats = store.persist_analytical(engine)
    assert stats["requests"] == 2
    assert stats["analytical_observations"] > 0
    n = store.conn.execute(
        "SELECT COUNT(*) AS n FROM feature__observation fo JOIN research__parameter_set ps ON ps.id=fo.parameter_set_id WHERE ps.signature='RET(1)'"
    ).fetchone()["n"]
    assert n > 0
    gate = store.conn.execute("SELECT ingestion_enabled FROM ops__schema_gate WHERE phase='phase9'").fetchone()
    assert int(gate["ingestion_enabled"]) == 0
    with pytest.raises(LiveQueryDenied):
        store.live().execute("SELECT value FROM feature__observation")


def test_phase9_sql_scope() -> None:
    text = (ROOT / "sql" / "009_phase9_analytical.sql").read_text().lower()
    assert "false" in text
    assert "binance" not in text
    assert "current_group" not in text
