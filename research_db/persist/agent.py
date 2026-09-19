from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from research_db.agent.engine import AgentConsult
from research_db.persist.ids import stable_id
DDL = Path(__file__).resolve().parents[2] / "sql" / "017_phase17_sqlite_twin.sql"
def _now():
    return datetime.now(timezone.utc).isoformat()
def install_phase17(self):
    self.conn.executescript(DDL.read_text(encoding="utf-8")); self.conn.commit()
def persist_consults(self, agent: AgentConsult):
    now = _now()
    with self.conn:
        self._upsert("ops__schema_gate", {"id": stable_id("gate","phase17"),"phase":"phase17","approved":1,"ingestion_enabled":0,"notes":"Consult log","created_at":now})
        for i, row in enumerate(agent.log):
            self._upsert("interface__consult_event", {"id": stable_id("ce", row["query"], row["knowledge_time"], str(i)), "query_name": row["query"], "knowledge_time": row["knowledge_time"], "payload": json.dumps(row["payload"]), "mutated": 1 if row["mutated"] else 0})
    return {"consults": self._count("interface__consult_event")}
def bind(cls):
    cls.install_phase17 = install_phase17
    cls.persist_consults = persist_consults
