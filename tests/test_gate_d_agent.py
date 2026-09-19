from pathlib import Path
import pytest
from research_db.agent.catalog import AVAILABLE, BLOCKED, CATALOG_VERSION, all_capabilities
from research_db.agent.context import AgentContext, fixture_agent_context
from research_db.agent.engine import AgentConsult, AgentDenied
from research_db.ingest.orchestrator import INGESTION_ENABLED
from research_db.persist import LiveQueryDenied, open_agent_catalog_store
ROOT = Path(__file__).resolve().parents[1]

def test_catalog_separates_available_reserved_blocked() -> None:
    caps = {c.name: c for c in all_capabilities()}
    assert caps["current_regime"].status == "available"
    assert caps["prediction_distribution"].status == "reserved"
    assert caps["live_order"].status == "blocked"
    assert caps["mutate_hypothesis"].mutation is True
    assert set(AVAILABLE) & set(BLOCKED) == set()

def test_context_requires_information_set_and_rejects_future() -> None:
    with pytest.raises(AgentDenied):
        AgentContext(subject="", snapshot="x", as_of="t")
    ctx, demo = fixture_agent_context()
    assert ctx.uncertainty == "INSUFFICIENT_EVIDENCE" and ctx.live_claim is False
    with pytest.raises(AgentDenied, match="PIT"):
        ctx.observe("events_as_of", demo["later_event"]["code"], demo["later_event"]["knowledge_time"])
    with pytest.raises(AgentDenied, match="blocked"):
        ctx.observe("live_order", "x", demo["early_as_of"])
    with pytest.raises(AgentDenied, match="reserved"):
        ctx.observe("prediction_distribution", "x", demo["early_as_of"])
    with pytest.raises(AgentDenied):
        ctx.decide("TAKE")

def test_consult_still_cannot_mutate() -> None:
    agent = AgentConsult()
    agent.consult("current_regime", "2026-01-01T10:00:00+00:00")
    with pytest.raises(AgentDenied):
        agent.mutate()

def test_persist_catalog_and_context() -> None:
    ctx, _ = fixture_agent_context()
    store = open_agent_catalog_store()
    n = store.persist_agent_catalog()
    assert n == len(all_capabilities())
    store.persist_agent_context(ctx)
    row = store.conn.execute("SELECT catalog_version, live_claim, mutated, uncertainty FROM interface__agent_context").fetchone()
    assert row["catalog_version"] == CATALOG_VERSION
    assert int(row["live_claim"]) == 0 and int(row["mutated"]) == 0
    assert row["uncertainty"] == "INSUFFICIENT_EVIDENCE"
    gate = store.conn.execute("SELECT ingestion_enabled FROM ops__schema_gate WHERE phase='activation_d'").fetchone()
    assert int(gate["ingestion_enabled"]) == 0
    with pytest.raises(LiveQueryDenied):
        store.live().execute("SELECT name FROM interface__agent_capability")
    assert INGESTION_ENABLED is False
    assert list((ROOT / "sql").glob("021*")) == []
