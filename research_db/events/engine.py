"""Phase 11 event representation. Not a shift detector."""
from __future__ import annotations
from typing import Any
EVENT_KINDS = {"anomaly", "break", "shift", "regime_transition"}
WINDOW_KINDS = {"pre", "event", "post"}
CONTEXT_KINDS = {"bar", "feature", "state", "regime", "group"}

class EventDenied(PermissionError):
    pass

class EventMemory:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self.windows: list[dict[str, Any]] = []
        self.context: list[dict[str, Any]] = []
    def record(self, *, code: str, kind: str, subject_kind: str, subject: str, onset_time: str, event_time: str, knowledge_time: str, peak_time: str | None = None, notes: str = "") -> dict[str, Any]:
        if kind not in EVENT_KINDS:
            raise EventDenied(f"invalid event kind {kind}")
        row = {"code": code, "kind": kind, "subject_kind": subject_kind, "subject": subject, "onset_time": onset_time, "event_time": event_time, "peak_time": peak_time, "knowledge_time": knowledge_time, "notes": notes}
        self.events.append(row)
        return row
    def add_window(self, event: str, kind: str, start_time: str, end_time: str) -> dict[str, Any]:
        if kind not in WINDOW_KINDS:
            raise EventDenied(f"invalid window {kind}")
        if end_time < start_time:
            raise EventDenied("window end precedes start")
        row = {"event": event, "kind": kind, "start_time": start_time, "end_time": end_time}
        self.windows.append(row)
        return row
    def link_context(self, event: str, source_kind: str, source_ref: str, knowledge_time: str) -> dict[str, Any]:
        if source_kind not in CONTEXT_KINDS:
            raise EventDenied(f"invalid context {source_kind}")
        row = {"event": event, "source_kind": source_kind, "source_ref": source_ref, "knowledge_time": knowledge_time}
        self.context.append(row)
        return row
    def events_as_of(self, knowledge_time: str) -> list[dict[str, Any]]:
        return [e for e in self.events if e["knowledge_time"] <= knowledge_time]

def fixture_events(bars: list[dict[str, Any]]) -> EventMemory:
    mem = EventMemory()
    if len(bars) < 30:
        raise EventDenied("fixture too short")
    onset, peak, later = bars[20], bars[24], bars[28]
    t_on, t_pk, t_aft = onset["event_time"], peak["event_time"], later["event_time"]
    k_on, k_pk = onset["as_of_time"], peak["as_of_time"]
    mem.record(code="E_BREAK_T20", kind="break", subject_kind="instrument", subject=onset["instrument"], onset_time=t_on, event_time=t_on, knowledge_time=k_on, notes="fixture annotation of onset; not a detector output")
    mem.add_window("E_BREAK_T20", "pre", bars[16]["event_time"], bars[19]["event_time"])
    mem.add_window("E_BREAK_T20", "event", t_on, t_on)
    mem.add_window("E_BREAK_T20", "post", bars[21]["event_time"], bars[23]["event_time"])
    mem.link_context("E_BREAK_T20", "bar", t_on, k_on)
    mem.link_context("E_BREAK_T20", "regime", "rsi_region", k_on)
    mem.record(code="E_SHIFT_T24", kind="shift", subject_kind="instrument", subject=peak["instrument"], onset_time=t_on, event_time=t_pk, peak_time=t_pk, knowledge_time=k_pk, notes="same episode peak; distinct from onset")
    mem.add_window("E_SHIFT_T24", "pre", t_on, bars[23]["event_time"])
    mem.add_window("E_SHIFT_T24", "event", t_pk, t_pk)
    mem.add_window("E_SHIFT_T24", "post", bars[25]["event_time"], t_aft)
    mem.link_context("E_SHIFT_T24", "bar", t_pk, k_pk)
    return mem
