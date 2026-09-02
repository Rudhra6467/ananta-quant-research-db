from pathlib import Path

import pytest

from research_db.lifecycle.engine import RSI_REGION, incremental_bar, run_fixture_lifecycle
from research_db.persist.ids import stable_id
from research_db.persist.store import LiveQueryDenied, open_fixture_store

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def loaded():
    memory = run_fixture_lifecycle()
    store = open_fixture_store()
    stats = store.persist_memory(memory)
    return memory, store, stats


def test_phase2_sql_is_postgres_timescale() -> None:
    text = (ROOT / "sql" / "002_phase2_market_truth.sql").read_text(encoding="utf-8")
    assert "CREATE EXTENSION IF NOT EXISTS timescaledb" in text
    assert "create_hypertable('market.ohlcv_bar'" in text
    assert "ingestion_enabled" in text


def test_canonical_bars_match_phase1(loaded) -> None:
    memory, store, stats = loaded
    assert stats["canonical_bars"] == 48
    rows = store.conn.execute("SELECT event_time, close FROM market__ohlcv_bar ORDER BY event_time").fetchall()
    assert [r["close"] for r in rows] == [b["close"] for b in memory.canonical_bars]


def test_rsi_region_and_rsi14_resolve(loaded) -> None:
    _, store, _ = loaded
    region = store.conn.execute("SELECT code, lo, hi FROM research__parameter_region").fetchone()
    assert region["code"] == "RSI(12-17)" and region["lo"] == 12 and region["hi"] == 17
    members = [r["signature"] for r in store.conn.execute(
        """SELECT ps.signature FROM research__parameter_region_member m
           JOIN research__parameter_set ps ON ps.id = m.parameter_set_id ORDER BY ps.signature"""
    )]
    assert members == [f"RSI({p})" for p in RSI_REGION]


def test_requested_observations_only(loaded) -> None:
    memory, store, stats = loaded
    signatures = {r["signature"] for r in store.conn.execute(
        """SELECT DISTINCT ps.signature FROM feature__observation o
           JOIN research__parameter_set ps ON ps.id = o.parameter_set_id"""
    )}
    assert signatures == {f"RSI({p})" for p in RSI_REGION}
    assert stats["parameter_sets"] == 6
    assert stats["observations"] == len(memory.feature_observations)


def test_combinations_are_requests_not_cubes(loaded) -> None:
    _, store, _ = loaded
    codes = {r["code"] for r in store.conn.execute("SELECT code FROM research__combination_request")}
    assert codes == {"R_RSI_REGION_OVERSOLD_4H", "R_RSI14_OVERSOLD_4H"}
    tables = {r[0] for r in store.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "combination_cube" not in tables
    assert "research__relationship_evidence" not in tables


def test_point_in_time_filter(loaded) -> None:
    memory, store, _ = loaded
    cutoff = memory.canonical_bars[10]["as_of_time"]
    visible = store.bars_as_of(cutoff)
    assert len(visible) == 11
    hidden = store.bars_as_of(memory.canonical_bars[10]["event_time"])
    assert memory.canonical_bars[10]["event_time"] not in {r["event_time"] for r in hidden}


def test_live_path_cannot_read_history(loaded) -> None:
    _, store, _ = loaded
    live = store.live()
    assert live.execute("SELECT event_time FROM ops__current_market_state").fetchall()
    with pytest.raises(LiveQueryDenied):
        live.execute("SELECT close FROM market__ohlcv_bar")
    with pytest.raises(LiveQueryDenied):
        live.execute("SELECT payload FROM raw__market_event")
    with pytest.raises(LiveQueryDenied):
        live.execute("SELECT value FROM feature__observation")


def test_incremental_bar_without_history_rewrite(loaded) -> None:
    memory, store, _ = loaded
    incremental_bar(memory)
    result = store.persist_incremental(memory)
    assert result["new_bars"] == 1
    assert result["new_observations"] == len(RSI_REGION)
    first_id = store.conn.execute("SELECT id FROM market__ohlcv_bar ORDER BY event_time LIMIT 1").fetchone()["id"]
    assert first_id == stable_id("bar", memory.canonical_bars[0]["source_record_id"])


def test_lineage_and_snapshot_reproducible(loaded) -> None:
    memory, store, _ = loaded
    snap = store.conn.execute("SELECT id, code FROM ops__dataset_snapshot").fetchone()
    assert snap["code"] == "fixture-btc-1h-v1"
    assert snap["id"] == stable_id("snapshot", "fixture-btc-1h-v1")
    gate = store.conn.execute("SELECT ingestion_enabled FROM ops__schema_gate WHERE phase='phase2'").fetchone()
    assert int(gate["ingestion_enabled"]) == 0
    again = open_fixture_store()
    again.persist_memory(memory)
    assert again.conn.execute("SELECT id FROM ops__dataset_snapshot").fetchone()["id"] == snap["id"]


def test_append_only_facts(loaded) -> None:
    _, store, _ = loaded
    with pytest.raises(Exception):
        store.conn.execute("DELETE FROM market__ohlcv_bar")


def test_no_exchange_modules() -> None:
    persist_root = ROOT / "research_db" / "persist"
    blob = "".join(p.read_text(encoding="utf-8") for p in persist_root.glob("*.py"))
    for needle in ("binance", "kraken", "ccxt", "wss://"):
        assert needle not in blob.lower()
