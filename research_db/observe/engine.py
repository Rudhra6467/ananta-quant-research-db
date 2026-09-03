"""Request-driven feature observation engine.

Computes only requested parameter sets. Incremental ticks update rolling
state instead of rescanning the full bar history or the unused RSI domain.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from research_db.lifecycle.features import _rsi

REQUESTED_PERIODS = tuple(range(12, 18))
ALLOWED = {f"RSI({period})" for period in REQUESTED_PERIODS}


class ObservationDenied(PermissionError):
    pass


@dataclass
class RollState:
    period: int
    seed_closes: list[float] = field(default_factory=list)
    avg_gain: float | None = None
    avg_loss: float | None = None
    last_close: float | None = None
    last_event_time: str | None = None
    primed: bool = False
    steps: int = 0


def signature_for(period: int) -> str:
    return f"RSI({period})"


class ObservationEngine:
    def __init__(self, periods: tuple[int, ...] = REQUESTED_PERIODS) -> None:
        if any(period not in REQUESTED_PERIODS for period in periods):
            raise ObservationDenied("phase4 fixture engine only accepts RSI(12-17)")
        self.periods = periods
        self.states = {signature_for(period): RollState(period=period) for period in periods}
        self.observations: list[dict[str, Any]] = []
        self.compute_log: list[dict[str, Any]] = []

    def request(self, signature: str) -> str:
        if signature not in ALLOWED:
            raise ObservationDenied(f"unrequested feature {signature}")
        return signature

    def compute(self, bars: list[dict[str, Any]]) -> list[dict[str, Any]]:
        created: list[dict[str, Any]] = []
        for signature, state in self.states.items():
            start = 0
            if state.last_event_time is not None:
                times = [bar["event_time"] for bar in bars]
                if state.last_event_time in times:
                    start = times.index(state.last_event_time) + 1
            window = bars[start:]
            self.compute_log.append(
                {
                    "kind": "rsi-roll",
                    "parameter_set": signature,
                    "n_bars": len(window),
                    "full_history": len(bars),
                }
            )
            for bar in window:
                value = self._step(state, float(bar["close"]), bar["event_time"])
                if value is None:
                    continue
                row = {
                    "feature": "RSI",
                    "feature_version": "v1",
                    "parameter_set": signature,
                    "instrument": bar["instrument"],
                    "timeframe": bar["timeframe"],
                    "event_time": bar["event_time"],
                    "as_of_time": bar["as_of_time"],
                    "value": value,
                    "dataset_snapshot": bar.get("dataset_snapshot"),
                }
                self.observations.append(row)
                created.append(row)
        return created

    def _step(self, state: RollState, close: float, event_time: str) -> float | None:
        state.steps += 1
        if state.last_close is None:
            state.last_close = close
            state.last_event_time = event_time
            state.seed_closes = [close]
            return None
        change = close - state.last_close
        gain = max(change, 0.0)
        loss = max(-change, 0.0)
        if not state.primed:
            state.seed_closes.append(close)
            if len(state.seed_closes) <= state.period:
                state.last_close = close
                state.last_event_time = event_time
                return None
            gains = 0.0
            losses = 0.0
            for i in range(1, state.period + 1):
                delta = state.seed_closes[i] - state.seed_closes[i - 1]
                if delta >= 0:
                    gains += delta
                else:
                    losses -= delta
            state.avg_gain = gains / state.period
            state.avg_loss = losses / state.period
            state.primed = True
            state.last_close = close
            state.last_event_time = event_time
            return _rsi(state.avg_gain, state.avg_loss)
        assert state.avg_gain is not None and state.avg_loss is not None
        state.avg_gain = (state.avg_gain * (state.period - 1) + gain) / state.period
        state.avg_loss = (state.avg_loss * (state.period - 1) + loss) / state.period
        state.last_close = close
        state.last_event_time = event_time
        return _rsi(state.avg_gain, state.avg_loss)
