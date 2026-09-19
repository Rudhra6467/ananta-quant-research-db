from pathlib import Path
import pytest
from research_db.agent.engine import AgentConsult, AgentDenied
from research_db.expansion.engine import ExpansionRegistry
from research_db.iface.engine import InterfaceDenied
from research_db.lifecycle.engine import run_fixture_lifecycle
from research_db.paper.engine import PaperDenied, PaperLedger
from research_db.persist import LiveQueryDenied, open_closed_loop_store
ROOT = Path(__file__).resolve().parents[1]

def test_agent_consult_uses_catalog_and_cannot_mutate() -> None:
    agent = AgentConsult()
    last = run_fixture_lifecycle().canonical_bars[-1]["as_of_time"]
    agent.consult("events_as_of", last)
    with pytest.raises(InterfaceDenied):
        agent.consult("raw_dump", last)
    with pytest.raises(AgentDenied):
        agent.mutate()

def test_paper_profiles_have_zero_capital() -> None:
    ledger = PaperLedger()
    assert all(p["live_capital"] is False for p in ledger.profiles)
    last = run_fixture_lifecycle().canonical_bars[-1]["as_of_time"]
    ledger.decide("AVERAGE", "WAIT", last, "insufficient evidence", "events_as_of")
    ledger.decide("AGGRESSIVE", "SKIP", last, "no validated edge")
    with pytest.raises(PaperDenied):
        ledger.decide("SAFE", "TAKE", last, "blocked")
    with pytest.raises(PaperDenied):
        ledger.decide("YOLO", "TAKE", last, "no")

def test_expansion_not_ingested() -> None:
    assert ExpansionRegistry().ingested() is False

def test_persist_closed_loop_fixture() -> None:
    memory = run_fixture_lifecycle()
    store = open_closed_loop_store()
    store.persist_memory(memory)
    agent = AgentConsult()
    agent.consult("current_regime", memory.canonical_bars[-1]["as_of_time"])
    store.persist_consults(agent)
    ledger = PaperLedger()
    ledger.decide("AVERAGE", "WAIT", memory.canonical_bars[-1]["as_of_time"], "lab only")
    store.persist_paper(ledger)
    store.persist_expansion()
    assert store._count("interface__consult_event") == 1
    assert store.conn.execute("SELECT MAX(mutated) AS m FROM interface__consult_event").fetchone()["m"] == 0
    assert store.conn.execute("SELECT MAX(live_capital) AS m FROM research__operating_profile").fetchone()["m"] == 0
    assert store.conn.execute("SELECT MAX(capital) AS m FROM research__paper_decision").fetchone()["m"] == 0
    assert store.conn.execute("SELECT MAX(ingested) AS m FROM ops__universe_plan").fetchone()["m"] == 0
    assert store.conn.execute("SELECT MAX(created) AS m FROM ops__market_database_plan").fetchone()["m"] == 0
    for phase in ("phase17", "phase18", "phase19", "phase20"):
        assert int(store.conn.execute("SELECT ingestion_enabled FROM ops__schema_gate WHERE phase=?", (phase,)).fetchone()["ingestion_enabled"]) == 0
    with pytest.raises(LiveQueryDenied):
        store.live().execute("SELECT action FROM research__paper_decision")

def test_sql_has_no_exchange() -> None:
    for name in ("017_phase17_agent.sql", "018_phase18_paper.sql", "019_phase19_expansion.sql", "020_phase20_markets.sql"):
        text = (ROOT / "sql" / name).read_text().lower()
        assert "binance" not in text and "false" in text
