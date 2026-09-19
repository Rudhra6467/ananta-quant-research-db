"""Persist Phase 11 annotated events."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from research_db.events.engine import EventMemory
from research_db.persist.ids import stable_id
DDL = Path(__file__).resolve().parents[2] / "sql" / "011_phase11_sqlite_twin.sql"
def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
def install_phase11(self) -> None:
    self.conn.executescript(DDL.read_text(encoding="utf-8"))
    self.conn.commit()
def persist_events(self, memory: EventMemory) -> dict[str, int]:
    now = _now()
    with self.conn:
        self._upsert("ops__schema_gate", {"id": stable_id("gate", "phase11"), "phase": "phase11", "approved": 1, "ingestion_enabled": 0, "notes": "Event representation only", "created_at": now})
        for e in memory.events:
            eid = stable_id("event", e["code"])
            self.ids[f"event:{e['code']}"] = eid
            self._upsert("research__market_event", {"id": eid, "code": e["code"], "kind": e["kind"], "subject_kind": e["subject_kind"], "subject_code": e["subject"], "onset_time": e["onset_time"], "event_time": e["event_time"], "peak_time": e.get("peak_time"), "knowledge_time": e["knowledge_time"], "notes": e.get("notes") or "", "created_at": now})
        for i, w in enumerate(memory.windows):
            self._upsert("research__event_window", {"id": stable_id("ewin", w["event"], w["kind"], str(i)), "event_id": self.ids[f"event:{w['event']}"], "kind": w["kind"], "start_time": w["start_time"], "end_time": w["end_time"]})
        for i, c in enumerate(memory.context):
            self._upsert("research__event_context_link", {"id": stable_id("ectx", c["event"], c["source_kind"], c["source_ref"], str(i)), "event_id": self.ids[f"event:{c['event']}"], "source_kind": c["source_kind"], "source_ref": c["source_ref"], "knowledge_time": c["knowledge_time"]})
    return {"events": self._count("research__market_event"), "windows": self._count("research__event_window")}
def events_as_of(self, knowledge_time: str) -> list[str]:
    rows = self.conn.execute("SELECT code FROM research__market_event WHERE knowledge_time <= ? ORDER BY code", (knowledge_time,))
    return [r["code"] for r in rows]
def bind(store_cls) -> None:
    store_cls.install_phase11 = install_phase11
    store_cls.persist_events = persist_events
    store_cls.events_as_of = events_as_of
