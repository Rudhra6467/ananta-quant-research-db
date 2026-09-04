from pathlib import Path

import pytest

from research_db.lifecycle.engine import run_fixture_lifecycle
from research_db.measure.engine import MeasurementDenied, MeasurementEngine
from research_db.memory.engine import HypothesisEngine
from research_db.observe.engine import ObservationEngine
from research_db.persist import LiveQueryDenied, open_measurement_store
from research_db.state.engine import StateCompiler

ROOT = Path(__file__).resolve().parents[1]
DEFN = "effect_size.mean_forward_return.v1"


def _prep():
    memory = run_fixture_lifecycle()
    obs = ObservationEngine()
    obs.compute(memory.canonical_bars)
    last = memory.canonical_bars[-1]
    compiler = StateCompiler()
    compiler.compile(last, [r for r in obs.observations if r["event_time"] == last["event_time"]])
    store = open_measurement_store()
    store.persist_memory(memory)
    store.persist_evidence(memory)
    store.persist_observation_engine(memory, obs)
    store.persist_state_compiler(compiler)
    hyp = HypothesisEngine()
    hyp.register("H_RSI14_OVERSOLD_4H", "R_RSI14_OVERSOLD_4H", last["event_time"], last["as_of_time"])
    store.persist_hypotheses(hyp)
    return memory, last, store


def test_unrequested_family_is_refused() -> None:
    engine = MeasurementEngine()
    with pytest.raises(MeasurementDenied):
        engine.request("wasserstein.drift.v1")
    with pytest.raises(MeasurementDenied):
        engine.request("rolling_ic.v1")


def test_maps_phase3_evidence_into_measurement_facts() -> None:
    memory, last, store = _prep()
    engine = MeasurementEngine()
    for ev in memory.evidence:
        if ev["relationship"] != "R_RSI14_OVERSOLD_4H":
            continue
        engine.from_evidence(
            definition=DEFN,
            relationship=ev["relationship"],
            hypothesis="H_RSI14_OVERSOLD_4H",
            direction=ev["direction"],
            effect=ev.get("effect"),
            sample_size=ev.get("sample_size"),
            uncertainty=ev.get("uncertainty"),
            event_time=last["event_time"],
            knowledge_time=last["as_of_time"] + ev["stage"],
            conditions={"instrument": "BTC-USD-SPOT", "timeframe": "1h", "stage": ev["stage"]},
        )
    stats = store.persist_measurements(engine)
    assert stats["requests"] == 1
    assert stats["observations"] >= 1
    statuses = {r["epistemic_status"] for r in store.conn.execute("SELECT epistemic_status FROM research__measurement_observation")}
    assert statuses <= {"OBSERVED", "INCONCLUSIVE", "INSUFFICIENT_EVIDENCE", "HIGH_UNCERTAINTY", "UNKNOWN"}
    gate = store.conn.execute("SELECT ingestion_enabled FROM ops__schema_gate WHERE phase='phase7'").fetchone()
    assert int(gate["ingestion_enabled"]) == 0
    with pytest.raises(Exception):
        store.conn.execute("DELETE FROM research__measurement_observation")


def test_live_path_does_not_read_measurements() -> None:
    memory, last, store = _prep()
    engine = MeasurementEngine()
    engine.from_evidence(
        definition=DEFN,
        relationship="R_RSI14_OVERSOLD_4H",
        hypothesis="H_RSI14_OVERSOLD_4H",
        direction="supports",
        effect=0.01,
        sample_size=5,
        uncertainty=0.002,
        event_time=last["event_time"],
        knowledge_time=last["as_of_time"],
        conditions={"instrument": "BTC-USD-SPOT", "timeframe": "1h"},
    )
    store.persist_measurements(engine)
    live = store.live()
    live.execute("SELECT event_time FROM ops__current_regime_state")
    with pytest.raises(LiveQueryDenied):
        live.execute("SELECT point_value FROM research__measurement_observation")
    with pytest.raises(LiveQueryDenied):
        live.execute("SELECT point_value FROM analytics__measurement_current")


def test_phase7_sql_has_no_engine_or_exchange() -> None:
    text = (ROOT / "sql" / "007_phase7_measurement.sql").read_text(encoding="utf-8").lower()
    assert "ingestion_enabled" in text and "false" in text
    assert "binance" not in text
    assert "ranking" not in text
    assert "grouping" not in text
    assert "create_hypertable" not in text
