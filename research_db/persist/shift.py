from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from research_db.persist.ids import stable_id
from research_db.shift.engine import ShiftRegistry
DDL = Path(__file__).resolve().parents[2] / "sql" / "activation_gate_c_sqlite_twin.sql"
def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
def install_activation_c(self) -> None:
    self.conn.executescript(DDL.read_text(encoding="utf-8"))
    self.conn.commit()
def persist_shift_registry(self, reg: ShiftRegistry) -> dict[str, int]:
    now = _now()
    with self.conn:
        self._upsert("ops__schema_gate", {"id": stable_id("gate", "activation_c"), "phase": "activation_c", "approved": 1, "ingestion_enabled": 0, "notes": "Gate C fixture detector only", "created_at": now})
        for s in reg.specs:
            self._upsert("research__shift_detector_definition", {"id": stable_id("sdef", s["code"], s["version"]), "code": s["code"], "version": s["version"], "kind": s["kind"], "params": json.dumps(s["params"]), "windows": json.dumps(s["windows"]), "subject_kind": s["subject_kind"], "created_at": now})
        for r in reg.runs:
            self._upsert("research__shift_detection_run", {"id": stable_id("srun", r["run_code"]), "run_code": r["run_code"], "detector_code": r["detector"], "version": r["version"], "snapshot_code": r["snapshot"], "as_of_knowledge_time": r["as_of"], "subject_kind": r["subject_kind"], "subject_code": r["subject"], "input_digest": r.get("input_digest"), "status": r["status"], "live_claim": 1 if r.get("live_claim") else 0, "tape": r.get("tape") or "fixture", "created_at": now})
        for c in reg.candidates:
            self._upsert("research__shift_candidate", {"id": stable_id("scand", c["candidate_code"]), "candidate_code": c["candidate_code"], "run_code": c["run_code"], "event_code": c["event_code"], "kind": c["kind"], "event_time": c["event_time"], "knowledge_time": c["knowledge_time"], "status": c["status"], "certainty": 1 if c.get("certainty") else 0, "live_claim": 0, "tape": "fixture", "note": c.get("note") or ""})
        for i, rv in enumerate(reg.reviews):
            self._upsert("research__shift_review_event", {"id": stable_id("srev", rv["candidate_code"], rv["status"], str(i)), "candidate_code": rv["candidate_code"], "status": rv["status"], "note": rv["note"], "knowledge_time": rv["knowledge_time"], "live_claim": 0, "created_at": now})
    return {"specs": self._count("research__shift_detector_definition"), "runs": self._count("research__shift_detection_run"), "candidates": self._count("research__shift_candidate"), "reviews": self._count("research__shift_review_event")}
def bind(cls) -> None:
    cls.install_activation_c = install_activation_c
    cls.persist_shift_registry = persist_shift_registry
