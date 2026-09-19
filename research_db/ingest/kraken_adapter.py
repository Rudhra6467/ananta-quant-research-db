"""Kraken public OHLC adapter. Charter-scoped. No credentials."""
from __future__ import annotations
import hashlib, json, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from typing import Any, Iterable
from research_db.activation.charter import ActivationCharter, SYMBOL_MAP, default_charter
from research_db.ingest.contract import IngestDenied, ProviderKind, RawRecord
INTERVAL_MINUTES = 60

def _sha(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
def _iso(unix):
    return datetime.fromtimestamp(int(unix), tz=timezone.utc).replace(minute=0, second=0, microsecond=0).isoformat()

class KrakenOHLCSource:
    code = "kraken.ohlc.spot"
    kind = ProviderKind.LIVE
    def __init__(self, charter: ActivationCharter | None = None, *, since_unix=None, max_pages=1, max_bars=None, sleep_s=1.1, opener=None):
        self.charter = charter or default_charter()
        self.since_unix = since_unix
        self.max_pages = max_pages
        self.max_bars = max_bars
        self.sleep_s = sleep_s
        self._opener = opener
        self.pages_fetched = 0
        self.mapping_failures = []
        self.watermarks = {}
    def records(self) -> Iterable[RawRecord]:
        if self.kind == ProviderKind.LIVE and self.charter is None:
            raise IngestDenied("live Kraken adapter requires a charter")
        yielded = 0
        now = datetime.now(timezone.utc)
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        for instrument, pair in SYMBOL_MAP.items():
            if instrument not in self.charter.instruments:
                self.mapping_failures.append(instrument); continue
            since = self.since_unix
            for _page in range(self.max_pages):
                raw = self._get(pair, since)
                self.pages_fetched += 1
                errors = raw.get("error") or []
                if errors:
                    raise IngestDenied(f"kraken error {errors} for {pair}")
                result = raw.get("result") or {}
                series_key = next((k for k in result if k != "last"), None)
                if series_key is None:
                    self.mapping_failures.append(pair); break
                rows = result[series_key]
                last = result.get("last")
                produced = 0
                for row in rows:
                    unix = int(row[0])
                    event_time = _iso(unix)
                    et = datetime.fromisoformat(event_time)
                    if et >= current_hour:
                        continue
                    payload = {"open": float(row[1]), "high": float(row[2]), "low": float(row[3]), "close": float(row[4]), "volume": float(row[6]), "vwap": float(row[5]), "count": int(row[7]), "wire_symbol": pair, "result_key": series_key}
                    rec = RawRecord(source_code=self.code, source_record_id=f"{pair}:{INTERVAL_MINUTES}:{unix}", instrument=instrument, timeframe=self.charter.timeframe, event_time=event_time, knowledge_time=now.isoformat(), payload=payload, checksum=_sha(payload), provider_kind=self.kind)
                    yield rec
                    yielded += 1; produced += 1
                    if self.max_bars is not None and yielded >= self.max_bars:
                        return
                if last:
                    self.watermarks[instrument] = int(last); since = int(last)
                if produced == 0:
                    break
                time.sleep(self.sleep_s)
    def _get(self, pair, since):
        q = {"pair": pair, "interval": str(INTERVAL_MINUTES)}
        if since is not None:
            q["since"] = str(since)
        url = self.charter.endpoint + "?" + urllib.parse.urlencode(q)
        if self._opener is not None:
            return self._opener(url)
        req = urllib.request.Request(url, headers={"User-Agent": "ananta-n2-charter/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())

class ReplayOHLCSource:
    def __init__(self, rows: list[RawRecord], code: str = "kraken.ohlc.spot.replay"):
        self.code = code
        self.kind = ProviderKind.REPLAY
        self._rows = rows
    def records(self):
        return list(self._rows)
