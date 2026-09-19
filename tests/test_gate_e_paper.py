from pathlib import Path
import pytest
from research_db.agent.engine import AgentDenied
from research_db.ingest.orchestrator import INGESTION_ENABLED
from research_db.paper.session import PaperDenied, fixture_paper_path
from research_db.persist import LiveQueryDenied, open_paper_session_store
ROOT = Path(__file__).resolve().parents[1]

def test_fixture_path_wait_then_inconclusive() -> None:
    session, demo = fixture_paper_path()
    rec = demo["record"]
    assert rec["capital"] == 0 and rec["live_order"] is False and rec["action"] == "WAIT"
    assert demo["evaluation"]["status"] == "inconclusive"
    assert session.outcomes[0]["knowledge_time"] > rec["as_of"]

def test_outcome_cannot_enter_decision_context() -> None:
    session, demo = fixture_paper_path()
    with pytest.raises(AgentDenied, match="PIT"):
        demo["context"].observe("current_market_state", demo["later"]["event_time"], demo["later"]["as_of_time"])

def test_zero_capital_and_no_broker() -> None:
    session, _ = fixture_paper_path()
    assert all(r["capital"] == 0 and r["live_order"] is False for r in session.records)
    assert all(k["executable"] is False for k in session.risks)
    assert session.predictions[0]["engine"] is None

def test_rerun_new_identity_same_digest() -> None:
    session, demo = fixture_paper_path()
    nxt = session.rerun(demo["record"]["run_code"], demo["context"])
    assert nxt["run_code"] != demo["record"]["run_code"]
    assert nxt["input_digest"] == demo["record"]["input_digest"]

def test_outcome_before_as_of_rejected() -> None:
    session, demo = fixture_paper_path()
    with pytest.raises(PaperDenied):
        session.realize_outcome(demo["record"]["run_code"], event_time=demo["early"]["event_time"], knowledge_time=demo["early"]["as_of_time"], note="too early")

def test_persist_and_no_phase21() -> None:
    session, demo = fixture_paper_path()
    store = open_paper_session_store()
    store.persist_paper(session.ledger)
    stats = store.persist_paper_session(session)
    assert stats["records"] >= 1
    row = store.conn.execute("SELECT capital, live_order FROM research__paper_session_record").fetchone()
    assert float(row["capital"]) == 0 and int(row["live_order"]) == 0
    assert store.conn.execute("SELECT status FROM research__paper_evaluation").fetchone()["status"] == "inconclusive"
    assert int(store.conn.execute("SELECT ingestion_enabled FROM ops__schema_gate WHERE phase='activation_e'").fetchone()["ingestion_enabled"]) == 0
    with pytest.raises(LiveQueryDenied):
        store.live().execute("SELECT action FROM research__paper_session_record")
    assert INGESTION_ENABLED is False
    assert list((ROOT / "sql").glob("021*")) == []
