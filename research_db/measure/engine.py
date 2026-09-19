"""Phase 7 requested empirical measurements. Not a stats warehouse."""

from __future__ import annotations

from hashlib import sha256
from typing import Any

ALLOWED_FAMILIES = {"effect_size"}
ALLOWED_DEFINITIONS = {"effect_size.mean_forward_return.v1"}

DIRECTION_STATUS = {
    "untested": "INSUFFICIENT_EVIDENCE",
    "supports": "OBSERVED",
    "contradicts": "OBSERVED",
    "inconclusive": "INCONCLUSIVE",
    "invalidated": "OBSERVED",
    "decayed": "OBSERVED",
}


class MeasurementDenied(PermissionError):
    pass


def condition_digest(parts: dict[str, str]) -> str:
    payload = "|".join(f"{k}={parts[k]}" for k in sorted(parts))
    return sha256(payload.encode()).hexdigest()[:16]


class MeasurementEngine:
    def __init__(self) -> None:
        self.families = [{"code": "effect_size", "description": "Scalar effect over a declared sample"}]
        self.definitions = [
            {
                "code": "effect_size.mean_forward_return.v1",
                "family": "effect_size",
                "param_schema": {"horizon_bars": "int"},
            }
        ]
        self.requests: list[str] = []
        self.observations: list[dict[str, Any]] = []
        self.distributions: list[dict[str, Any]] = []

    def request(self, definition: str) -> str:
        if definition not in ALLOWED_DEFINITIONS:
            raise MeasurementDenied(f"unrequested measurement {definition}")
        if definition not in self.requests:
            self.requests.append(definition)
        return definition

    def from_evidence(
        self,
        *,
        definition: str,
        relationship: str,
        hypothesis: str | None,
        direction: str,
        effect: float | None,
        sample_size: int | None,
        uncertainty: float | None,
        event_time: str,
        knowledge_time: str,
        conditions: dict[str, str],
    ) -> dict[str, Any]:
        self.request(definition)
        status = DIRECTION_STATUS.get(direction)
        if status is None:
            raise MeasurementDenied(f"unknown evidence direction {direction}")
        if sample_size is not None and sample_size < 2:
            status = "INSUFFICIENT_EVIDENCE"
        row = {
            "definition": definition,
            "family": "effect_size",
            "relationship": relationship,
            "hypothesis": hypothesis,
            "point_value": effect,
            "sample_size": sample_size,
            "epistemic_status": status,
            "event_time": event_time,
            "knowledge_time": knowledge_time,
            "condition_digest": condition_digest(conditions),
            "conditions": conditions,
            "evidence_direction": direction,
        }
        self.observations.append(row)
        if uncertainty is not None:
            self.distributions.append(
                {
                    "definition": definition,
                    "relationship": relationship,
                    "knowledge_time": knowledge_time,
                    "representation": "parametric",
                    "payload": {"se": uncertainty, "kind": "symmetric_se"},
                }
            )
        return row
