"""Phase 12-13 subject links and event analogues. No correlation/similarity engine."""
from __future__ import annotations
from typing import Any
RELATIONS = {"co_member", "related", "leads", "lags", "concurrent"}
class RelationDenied(PermissionError):
    pass
class RelationGraph:
    def __init__(self) -> None:
        self.links: list[dict[str, Any]] = []
    def link(self, *, left_kind: str, left: str, relation: str, right_kind: str, right: str, effective_time: str, knowledge_time: str, expiry_time: str | None = None, via: str | None = None) -> dict[str, Any]:
        if relation not in RELATIONS:
            raise RelationDenied(f"invalid relation {relation}")
        if left == right and left_kind == right_kind:
            raise RelationDenied("cannot relate a subject to itself")
        row = {"left_kind": left_kind, "left": left, "relation": relation, "right_kind": right_kind, "right": right, "effective_time": effective_time, "expiry_time": expiry_time, "knowledge_time": knowledge_time, "via": via}
        self.links.append(row)
        return row
    def links_as_of(self, knowledge_time: str, event_time: str | None = None) -> list[dict[str, Any]]:
        out = []
        for row in self.links:
            if row["knowledge_time"] > knowledge_time:
                continue
            if event_time is not None:
                if row["effective_time"] > event_time:
                    continue
                if row["expiry_time"] is not None and row["expiry_time"] <= event_time:
                    continue
            out.append(row)
        return out
class AnalogueIndex:
    def __init__(self) -> None:
        self.links: list[dict[str, str]] = []
    def pair(self, event_a: str, event_b: str, basis: str, knowledge_time: str) -> dict[str, str]:
        if event_a == event_b:
            raise RelationDenied("analogue requires two events")
        row = {"event_a": event_a, "event_b": event_b, "basis": basis, "knowledge_time": knowledge_time, "score": ""}
        self.links.append(row)
        return row
