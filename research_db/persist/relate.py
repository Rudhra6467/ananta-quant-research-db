"""Persist Phase 12-13 declared links. No scores."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from research_db.persist.ids import stable_id
from research_db.relate.engine import AnalogueIndex, RelationGraph
DDL12 = Path(__file__).resolve().parents[2] / "sql" / "012_phase12_sqlite_twin.sql"
DDL13 = Path(__file__).resolve().parents[2] / "sql" / "013_phase13_sqlite_twin.sql"
def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
def install_phase12(self) -> None:
    self.conn.executescript(DDL12.read_text(encoding="utf-8"))
    self.conn.commit()
def install_phase13(self) -> None:
    self.conn.executescript(DDL13.read_text(encoding="utf-8"))
    self.conn.commit()
def persist_relations(self, graph: RelationGraph) -> dict[str, int]:
    now = _now()
    with self.conn:
        self._upsert("ops__schema_gate", {"id": stable_id("gate", "phase12"), "phase": "phase12", "approved": 1, "ingestion_enabled": 0, "notes": "Declared links only", "created_at": now})
        for i, row in enumerate(graph.links):
            self._upsert("research__cross_subject_link", {"id": stable_id("csl", row["left"], row["relation"], row["right"], row["knowledge_time"], str(i)), "left_kind": row["left_kind"], "left_code": row["left"], "relation": row["relation"], "right_kind": row["right_kind"], "right_code": row["right"], "via": row.get("via"), "effective_time": row["effective_time"], "expiry_time": row.get("expiry_time"), "knowledge_time": row["knowledge_time"], "created_at": now})
    return {"links": self._count("research__cross_subject_link")}
def persist_analogues(self, index: AnalogueIndex) -> dict[str, int]:
    now = _now()
    with self.conn:
        self._upsert("ops__schema_gate", {"id": stable_id("gate", "phase13"), "phase": "phase13", "approved": 1, "ingestion_enabled": 0, "notes": "Analogue definition links only", "created_at": now})
        for i, row in enumerate(index.links):
            self._upsert("research__event_analogue_link", {"id": stable_id("eal", row["event_a"], row["event_b"], str(i)), "event_a": row["event_a"], "event_b": row["event_b"], "basis": row["basis"], "knowledge_time": row["knowledge_time"]})
    return {"analogues": self._count("research__event_analogue_link")}
def bind(store_cls) -> None:
    store_cls.install_phase12 = install_phase12
    store_cls.install_phase13 = install_phase13
    store_cls.persist_relations = persist_relations
    store_cls.persist_analogues = persist_analogues
