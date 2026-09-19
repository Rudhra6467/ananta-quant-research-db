"""Named snapshot quality. Does not invent bars to fill gaps."""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any
from research_db.activation.charter import INSTRUMENTS, WINDOW_START
from research_db.ingest.contract import IngestBatch

def last_complete_hour(now=None):
    now = now or datetime.now(timezone.utc)
    return now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)

def expected_hours(start: str, end: datetime) -> int:
    s = datetime.fromisoformat(start.replace("Z", "+00:00"))
    return int((end - s).total_seconds() // 3600) + 1

def classify_gap(hours: int) -> str:
    if hours <= 0: return "none"
    if hours == 1: return "single_hour"
    if hours <= 6: return "short_outage_or_missing_provider"
    return "missing_provider_or_listing_gap"

def instrument_report(instrument, event_times, *, start, end):
    ts = sorted({datetime.fromisoformat(t) for t in event_times})
    expected = expected_hours(start, end)
    intra = 0
    classes = Counter()
    for a, b in zip(ts, ts[1:]):
        hole = int((b - a).total_seconds() // 3600) - 1
        if hole > 0:
            intra += hole
            classes[classify_gap(hole)] += 1
    earliest = ts[0].isoformat() if ts else None
    latest = ts[-1].isoformat() if ts else None
    lead = tail = 0
    s = datetime.fromisoformat(start.replace("Z", "+00:00"))
    if ts:
        lead = max(0, int((ts[0] - s).total_seconds() // 3600))
        tail = max(0, int((end - ts[-1]).total_seconds() // 3600))
    acquired = len(ts)
    return {"instrument": instrument, "requested_start": start, "actual_earliest_event": earliest, "actual_latest_complete_event": latest, "expected_bar_count": expected, "acquired_count": acquired, "intra_series_gaps": intra, "leading_missing_hours": lead, "trailing_missing_hours": tail, "gap_classes": dict(classes), "complete_vs_charter": acquired == expected and intra == 0 and lead == 0 and tail == 0}

def snapshot_quality(batch: IngestBatch, *, window_start: str = WINDOW_START, end=None):
    end = end or last_complete_hour()
    by = defaultdict(list)
    for rec in batch.accepted:
        by[rec.instrument].append(rec.event_time)
    per = [instrument_report(inst, by.get(inst, []), start=window_start, end=end) for inst in INSTRUMENTS]
    return {"snapshot_code": batch.snapshot_code, "run_code": batch.run_code, "source_identity": "kraken.ohlc.spot", "window_start": window_start, "window_end": end.isoformat(), "instruments": per, "rows_accepted": len(batch.accepted), "rows_quarantined": len(batch.quarantined), "duplicates": batch.duplicates, "cross_instrument_coverage": sum(1 for p in per if p["acquired_count"] > 0), "snapshot_complete": all(p["complete_vs_charter"] for p in per), "n3_authorized": False, "source_limitation": "Kraken public /0/public/OHLC returns at most 720 completed 1h candles (~30d) regardless of since="}
