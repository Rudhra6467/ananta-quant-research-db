from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from research_db.persist.ids import stable_id
from research_db.scaleout.engine import ScaleoutRegistry
DDL = Path(__file__).resolve().parents[2] / "sql" / "activation_gate_f_sqlite_twin.sql"
CHECKLIST = [("ingestion","design_only"),("data_quality","fixture_gates"),("pit","enforced"),("provenance","enforced"),("state","fixture_only"),("shifts","annotated_replay"),("laboratory","fixture_only"),("agent_context","read_only"),("paper_decisions","zero_capital"),("outcomes","fixture_only"),("evaluation","inconclusive_ok"),("monitoring","deferred"),("failure_handling","quarantine_designed"),("auditability","append_only"),("security","roles_fixture"),("rollback","new_run_not_delete"),("operational_controls","gates_required")]
def _now():
    return datetime.now(timezone.utc).isoformat()
def install_activation_f(self):
    self.conn.executescript(DDL.read_text(encoding="utf-8")); self.conn.commit()
def persist_scaleout(self, reg: ScaleoutRegistry):
    now = _now()
    with self.conn:
        self._upsert("ops__schema_gate", {"id": stable_id("gate","activation_f"),"phase":"activation_f","approved":1,"ingestion_enabled":0,"notes":"Gate F readiness only","created_at":now})
        for i in reg.instruments:
            self._upsert("ops__scaleout_instrument_plan", {"id": stable_id("sinst", i["code"]), "code": i["code"], "venue": i["venue"], "market": i["market"], "ingested": 1 if i.get("ingested") else 0, "fixture": 1 if i.get("fixture") else 0})
        for w in reg.worlds:
            self._upsert("ops__scaleout_world", {"id": stable_id("sworld", w["code"]), "code": w["code"], "isolated": 1})
        for step, status in reg.lineage_status.items():
            self._upsert("ops__scaleout_lineage", {"id": stable_id("slin", step), "step": step, "status": status})
        for item, state in CHECKLIST:
            self._upsert("ops__production_checklist", {"id": stable_id("pchk", item), "item": item, "state": state})
    return {"instruments": self._count("ops__scaleout_instrument_plan"), "ingested": int(reg.ingested())}
def bind(cls):
    cls.install_activation_f = install_activation_f
    cls.persist_scaleout = persist_scaleout
