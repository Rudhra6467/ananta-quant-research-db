"""Official Kraken public Trades → 1h bars. Never labeled as OHLCVT ZIP."""
from __future__ import annotations
import hashlib, json, time, urllib.parse, urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Iterable
from research_db.activation.charter import ActivationCharter, INSTRUMENTS
from research_db.ingest.contract import IngestDenied, ProviderKind, RawRecord
from research_db.ingest.source_map import TRADE_AGG, map_pair
ENDPOINT = "https://api.kraken.com/0/public/Trades"
Q2_START_UNIX = int(datetime(2026, 4, 1, tzinfo=timezone.utc).timestamp())
Q2_END_UNIX = int(datetime(2026, 7, 1, tzinfo=timezone.utc).timestamp())
def _sha(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
def hour_floor(unix: float) -> int:
    return int(unix) - (int(unix) % 3600)
def aggregate_trades(trades: list[tuple[float, float, float]], *, wire: str) -> list[dict[str, Any]]:
    buckets: dict[int, list[tuple[float, float, float]]] = defaultdict(list)
    for price, vol, ts in trades:
        buckets[hour_floor(ts)].append((price, vol, ts))
    bars = []
    for hour in sorted(buckets):
        rows = buckets[hour]
        prices = [r[0] for r in rows]
        vols = [r[1] for r in rows]
        bars.append({"open": prices[0], "high": max(prices), "low": min(prices), "close": prices[-1], "volume": float(sum(vols)), "trades": len(rows), "event_unix": hour, "wire_symbol": wire, "source_code": TRADE_AGG})
    return bars
def bar_to_record(bar: dict[str, Any], *, knowledge_time: str, instrument: str) -> RawRecord:
    event = datetime.fromtimestamp(bar["event_unix"], tz=timezone.utc).isoformat()
    payload = {"open": bar["open"], "high": bar["high"], "low": bar["low"], "close": bar["close"], "volume": bar["volume"], "trades": bar["trades"], "wire_symbol": bar["wire_symbol"], "aggregate_of": "kraken.public.trades", "not_ohlcvt_zip": True}
    return RawRecord(source_code=TRADE_AGG, source_record_id=f"tradesagg:{bar['wire_symbol']}:60:{bar['event_unix']}", instrument=instrument, timeframe="1h", event_time=event, knowledge_time=knowledge_time, payload=payload, checksum=_sha(payload), provider_kind=ProviderKind.REPLAY)
class Q2TradeAggCharter(ActivationCharter):
    def __init__(self, *, authorized: bool = False, instruments: tuple[str, ...] | None = None):
        super().__init__(source_code=TRADE_AGG, run_code="run-n27-kraken-trades-agg-q2-v1", endpoint=ENDPOINT, instruments=instruments or INSTRUMENTS, n3_authorized=False)
        object.__setattr__(self, "_agg_authorized", authorized)
    def authorizes(self, *, source_code: str, snapshot_code: str, run_code: str, instrument: str | None = None) -> bool:
        if not getattr(self, "_agg_authorized", False) or source_code != TRADE_AGG:
            return False
        if snapshot_code != self.snapshot_code or not run_code.startswith("run-n27-kraken-trades-agg"):
            return False
        if instrument is not None and instrument not in self.instruments:
            return False
        return True
class KrakenTradesAggSource:
    code = TRADE_AGG
    kind = ProviderKind.REPLAY
    def __init__(self, *, pairs: list[str], since_unix: int = Q2_START_UNIX, until_unix: int = Q2_END_UNIX, max_pages: int = 3, max_hours: int | None = 3, sleep_s: float = 0.8, opener=None):
        self.pairs = pairs
        self.since_unix = since_unix
        self.until_unix = until_unix
        self.max_pages = max_pages
        self.max_hours = max_hours
        self.sleep_s = sleep_s
        self._opener = opener
        self.pages_fetched = 0
        self.trade_count = 0
    def _get(self, pair: str, since: int | str) -> dict[str, Any]:
        q = urllib.parse.urlencode({"pair": pair, "since": since})
        req = urllib.request.Request(f"{ENDPOINT}?{q}", headers={"User-Agent": "ananta-n27-trades"})
        opener = self._opener or urllib.request.urlopen
        with opener(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        if data.get("error"):
            raise IngestDenied(f"kraken trades error {data['error']}")
        return data["result"]
    def records(self) -> Iterable[RawRecord]:
        now = datetime.now(timezone.utc).isoformat()
        for pair in self.pairs:
            instrument = map_pair(pair)
            ticks: list[tuple[float, float, float]] = []
            since: int | str = self.since_unix
            for _ in range(self.max_pages):
                result = self._get(pair, since)
                self.pages_fetched += 1
                rows = []
                last = result.get("last")
                for key, val in result.items():
                    if key == "last":
                        continue
                    rows = val
                for row in rows:
                    ts = float(row[2])
                    if self.since_unix <= ts < self.until_unix:
                        ticks.append((float(row[0]), float(row[1]), ts))
                self.trade_count += len(rows)
                if not rows or last is None:
                    break
                since = last
                if ticks and hour_floor(ticks[-1][2]) >= self.since_unix + (self.max_hours or 10**9) * 3600:
                    break
                time.sleep(self.sleep_s)
            ticks.sort(key=lambda t: t[2])
            bars = aggregate_trades(ticks, wire=pair)
            if self.max_hours is not None:
                bars = bars[: self.max_hours]
            for bar in bars:
                yield bar_to_record(bar, knowledge_time=now, instrument=instrument)
