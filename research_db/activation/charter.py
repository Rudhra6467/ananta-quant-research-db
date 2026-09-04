"""N1 named real-tape charter. Versioned authorization, not a global ingest switch."""
from __future__ import annotations
from dataclasses import dataclass
CHARTER_CODE = "N1.CRYPTO_LAB_10"
CHARTER_VERSION = "v1"
SOURCE_CODE = "kraken.ohlc.spot"
VENUE = "KRAKEN"
MARKET = "spot"
TIMEFRAME = "1h"
WINDOW_START = "2021-09-01T00:00:00+00:00"
SNAPSHOT_CODE = "snap-cryptolab10-kraken-1h-v1"
RUN_CODE = "run-n2-kraken-ohlc-charter-v1"
ENDPOINT = "https://api.kraken.com/0/public/OHLC"
INSTRUMENTS = ("BTC-USD-SPOT","ETH-USD-SPOT","SOL-USD-SPOT","XRP-USD-SPOT","ADA-USD-SPOT","AVAX-USD-SPOT","LINK-USD-SPOT","DOGE-USD-SPOT","LTC-USD-SPOT","BCH-USD-SPOT")
SYMBOL_MAP = {"BTC-USD-SPOT":"XBTUSD","ETH-USD-SPOT":"ETHUSD","SOL-USD-SPOT":"SOLUSD","XRP-USD-SPOT":"XRPUSD","ADA-USD-SPOT":"ADAUSD","AVAX-USD-SPOT":"AVAXUSD","LINK-USD-SPOT":"LINKUSD","DOGE-USD-SPOT":"XDGUSD","LTC-USD-SPOT":"LTCUSD","BCH-USD-SPOT":"BCHUSD"}

@dataclass(frozen=True)
class ActivationCharter:
    code: str = CHARTER_CODE
    version: str = CHARTER_VERSION
    source_code: str = SOURCE_CODE
    venue: str = VENUE
    market: str = MARKET
    timeframe: str = TIMEFRAME
    window_start: str = WINDOW_START
    snapshot_code: str = SNAPSHOT_CODE
    run_code: str = RUN_CODE
    endpoint: str = ENDPOINT
    instruments: tuple[str, ...] = INSTRUMENTS
    continuous: bool = False
    capital: float = 0.0
    agent_runtime: bool = False
    n3_authorized: bool = False
    def authorizes(self, *, source_code: str, snapshot_code: str, run_code: str, instrument: str | None = None) -> bool:
        if source_code != self.source_code or snapshot_code != self.snapshot_code:
            return False
        if run_code != self.run_code and not run_code.startswith(self.run_code):
            return False
        if instrument is not None and instrument not in self.instruments:
            return False
        return True

def default_charter() -> ActivationCharter:
    return ActivationCharter()
