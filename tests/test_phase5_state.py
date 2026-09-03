from pathlib import Path
from statistics import median

import pytest

from research_db.lifecycle.engine import incremental_bar, run_fixture_lifecycle
from research_db.observe.engine import ALLOWED, ObservationDenied, ObservationEngine, REQUESTED_PERIODS
from research_db.persist import LiveQueryDenied, open_state_store
from research_db.state.engine import OVERSOLD, REGIME_FAMILY, StateCompileDenied, StateCompiler

ROOT = Path(__file__).resolve().parents[1]


def _latest_obs(engine, event_time: str):
    return [row for row in engine.observations if row["event_time"] == event_time]


def test_compiler_uses_only_requested_features() -> None:
    memory = run_fixture_lifecycle()
    engine = ObservationEngine()
    engine.compute(memory.canonical_bars)
    last = memory.canonical_bars[-1]
    compiler = StateCompiler()
    out = compiler.compile(last, _latest_obs(engine, last["event_time"]))
    assert set(out["features"]) == ALLOWED
    values = [row["value"] for row in out["features"].values() if row["value"] is not None]
    assert out["regime"]["value"] == float(median(values))
    assert out["regime"]["regime_family"] == REGIME_FAMILY
    assert out["regime"]["provenance"] == "system_fixture"
    expected = "oversold" if out["regime"]["value"] < OVERSOLD else "neutral"
    assert out["regime"]["label"] == expected
    assert out["market"]["close"] == last["close"]
    assert out["market"]["event_time"] == last["event_time"]


def test_unrequested_feature_cannot_enter_state() -> None:
    memory = run_fixture_lifecycle()
    last = memory.canonical_bars[-1]
    compiler = StateCompiler()
    with pytest.raises(StateCompileDenied):
        compiler.compile(last, [{"parameter_set": "RSI(2)", "event_time": last["event_time"], "value": 10.0}])


def test_unknown_when_no_features() -> None:
    memory = run_fixture_lifecycle()
    last = memory.canonical_bars[-1]
    out = StateCompiler().compile(last, [])
    assert out["regime"]["label"] == "UNKNOWN"
    assert out["regime"]["epistemic_status"] == "INSUFFICIENT_EVIDENCE"


def test_persist_current_projections_and_append_only_facts() -> None:
    memory = run_fixture_lifecycle()
    engine = ObservationEngine()
    engine.compute(memory.canonical_bars)
    last = memory.canonical_bars[-1]
    compiler = StateCompiler()
    compiler.compile(last, _latest_obs(engine, last["event_time"]))
    store = open_state_store()
    store.persist_memory(memory)
    store.persist_observation_engine(memory, engine)
    stats = store.persist_state_compiler(compiler)
    assert stats["current_features"] == 6
    assert stats["market_facts"] == 1
    assert stats["regime_facts"] == 1
    gate = store.conn.execute("SELECT ingestion_enabled FROM ops__schema_gate WHERE phase='phase5'").fetchone()
    assert int(gate["ingestion_enabled"]) == 0
    row = store.conn.execute("SELECT event_time, label FROM ops__current_regime_state").fetchone()
    assert row["event_time"] == last["event_time"]
    assert row["label"] in {"oversold", "neutral", "UNKNOWN"}
    cms = store.conn.execute("SELECT event_time, payload FROM ops__current_market_state").fetchone()
    assert cms["event_time"] == last["event_time"]


def test_live_path_reads_only_ops_current() -> None:
    memory = run_fixture_lifecycle()
    engine = ObservationEngine()
    engine.compute(memory.canonical_bars)
    last = memory.canonical_bars[-1]
    compiler = StateCompiler()
    compiler.compile(last, _latest_obs(engine, last["event_time"]))
    store = open_state_store()
    store.persist_memory(memory)
    store.persist_observation_engine(memory, engine)
    store.persist_state_compiler(compiler)
    live = store.live()
    live.execute("SELECT event_time FROM ops__current_market_state")
    live.execute("SELECT value FROM ops__current_feature_value")
    live.execute("SELECT label FROM ops__current_regime_state")
    with pytest.raises(LiveQueryDenied):
        live.execute("SELECT close FROM state__market_state_observation")
    with pytest.raises(LiveQueryDenied):
        live.execute("SELECT label FROM state__regime_observation")
    with pytest.raises(LiveQueryDenied):
        live.execute("SELECT value FROM feature__observation")
    with pytest.raises(LiveQueryDenied):
        live.execute("SELECT close FROM market__ohlcv_bar")


def test_incremental_compile_does_not_rescan_history() -> None:
    memory = run_fixture_lifecycle()
    engine = ObservationEngine()
    engine.compute(memory.canonical_bars)
    compiler = StateCompiler()
    first = memory.canonical_bars[-1]
    compiler.compile(first, _latest_obs(engine, first["event_time"]))
    store = open_state_store()
    store.persist_memory(memory)
    store.persist_observation_engine(memory, engine)
    store.persist_state_compiler(compiler)
    incremental_bar(memory)
    created = engine.compute(memory.canonical_bars)
    assert len(created) == len(REQUESTED_PERIODS)
    last = memory.canonical_bars[-1]
    compiler.compile(last, created)
    assert compiler.compile_log[-1]["full_history_scan"] is False
    store.persist_incremental(memory)
    store.persist_observation_engine(memory, engine)
    store.persist_state_compiler(compiler)
    assert store.conn.execute("SELECT COUNT(*) AS n FROM state__regime_observation").fetchone()["n"] == 2
    current = store.conn.execute("SELECT event_time FROM ops__current_market_state").fetchone()
    assert current["event_time"] == last["event_time"]
    times = {r["event_time"] for r in store.conn.execute("SELECT event_time FROM state__market_state_observation")}
    assert first["event_time"] in times and last["event_time"] in times


def test_phase4_engine_still_refuses_unrequested() -> None:
    with pytest.raises(ObservationDenied):
        ObservationEngine().request("RSI(2)")


def test_phase5_sql_has_no_exchange_or_ranking() -> None:
    text = (ROOT / "sql" / "005_phase5_state.sql").read_text(encoding="utf-8")
    lowered = text.lower()
    assert "ingestion_enabled" in lowered
    assert "false" in lowered
    assert "binance" not in lowered
    assert "ranking" not in lowered
    assert "prediction" not in lowered
    assert "create_hypertable" not in lowered
