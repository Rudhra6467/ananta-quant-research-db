"""Phase 14 memory tiers. Compress routine history; never delete raw facts."""
from __future__ import annotations
from statistics import mean
from typing import Any
class MemoryTierDenied(PermissionError):
    pass
class MemoryTierPolicy:
    def __init__(self) -> None:
        self.policies = [
            {"code": "ROLLING_12Y", "tier": "hot_analytical", "horizon": "12y", "deletes_raw": False},
            {"code": "COMPRESS_OLDER", "tier": "compressed_memory", "horizon": "12y+", "deletes_raw": False},
            {"code": "RAW_ARCHIVE", "tier": "raw_archive", "horizon": "all", "deletes_raw": False},
            {"code": "EVENT_RICH", "tier": "event_rich", "horizon": "important_events", "deletes_raw": False},
        ]
        self.summaries = []
    def summarize(self, bars, *, split: int = 24):
        if split >= len(bars):
            raise MemoryTierDenied("need a split inside the fixture")
        older, recent = bars[:split], bars[split:]
        older_closes = [float(b["close"]) for b in older]
        self.summaries.append({"code": "FIXTURE_OLDER_SUMMARY", "tier": "compressed_memory", "n": len(older), "mean_close": mean(older_closes), "min_close": min(older_closes), "max_close": max(older_closes), "start": older[0]["event_time"], "end": older[-1]["event_time"], "raw_retained": True})
        self.summaries.append({"code": "FIXTURE_RECENT_HOT", "tier": "hot_analytical", "n": len(recent), "mean_close": mean(float(b["close"]) for b in recent), "min_close": min(float(b["close"]) for b in recent), "max_close": max(float(b["close"]) for b in recent), "start": recent[0]["event_time"], "end": recent[-1]["event_time"], "raw_retained": True})
        return self.summaries
