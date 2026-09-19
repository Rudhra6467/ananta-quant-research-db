from pathlib import Path

from research_db.lifecycle.engine import run_fixture_lifecycle
from research_db.observe.engine import ObservationEngine
from research_db.persist import open_regime_store
from research_db.regime.engine import RegimeDefinitionRegistry
from research_db.state.engine import StateCompiler

ROOT = Path(__file__).resolve().parents[1]


def test_versioned_definition_does_not_replace_phase5() -> None:
    reg = RegimeDefinitionRegistry()
    active = reg.active("rsi_region")
    assert active["version"] == "v1"
    memory = run_fixture_lifecycle()
    obs = ObservationEngine()
    obs.compute(memory.canonical_bars)
    last = memory.canonical_bars[-1]
    compiler = StateCompiler()
    compiler.compile(last, [r for r in obs.observations if r["event_time"] == last["event_time"]])
    assert compiler.regime_states[-1]["label"] in {"oversold", "neutral", "UNKNOWN"}


def test_persist_regime_definition_fixture() -> None:
    store = open_regime_store()
    store.persist_memory(run_fixture_lifecycle())
    stats = store.persist_regime_definitions()
    assert stats["definitions"] == 1
    row = store.conn.execute("SELECT code, version, status FROM research__regime_definition").fetchone()
    assert row["code"] == "rsi_region" and row["version"] == "v1"
    gate = store.conn.execute("SELECT ingestion_enabled FROM ops__schema_gate WHERE phase='phase10'").fetchone()
    assert int(gate["ingestion_enabled"]) == 0


def test_phase10_sql_has_no_shift_engine() -> None:
    text = (ROOT / "sql" / "010_phase10_regime.sql").read_text().lower()
    assert "cusum" not in text
    assert "pelt" not in text
    assert "binance" not in text
