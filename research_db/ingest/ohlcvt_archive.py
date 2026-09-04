"""Kraken official OHLCVT ZIP/CSV archive. Public, no credentials. Not trades reconstruction."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from research_db.activation.charter import SYMBOL_MAP, default_charter
from research_db.ingest.contract import ProviderKind, RawRecord
ARCHIVE_ID = "kraken.ohlcvt.master_q4"
ARCHIVE_FILE = "Kraken_OHLCVT.zip"
ARCHIVE_DRIVE_ID = "1ptNqWYidLkhb2VAKuLCxmp2OXEfGO-AP"
ARCHIVE_KNOWLEDGE_TIME = "2026-01-01T00:05:00+00:00"
MEMBER_BY_INSTRUMENT = {"BTC-USD-SPOT":"master_q4/XBTUSD_60.csv","ETH-USD-SPOT":"master_q4/ETHUSD_60.csv","SOL-USD-SPOT":"master_q4/SOLUSD_60.csv","XRP-USD-SPOT":"master_q4/XRPUSD_60.csv","ADA-USD-SPOT":"master_q4/ADAUSD_60.csv","AVAX-USD-SPOT":"master_q4/AVAXUSD_60.csv","LINK-USD-SPOT":"master_q4/LINKUSD_60.csv","DOGE-USD-SPOT":"master_q4/XDGUSD_60.csv","LTC-USD-SPOT":"master_q4/LTCUSD_60.csv","BCH-USD-SPOT":"master_q4/BCHUSD_60.csv"}

def _sha(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()

class OhlcvtCsvSource:
    code = ARCHIVE_ID
    kind = ProviderKind.REPLAY
    def __init__(self, files: dict[str, Path], *, start: str, end: str) -> None:
        self.files = files; self.start = start; self.end = end; self.charter = default_charter()
    def records(self) -> Iterable[RawRecord]:
        start = datetime.fromisoformat(self.start.replace("Z", "+00:00"))
        end = datetime.fromisoformat(self.end.replace("Z", "+00:00"))
        for instrument, path in self.files.items():
            wire = SYMBOL_MAP[instrument]
            for line in Path(path).read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                parts = line.split(",")
                unix = int(float(parts[0]))
                event = datetime.fromtimestamp(unix, tz=timezone.utc).replace(minute=0, second=0, microsecond=0)
                if event < start or event > end:
                    continue
                payload = {"open": float(parts[1]), "high": float(parts[2]), "low": float(parts[3]), "close": float(parts[4]), "volume": float(parts[5]), "trades": int(float(parts[6])) if len(parts)>6 else 0, "wire_symbol": wire, "archive_member": MEMBER_BY_INSTRUMENT.get(instrument,""), "archive_file": ARCHIVE_FILE, "archive_id": ARCHIVE_DRIVE_ID}
                yield RawRecord(source_code=self.code, source_record_id=f"ohlcvt:{wire}:60:{unix}", instrument=instrument, timeframe="1h", event_time=event.isoformat(), knowledge_time=ARCHIVE_KNOWLEDGE_TIME, payload=payload, checksum=_sha(payload), provider_kind=self.kind)
