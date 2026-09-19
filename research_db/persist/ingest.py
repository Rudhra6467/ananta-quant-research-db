from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from research_db.ingest.orchestrator import INGESTION_ENABLED, IngestionOrchestrator
from research_db.persist.ids import stable_id
DDL = Path(__file__).resolve().parents[2] / "sql" / "activation_gate_a_sqlite_twin.sql"
def _now():
    return datetime.now(timezone.utc).isoformat()
def install_activation_a(self):
    self.conn.executescript(DDL.read_text(encoding="utf-8")); self.conn.commit()
def persist_ingest_batch(self, orch: IngestionOrchestrator):
    now = _now()
    with self.conn:
        self._upsert("ops__schema_gate", {"id": stable_id("gate", "activation_a"), "phase": "activation_a", "approved": 1, "ingestion_enabled": 0, "notes": "Gate A scaffold", "created_at": now})
        n = 0
        for batch in orch.batches:
            self._upsert("ops__ingest_audit", {"id": stable_id("iaud", batch.run_code), "run_code": batch.run_code, "snapshot_code": batch.snapshot_code, "provider_kind": batch.provider_kind, "accepted": len(batch.accepted), "quarantined": len(batch.quarantined), "duplicates": batch.duplicates, "ingestion_enabled": 1 if INGESTION_ENABLED else 0, "created_at": now})
            for i, q in enumerate(batch.quarantined):
                self._upsert("ops__quarantine_record", {"id": stable_id("qrec", batch.run_code, q["source_record_id"], str(i)), "run_code": batch.run_code, "source_record_id": q["source_record_id"], "reason": q["reason"], "event_time": q.get("event_time"), "created_at": now})
            n += 1
    return {"batches": n, "ingestion_enabled": int(INGESTION_ENABLED)}
def bind(cls):
    cls.install_activation_a = install_activation_a
    cls.persist_ingest_batch = persist_ingest_batch
