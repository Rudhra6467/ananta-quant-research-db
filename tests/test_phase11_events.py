from pathlib import Path
import pytest
from research_db.events.engine import EventDenied, EventMemory, fixture_events
from research_db.lifecycle.engine import run_fixture_lifecycle
from research_db.persist import LiveQueryDenied, open_event_store
ROOT = Path(__file__).resolve().parents[1]

def test_onset_distinct_from_peak_and_windows_exist() -> None:
    bars = run_fixture_lifecycle().canonical_bars
    mem = fixture_events(bars)
    codes = {e["code"] for e in mem.events}
    assert codes == {"E_BREAK_T20", "E_SHIFT_T24"}
    brk = next(e for e in mem.events if e["code"] == "E_BREAK_T20")
    sh = next(e for e in mem.events if e["code"] == "E_SHIFT_T24")
    assert brk["kind"] == "break" and sh["kind"] == "shift"
    assert brk["event_time"] != sh["event_time"]
    assert {w["kind"] for w in mem.windows if w["event"] == "E_BREAK_T20"} == {"pre", "event", "post"}

def test_knowledge_time_hides_later_event() -> None:
    bars = run_fixture_lifecycle().canonical_bars
    mem = fixture_events(bars)
    early_k = bars[20]["as_of_time"]
    late_k = bars[24]["as_of_time"]
    assert [e["code"] for e in mem.events_as_of(early_k)] == ["E_BREAK_T20"]
    assert {e["code"] for e in mem.events_as_of(late_k)} == {"E_BREAK_T20", "E_SHIFT_T24"}

def test_invalid_event_kind_rejected() -> None:
    mem = EventMemory()
    with pytest.raises(EventDenied):
        mem.record(code="X", kind="alert", subject_kind="instrument", subject="BTC", onset_time="t", event_time="t", knowledge_time="t")

def test_persist_and_live_denial() -> None:
    memory = run_fixture_lifecycle()
    store = open_event_store()
    store.persist_memory(memory)
    ev = fixture_events(memory.canonical_bars)
    stats = store.persist_events(ev)
    assert stats["events"] == 2 and stats["windows"] == 6
    early = memory.canonical_bars[20]["as_of_time"]
    assert store.events_as_of(early) == ["E_BREAK_T20"]
    assert int(store.conn.execute("SELECT ingestion_enabled FROM ops__schema_gate WHERE phase='phase11'").fetchone()["ingestion_enabled"]) == 0
    with pytest.raises(Exception):
        store.conn.execute("DELETE FROM research__market_event")
    with pytest.raises(LiveQueryDenied):
        store.live().execute("SELECT code FROM research__market_event")

def test_phase11_sql_is_not_a_detector() -> None:
    text = (ROOT / "sql" / "011_phase11_events.sql").read_text().lower()
    assert "cusum" not in text and "pelt" not in text and "bocpd" not in text
    assert "binance" not in text and "false" in text
