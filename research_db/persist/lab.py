from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from research_db.lab.engine import Laboratory
from research_db.persist.ids import stable_id
DDL = Path(__file__).resolve().parents[2] / "sql" / "activation_gate_b_sqlite_twin.sql"
def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
def install_activation_b(self) -> None:
    self.conn.executescript(DDL.read_text(encoding="utf-8"))
    self.conn.commit()
def persist_laboratory(self, lab: Laboratory) -> dict[str, int]:
    now = _now()
    snap = self.ids.get("snapshot")
    with self.conn:
        self._upsert("ops__schema_gate", {"id": stable_id("gate", "activation_b"), "phase": "activation_b", "approved": 1, "ingestion_enabled": 0, "notes": "Gate B laboratory fixture only", "created_at": now})
        for d in lab.definitions:
            self._upsert("research__lab_experiment_definition", {"id": stable_id("edef", d["code"], d["version"]), "code": d["code"], "version": d["version"], "question": d["question"], "snapshot_code": d["snapshot"], "hypothesis_code": d.get("hypothesis"), "measurement_code": d.get("measurement"), "status": d["status"], "created_at": now})
        for c in lab.cohorts:
            self._upsert("research__lab_cohort", {"id": stable_id("ecoh", c["code"], c["experiment"], c["version"]), "code": c["code"], "experiment_code": c["experiment"], "version": c["version"], "note": c.get("note") or "", "created_at": now})
        for r in lab.runs:
            self._upsert("research__experiment_run", {"id": stable_id("erun", r["run_code"]), "code": r["run_code"], "dataset_snapshot_id": snap, "code_commit": r["version"], "config_hash": r.get("input_digest"), "status": r["status"], "created_at": now})
        for i, l in enumerate(lab.links):
            self._upsert("research__lab_input_link", {"id": stable_id("elink", l["run_code"], l["source_kind"], l["source_ref"], str(i)), "run_code": l["run_code"], "source_kind": l["source_kind"], "source_ref": l["source_ref"], "knowledge_time": l["knowledge_time"]})
        for res in lab.results:
            self._upsert("research__lab_result", {"id": stable_id("eres", res["run_code"]), "run_code": res["run_code"], "experiment_code": res["experiment"], "version": res["version"], "cohort_code": res["cohort"], "snapshot_code": res["snapshot"], "as_of_knowledge_time": res["as_of"], "status": res["status"], "note": res["note"], "input_digest": res["input_digest"], "tape": res.get("tape") or "fixture", "created_at": now})
    return {"definitions": self._count("research__lab_experiment_definition"), "cohorts": self._count("research__lab_cohort"), "runs": self._count("research__experiment_run"), "results": self._count("research__lab_result")}
def bind(cls) -> None:
    cls.install_activation_b = install_activation_b
    cls.persist_laboratory = persist_laboratory
