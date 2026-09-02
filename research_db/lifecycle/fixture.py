"""Deterministic BTC 1h fixture. Not exchange history."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

FIXTURE_CODE = "fixture-btc-1h-v1"
VENUE = "FIXTURE"
INSTRUMENT = "BTC-USD-SPOT"
TIMEFRAME = "1h"
SOURCE = "synthetic_fixture"
CANONICALIZATION_VERSION = "canon-v1"
BARS = 48
HORIZON_BARS = 4


def _close_series() -> list[float]:
    start = 100_000.0
    deltas = [
        -80, -120, -60, -200, -40, -150, -90, -30,
        -180, -70, -110, -50, -220, -40, -90, 20,
        -60, -30, 40, -20, 80, 30, -10, 90,
        40, 120, -30, 70, 50, -20, 110, 40,
        -15, 60, 25, -40, 80, 20, 50, -10,
        30, 45, -25, 70, 15, 40, -20, 55,
    ]
    assert len(deltas) == BARS
    out = []
    price = start
    for d in deltas:
        price += d
        out.append(round(price, 2))
    return out


def build_raw_payloads(include_extra: bool = False) -> list[dict[str, Any]]:
    closes = _close_series()
    if include_extra:
        closes = closes + [round(closes[-1] + 35.0, 2)]
    start = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    rows = []
    prev = closes[0]
    for i, close in enumerate(closes):
        event_time = start + timedelta(hours=i)
        high = max(prev, close) + 25
        low = min(prev, close) - 25
        rows.append(
            {
                "source": SOURCE,
                "source_record_id": f"{FIXTURE_CODE}:{i:03d}",
                "instrument": INSTRUMENT,
                "venue": VENUE,
                "timeframe": TIMEFRAME,
                "event_time": event_time.isoformat(),
                "payload": {
                    "open": prev,
                    "high": high,
                    "low": low,
                    "close": close,
                    "volume": 100.0 + i,
                },
                "checksum": f"chk-{i:03d}-{close}",
            }
        )
        prev = close
    return rows


def received_at_for(event_time: datetime) -> datetime:
    return event_time + timedelta(hours=1)
