from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime
from research_db.ingest.contract import IngestBatch
def quality_report(batch: IngestBatch, *, mapping_failures=None, watermarks=None):
    accepted = batch.accepted
    by_inst = Counter(r.instrument for r in accepted)
    times = [r.event_time for r in accepted]
    kts = [r.knowledge_time for r in accepted]
    return {"run_code": batch.run_code, "snapshot_code": batch.snapshot_code, "source_identity": "kraken.ohlc.spot", "provider_kind": batch.provider_kind, "rows_acquired": len(accepted)+len(batch.quarantined)+batch.duplicates, "rows_accepted": len(accepted), "rows_quarantined": len(batch.quarantined), "duplicates": batch.duplicates, "timestamp_violations": sum(1 for q in batch.quarantined if q["reason"] in {"knowledge_before_event","not_hour_aligned","bad_event_time"}), "malformed_records": sum(1 for q in batch.quarantined if q["reason"] in {"missing_ohlcv","high_lt_low","range_inconsistent","negative_volume"}), "symbol_mapping_failures": list(mapping_failures or []), "revisions": 0, "earliest_event_time": min(times) if times else None, "latest_event_time": max(times) if times else None, "earliest_knowledge_time": min(kts) if kts else None, "latest_knowledge_time": max(kts) if kts else None, "completeness_by_instrument": dict(by_inst), "completeness_by_timeframe": dict(Counter(r.timeframe for r in accepted)), "watermarks": watermarks or {}, "gaps": _gaps(accepted), "n3_authorized": False}
def _gaps(accepted):
    by = defaultdict(list)
    for r in accepted:
        by[r.instrument].append(datetime.fromisoformat(r.event_time))
    out = {}
    for inst, ts in by.items():
        ts = sorted(set(ts)); missing = 0
        for a, b in zip(ts, ts[1:]):
            hours = int((b-a).total_seconds()//3600)
            if hours > 1: missing += hours-1
        out[inst] = missing
    return out
