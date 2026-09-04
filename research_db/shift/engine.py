KINDS = {"distribution_shift", "feature_drift", "regime_transition", "relationship_decay", "data_quality_shift", "market_structure_shift", "source_quality_degradation"}
class ShiftDenied(PermissionError):
    pass
class ShiftReview:
    def __init__(self) -> None:
        self.candidates = []
    def note(self, kind: str, event_code: str, basis: str):
        if kind not in KINDS:
            raise ShiftDenied(kind)
        row = {"kind": kind, "event": event_code, "basis": basis, "live_claim": False, "tape": "fixture"}
        self.candidates.append(row)
        return row
