from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any
@dataclass
class ValidationResult:
    ok: bool
    reason: str = ""
def validate_ohlcv(payload: dict[str, Any], *, event_time: str, knowledge_time: str) -> ValidationResult:
    needed = ("open", "high", "low", "close", "volume")
    if any(k not in payload for k in needed):
        return ValidationResult(False, "missing_ohlcv")
    o, h, l, c, v = (float(payload[k]) for k in needed)
    if h < l:
        return ValidationResult(False, "high_lt_low")
    if h < max(o, c) or l > min(o, c):
        return ValidationResult(False, "range_inconsistent")
    if v < 0:
        return ValidationResult(False, "negative_volume")
    if knowledge_time < event_time:
        return ValidationResult(False, "knowledge_before_event")
    try:
        et = datetime.fromisoformat(event_time)
    except ValueError:
        return ValidationResult(False, "bad_event_time")
    if et.minute != 0 or et.second != 0:
        return ValidationResult(False, "not_hour_aligned")
    return ValidationResult(True)
