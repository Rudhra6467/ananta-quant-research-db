"""Phase 9 requested analytical features. Reuses observation grain. No cube."""

from __future__ import annotations

from typing import Any

ALLOWED = {"RET(1)", "RANGE_VOL(1)"}


class AnalyticalDenied(PermissionError):
    pass


class AnalyticalEngine:
    def __init__(self) -> None:
        self.requests: list[str] = []
        self.observations: list[dict[str, Any]] = []
        self._last_close: float | None = None
        self._last_event: str | None = None

    def request(self, signature: str) -> str:
        if signature not in ALLOWED:
            raise AnalyticalDenied(f"unrequested analytical feature {signature}")
        if signature not in self.requests:
            self.requests.append(signature)
        return signature

    def compute(self, bars: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self.requests:
            return []
        created: list[dict[str, Any]] = []
        start = 0
        if self._last_event is not None:
            times = [b["event_time"] for b in bars]
            if self._last_event in times:
                start = times.index(self._last_event) + 1
        for bar in bars[start:]:
            close = float(bar["close"])
            high = float(bar.get("high", close))
            low = float(bar.get("low", close))
            if "RET(1)" in self.requests and self._last_close is not None and self._last_close != 0:
                created.append(self._row("RET(1)", bar, (close / self._last_close) - 1.0))
            if "RANGE_VOL(1)" in self.requests and close != 0:
                created.append(self._row("RANGE_VOL(1)", bar, (high - low) / close))
            self._last_close = close
            self._last_event = bar["event_time"]
        self.observations.extend(created)
        return created

    def _row(self, signature: str, bar: dict[str, Any], value: float) -> dict[str, Any]:
        return {
            "feature": signature.split("(")[0],
            "feature_version": "v1",
            "parameter_set": signature,
            "instrument": bar["instrument"],
            "timeframe": bar["timeframe"],
            "event_time": bar["event_time"],
            "as_of_time": bar["as_of_time"],
            "value": value,
            "status": "OBSERVED",
        }
