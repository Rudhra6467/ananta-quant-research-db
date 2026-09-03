from pathlib import Path

import pytest

from research_db.lifecycle.engine import incremental_bar, run_fixture_lifecycle
from research_db.lifecycle.features import rsi
from research_db.observe.engine import ALLOWED, ObservationDenied, ObservationEngine, REQUESTED_PERIODS
from research_db.persist import LiveQueryDenied, open_observation_store

ROOT = Path(__file__).resolve().parents[1]


def test_unrequested_parameter_is_refused() -> None:
    engine = ObservationEngine()
    with pytest.raises(ObservationDenied):
        engine.request("RSI(2)")
    with pytest.raises(ObservationDenied):
        engine.request("RSI(50)")
    with pytest.raises(ObservationDenied):
        ObservationEngine(periods=(14, 30))


def test_engine_matches_phase1_rsi_series() -> None:
    memory = run_fixture_lifecycle()
    engine = ObservationEngine()
    created = engine.compute(memory.canonical_bars)
    closes = [bar["close"] for bar in memory.canonical_bars]
    assert {row["parameter_set"] for row in created} == ALLOWED
    for period in REQUESTED_PERIODS:
        expected = rsi(closes, period)
        got = {
            row["event_time"]: row["value"]
            for row in engine.observations
            if row["parameter_set"] == f"RSI({period})"
        }
        for bar, value in zip(memory.canonical_bars, expected):
            if value is None:
                assert bar["event_time"] not in got
            else:
                assert got[bar["event_time"]] == value


def test_incremental_does_not_rescan_full_history() -> None:
    memory = run_fixture_lifecycle()
    engine = ObservationEngine()
    engine.compute(memory.canonical_bars)
    first_steps = {sig: state.steps for sig, state in engine.states.items()}
    incremental_bar(memory)
    created = engine.compute(memory.canonical_bars)
    assert len(created) == len(REQUESTED_PERIODS)
    for signature, state in engine.states.items():
        assert state.steps == first_steps[signature] + 1
    assert all(row["n_bars"] == 1 for row in engine.compute_log[-len(REQUESTED_PERIODS) :])


def test_persisted_requests_are_only_rsi_12_17() -> None:
    memory = run_fixture_lifecycle()
    engine = ObservationEngine()
    engine.compute(memory.canonical_bars)
    store = open_observation_store()
    store.persist_memory(memory)
    stats = store.persist_observation_engine(memory, engine)
    assert stats["requests"] == 6
    signatures = {row["signature"] for row in store.conn.execute("SELECT signature FROM research__feature_request")}
    assert signatures == ALLOWED
    assert store.conn.execute("SELECT COUNT(*) AS n FROM ops__feature_roll_state").fetchone()["n"] == 6
    notes = store.conn.execute(
        "SELECT ingestion_enabled FROM ops__schema_gate WHERE phase='phase4'"
    ).fetchone()
    assert int(notes["ingestion_enabled"]) == 0


def test_live_path_cannot_read_observation_history() -> None:
    memory = run_fixture_lifecycle()
    engine = ObservationEngine()
    engine.compute(memory.canonical_bars)
    store = open_observation_store()
    store.persist_memory(memory)
    store.persist_observation_engine(memory, engine)
    live = store.live()
    live.execute("SELECT event_time FROM ops__current_feature_value")
    with pytest.raises(LiveQueryDenied):
        live.execute("SELECT value FROM feature__observation")


def test_phase4_sql_has_no_exchange() -> None:
    text = (ROOT / "sql" / "004_phase4_observation.sql").read_text(encoding="utf-8")
    assert "ingestion_enabled" in text
    assert "false" in text
    assert "binance" not in text.lower()
    assert "create_hypertable" not in text.lower()
