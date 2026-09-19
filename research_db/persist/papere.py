from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from research_db.paper.session import PaperSession
from research_db.persist.ids import stable_id
DDL = Path(__file__).resolve().parents[2] / "sql" / "activation_gate_e_sqlite_twin.sql"
def _now():
    return datetime.now(timezone.utc).isoformat()
def install_activation_e(self):
    self.conn.executescript(DDL.read_text(encoding="utf-8")); self.conn.commit()
def persist_paper_session(self, session: PaperSession):
    now = _now()
    with self.conn:
        self._upsert("ops__schema_gate", {"id": stable_id("gate","activation_e"),"phase":"activation_e","approved":1,"ingestion_enabled":0,"notes":"Gate E zero-capital paper","created_at":now})
        for d in session.definitions:
            self._upsert("research__paper_decision_definition", {"id": stable_id("pdef", d["code"], d["version"]), "code": d["code"], "version": d["version"], "policy": d["policy"], "question": d["question"], "created_at": now})
        for r in session.records:
            if r["capital"] != 0 or r["live_order"]:
                raise RuntimeError("zero-capital invariant")
            self._upsert("research__paper_session_record", {"id": stable_id("psess", r["run_code"]), "run_code": r["run_code"], "definition_code": r["definition"], "version": r["version"], "policy": r["policy"], "action": r["action"], "subject_code": r["subject"], "snapshot_code": r["snapshot"], "as_of_knowledge_time": r["as_of"], "context_digest": r["context_digest"], "input_digest": r["input_digest"], "capital": 0, "live_order": 0, "tape": "fixture"})
        for i, p in enumerate(session.predictions):
            self._upsert("research__paper_prediction", {"id": stable_id("ppred", p["run_code"], str(i)), "run_code": p["run_code"], "target": p["target"], "horizon": p["horizon"], "uncertainty": p["uncertainty"], "model": p["model"], "status": p["status"]})
        for i, k in enumerate(session.risks):
            self._upsert("research__paper_risk", {"id": stable_id("prisk", k["run_code"], str(i)), "run_code": k["run_code"], "policy_version": k["policy_version"], "status": k["status"], "note": k["note"], "capital": 0, "executable": 0})
        for i, o in enumerate(session.outcomes):
            self._upsert("research__paper_outcome", {"id": stable_id("pout", o["run_code"], str(i)), "run_code": o["run_code"], "event_time": o["event_time"], "knowledge_time": o["knowledge_time"], "note": o["note"], "value": o.get("value")})
        for i, e in enumerate(session.evaluations):
            self._upsert("research__paper_evaluation", {"id": stable_id("peval", e["run_code"], str(i)), "run_code": e["run_code"], "status": e["status"], "note": e["note"], "knowledge_time": e["knowledge_time"], "input_digest": e["input_digest"]})
    return {"records": self._count("research__paper_session_record"), "evaluations": self._count("research__paper_evaluation")}
def bind(cls):
    cls.install_activation_e = install_activation_e
    cls.persist_paper_session = persist_paper_session
