from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from research_db.activation.charter import ActivationCharter, SYMBOL_MAP
from research_db.persist.ids import stable_id
DDL = Path(__file__).resolve().parents[2] / "sql" / "activation_n2_sqlite_twin.sql"
def _now():
    return datetime.now(timezone.utc).isoformat()
def install_activation_n2(self):
    self.conn.executescript(DDL.read_text(encoding="utf-8")); self.conn.commit()
def persist_charter(self, charter: ActivationCharter):
    now = _now()
    with self.conn:
        self._upsert("ops__schema_gate", {"id": stable_id("gate","n2"),"phase":"n2_charter","approved":1,"ingestion_enabled":0,"notes":"N2 charter-scoped live only","created_at":now})
        self._upsert("ops__activation_charter", {"id": stable_id("charter", charter.code, charter.version),"code": charter.code,"version": charter.version,"source_code": charter.source_code,"snapshot_code": charter.snapshot_code,"run_code": charter.run_code,"window_start": charter.window_start,"continuous": 1 if charter.continuous else 0,"n3_authorized": 1 if charter.n3_authorized else 0})
        for inst, wire in SYMBOL_MAP.items():
            self._upsert("ops__source_symbol_map", {"id": stable_id("smap", charter.source_code, wire),"source_code": charter.source_code,"wire_symbol": wire,"instrument_code": inst})
    return 1
def persist_quality_report(self, report: dict):
    now = _now()
    with self.conn:
        self._upsert("ops__ingest_quality_report", {"id": stable_id("qrep", report["run_code"]), "run_code": report["run_code"], "snapshot_code": report["snapshot_code"], "payload": json.dumps(report, default=str), "created_at": now})
        for inst, unix in (report.get("watermarks") or {}).items():
            src = report.get("source_identity") or "charter.source"
            self._upsert("ops__ingest_watermark", {"id": stable_id("wm", inst, src), "instrument_code": inst, "source_code": src, "last_unix": int(unix)})
    return 1
def persist_snapshot_bars(self, batch, report):
    with self.conn:
        for rec in batch.accepted:
            pl = rec.payload
            self._upsert("ops__snapshot_bar", {"id": stable_id("sbar", batch.snapshot_code, rec.source_record_id), "snapshot_code": batch.snapshot_code, "run_code": batch.run_code, "instrument_code": rec.instrument, "source_record_id": rec.source_record_id, "event_time": rec.event_time, "knowledge_time": rec.knowledge_time, "open": float(pl["open"]), "high": float(pl["high"]), "low": float(pl["low"]), "close": float(pl["close"]), "volume": float(pl["volume"]), "checksum": rec.checksum})
        self._upsert("ops__snapshot_status", {"id": stable_id("sstat", batch.snapshot_code), "snapshot_code": batch.snapshot_code, "run_code": batch.run_code, "complete": 1 if report.get("snapshot_complete") else 0, "accepted": len(batch.accepted), "notes": report.get("source_limitation") or ""})
    return self._count("ops__snapshot_bar")
def snapshot_bars_as_of(self, snapshot_code, as_of, instrument=None):
    q = "SELECT * FROM ops__snapshot_bar WHERE snapshot_code=? AND knowledge_time<=?"
    args = [snapshot_code, as_of]
    if instrument:
        q += " AND instrument_code?".replace("?", "=?") if False else " AND instrument_code=?"
        args.append(instrument)
    return list(self.conn.execute(q, args))
def bind(cls):
    cls.install_activation_n2 = install_activation_n2
    cls.persist_charter = persist_charter
    cls.persist_quality_report = persist_quality_report
    cls.persist_snapshot_bars = persist_snapshot_bars
    cls.snapshot_bars_as_of = snapshot_bars_as_of
