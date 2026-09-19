from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from research_db.agent.catalog import all_capabilities
from research_db.agent.context import AgentContext
from research_db.persist.ids import stable_id
DDL = Path(__file__).resolve().parents[2] / "sql" / "activation_gate_d_sqlite_twin.sql"
def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
def install_activation_d(self) -> None:
    self.conn.executescript(DDL.read_text(encoding="utf-8"))
    self.conn.commit()
def persist_agent_catalog(self) -> int:
    now = _now()
    with self.conn:
        self._upsert("ops__schema_gate", {"id": stable_id("gate", "activation_d"), "phase": "activation_d", "approved": 1, "ingestion_enabled": 0, "notes": "Gate D read-only catalog", "created_at": now})
        n = 0
        for cap in all_capabilities():
            self._upsert("interface__agent_capability", {"id": stable_id("acap", cap.name), "name": cap.name, "layer": cap.layer, "status": cap.status, "mutation": 1 if cap.mutation else 0})
            n += 1
    return n
def persist_agent_context(self, ctx: AgentContext):
    now = _now()
    d = ctx.as_dict()
    with self.conn:
        self._upsert("interface__agent_context", {"id": stable_id("actx", d["digest"]), "subject_code": d["subject"], "snapshot_code": d["snapshot"], "as_of_knowledge_time": d["knowledge_time"], "catalog_version": d["catalog_version"], "uncertainty": d["uncertainty"], "digest": d["digest"], "live_claim": 0, "mutated": 0, "created_at": now})
        for i, item in enumerate(d["items"]):
            self._upsert("interface__agent_context_item", {"id": stable_id("aitm", d["digest"], item["capability"], item["ref"], str(i)), "context_digest": d["digest"], "capability": item["capability"], "layer": item["layer"], "ref": item["ref"], "knowledge_time": item["knowledge_time"]})
    return {"items": len(d["items"])}
def bind(cls) -> None:
    cls.install_activation_d = install_activation_d
    cls.persist_agent_catalog = persist_agent_catalog
    cls.persist_agent_context = persist_agent_context
