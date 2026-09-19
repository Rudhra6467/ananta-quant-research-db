"""Phase 6 hypothesis lifecycle. Not predictions. Not ranking. Not ingest."""

from __future__ import annotations

from typing import Any

HYPOTHESIS_STATES = (
    "proposed",
    "under_test",
    "supported",
    "contradicted",
    "inconclusive",
    "invalidated",
    "decayed",
)

EVIDENCE_TO_STATUS = {
    "untested": "under_test",
    "supports": "supported",
    "contradicts": "contradicted",
    "inconclusive": "inconclusive",
    "invalidated": "invalidated",
    "decayed": "decayed",
}


class HypothesisDenied(PermissionError):
    pass


class HypothesisEngine:
    def __init__(self) -> None:
        self.hypotheses: list[dict[str, Any]] = []
        self.status_events: list[dict[str, Any]] = []
        self.support_links: list[dict[str, Any]] = []
        self.analogue_definitions: list[dict[str, Any]] = []

    def register(self, code: str, relationship: str, event_time: str, knowledge_time: str) -> dict[str, Any]:
        row = {
            "code": code,
            "relationship": relationship,
            "claim_kind": "system_hypothesis",
            "version": "v1",
        }
        self.hypotheses.append(row)
        self._event(code, "proposed", event_time, knowledge_time, evidence_direction=None, note="registered")
        return row

    def apply_evidence(
        self,
        code: str,
        direction: str,
        event_time: str,
        knowledge_time: str,
        *,
        evidence_key: str | None = None,
    ) -> dict[str, Any]:
        if direction not in EVIDENCE_TO_STATUS:
            raise HypothesisDenied(f"unknown evidence direction {direction}")
        status = EVIDENCE_TO_STATUS[direction]
        ev = self._event(code, status, event_time, knowledge_time, evidence_direction=direction, note="evidence")
        if evidence_key:
            self.support_links.append(
                {
                    "hypothesis": code,
                    "source_kind": "evidence",
                    "source_id": evidence_key,
                    "event_time": event_time,
                    "knowledge_time": knowledge_time,
                }
            )
        return ev

    def link_state(self, code: str, source_kind: str, source_id: str, event_time: str, knowledge_time: str) -> None:
        if source_kind not in {"market_state", "regime_state", "feature_observation"}:
            raise HypothesisDenied(f"unsupported provenance kind {source_kind}")
        self.support_links.append(
            {
                "hypothesis": code,
                "source_kind": source_kind,
                "source_id": source_id,
                "event_time": event_time,
                "knowledge_time": knowledge_time,
            }
        )

    def define_analogue(self, code: str = "state_l2_v1") -> dict[str, Any]:
        row = {
            "code": code,
            "version": "v1",
            "metric_name": "l2_state_distance",
            "description": "Reserved analogue identity. No scores computed in Phase 6.",
        }
        self.analogue_definitions.append(row)
        return row

    def current_status(self, code: str) -> str:
        events = [e for e in self.status_events if e["hypothesis"] == code]
        if not events:
            raise HypothesisDenied(f"unknown hypothesis {code}")
        return events[-1]["status"]

    def _event(
        self,
        code: str,
        status: str,
        event_time: str,
        knowledge_time: str,
        *,
        evidence_direction: str | None,
        note: str,
    ) -> dict[str, Any]:
        if status not in HYPOTHESIS_STATES:
            raise HypothesisDenied(f"illegal status {status}")
        row = {
            "hypothesis": code,
            "status": status,
            "event_time": event_time,
            "knowledge_time": knowledge_time,
            "evidence_direction": evidence_direction,
            "note": note,
        }
        self.status_events.append(row)
        return row
