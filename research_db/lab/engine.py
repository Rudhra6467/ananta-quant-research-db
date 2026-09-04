from __future__ import annotations
from typing import Any
class LaboratoryDenied(PermissionError):
    pass
class ExperimentSpec:
    def __init__(self, code: str, snapshot: str, question: str) -> None:
        if not code or not snapshot:
            raise LaboratoryDenied("experiment needs code and snapshot")
        self.code = code
        self.snapshot = snapshot
        self.question = question
        self.results: list[dict[str, Any]] = []
    def record(self, status: str, note: str, measurement_code: str | None = None):
        if status not in {"supported", "contradicted", "inconclusive", "invalidated", "insufficient"}:
            raise LaboratoryDenied(f"bad status {status}")
        row = {"status": status, "note": note, "measurement": measurement_code, "tape": "fixture"}
        self.results.append(row)
        return row
