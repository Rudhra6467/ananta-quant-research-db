"""Phase 5 current-state / regime compiler.

Market truth and feature observations are inputs.
State and regime are derived system representations, not market facts
and not predictions. Only requested RSI(12-17) values are used.
"""

from __future__ import annotations

from statistics import median
from typing import Any

from research_db.observe.engine import REQUESTED_PERIODS, signature_for

REGIME_FAMILY = "rsi_region"
OVERSOLD = 35.0
PROVENANCE = "system_fixture"


class StateCompileDenied(PermissionError):
    pass


class StateCompiler:
    def __init__(self) -> None:
        self.market_states: list[dict[str, Any]] = []
        self.feature_currents: dict[str, dict[str, Any]] = {}
        self.regime_states: list[dict[str, Any]] = []
        self.compile_log: list[dict[str, Any]] = []

    def compile(
        self,
        bar: dict[str, Any],
        observations: list[dict[str, Any]],
        *,
        source: str = "observation_engine",
    ) -> dict[str, Any]:
        event_time = bar["event_time"]
        as_of_time = bar["as_of_time"]
        features: dict[str, float | None] = {signature_for(p): None for p in REQUESTED_PERIODS}
        used = 0
        for row in observations:
            if row.get("event_time") != event_time:
                continue
            key = row["parameter_set"]
            if key not in features:
                raise StateCompileDenied(f"unrequested feature in state compile: {key}")
            features[key] = None if row.get("value") is None else float(row["value"])
            used += 1
        self.feature_currents = {
            key: {
                "parameter_set": key,
                "event_time": event_time,
                "as_of_time": as_of_time,
                "value": value,
            }
            for key, value in features.items()
        }
        present = [v for v in features.values() if v is not None]
        if not present:
            label = "UNKNOWN"
            status = "INSUFFICIENT_EVIDENCE"
            value: float | None = None
        else:
            value = float(median(present))
            label = "oversold" if value < OVERSOLD else "neutral"
            status = "OBSERVED"
        market = {
            "instrument": bar["instrument"],
            "venue": bar.get("venue", "FIXTURE"),
            "timeframe": bar["timeframe"],
            "event_time": event_time,
            "as_of_time": as_of_time,
            "close": float(bar["close"]),
            "state_version": f"state:{event_time}",
        }
        regime = {
            "regime_family": REGIME_FAMILY,
            "label": label,
            "value": value,
            "epistemic_status": status,
            "event_time": event_time,
            "as_of_time": as_of_time,
            "provenance": PROVENANCE,
            "threshold": OVERSOLD,
            "n_features": len(present),
        }
        self.market_states.append(market)
        self.regime_states.append(regime)
        self.compile_log.append(
            {
                "kind": "state-compile",
                "event_time": event_time,
                "n_features_used": used,
                "source": source,
                "full_history_scan": False,
            }
        )
        return {"market": market, "regime": regime, "features": self.feature_currents}

    def current_market(self) -> dict[str, Any]:
        return self.market_states[-1]

    def current_regime(self) -> dict[str, Any]:
        return self.regime_states[-1]
