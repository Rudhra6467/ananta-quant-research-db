from pathlib import Path
import pytest
from research_db.iface.engine import InterfaceDenied, QueryCatalog
from research_db.lifecycle.engine import run_fixture_lifecycle
from research_db.memorytier.engine import MemoryTierPolicy
from research_db.persist import LiveQueryDenied, open_governance_store
from research_db.security.engine import AccessDenied, AccessPolicy
ROOT = Path(__file__).resolve().parents[1]

def test_compression_does_not_delete_raw() -> None:
    memory = run_fixture_lifecycle()
    policy = MemoryTierPolicy()
    policy.summarize(memory.canonical_bars)
    assert all(not p["deletes_raw"] for p in policy.policies)
    assert all(s["raw_retained"] for s in policy.summaries)
    store = open_governance_store()
    store.persist_memory(memory)
    store.persist_memory_tiers(policy)
    assert store._count("market__ohlcv_bar") == len(memory.canonical_bars)
    assert store._count("research__memory_summary") == 2
    assert int(store.conn.execute("SELECT ingestion_enabled FROM ops__schema_gate WHERE phase='phase14'").fetchone()["ingestion_enabled"]) == 0

def test_agent_reader_cannot_write_research() -> None:
    policy = AccessPolicy()
    assert policy.allows("live_reader", "ops.current_*", "read")
    assert policy.allows("agent_reader", "interface.*", "read")
    assert policy.allows("agent_reader", "research.*", "write") is False
    with pytest.raises(AccessDenied):
        policy.allows("bot", "research.*", "read")

def test_query_catalog_is_read_only_and_bounded() -> None:
    cat = QueryCatalog()
    cat.request("events_as_of")
    with pytest.raises(InterfaceDenied):
        cat.request("delete_all_evidence")
    store = open_governance_store()
    store.persist_memory(run_fixture_lifecycle())
    store.persist_access_policy()
    store.persist_query_catalog(cat)
    assert store._count("interface__query_catalog") == len(cat.queries)
    mut = store.conn.execute("SELECT MAX(mutation) AS m FROM interface__query_catalog").fetchone()["m"]
    assert int(mut) == 0
    with pytest.raises(LiveQueryDenied):
        store.live().execute("SELECT name FROM interface__query_catalog")

def test_sql_scope() -> None:
    for path in ["sql/014_phase14_memory.sql", "sql/015_phase15_security.sql", "sql/016_phase16_interface.sql"]:
        text = (ROOT / path).read_text().lower()
        assert "false" in text and "binance" not in text and "cusum" not in text
