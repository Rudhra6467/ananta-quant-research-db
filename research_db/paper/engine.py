"""Phase 18 paper profiles and decision ledger. No real capital. No exchange."""
from __future__ import annotations
PROFILES = {"SAFE", "AVERAGE", "AGGRESSIVE"}
ACTIONS = {"TAKE", "SKIP", "WAIT", "HOLD"}
class PaperDenied(PermissionError):
    pass
class PaperLedger:
    def __init__(self) -> None:
        self.profiles = [
            {"code": "SAFE", "max_risk": "low", "live_capital": False},
            {"code": "AVERAGE", "max_risk": "medium", "live_capital": False},
            {"code": "AGGRESSIVE", "max_risk": "high", "live_capital": False},
        ]
        self.decisions = []
    def decide(self, profile: str, action: str, knowledge_time: str, reason: str, query: str | None = None, information_set: dict | None = None):
        if profile not in PROFILES:
            raise PaperDenied(f"unknown profile {profile}")
        if action not in ACTIONS:
            raise PaperDenied(f"unknown action {action}")
        if profile == "SAFE" and action == "TAKE":
            raise PaperDenied("SAFE profile cannot TAKE on this fixture ledger")
        row = {"profile": profile, "action": action, "knowledge_time": knowledge_time, "reason": reason, "query": query, "capital": 0, "information_set": information_set or {}, "live_order": False}
        self.decisions.append(row)
        return row
