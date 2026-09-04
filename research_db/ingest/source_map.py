"""Explicit source mapping. Does not fetch or ingest."""
from __future__ import annotations
PREFERRED_ARCHIVE = "kraken.ohlcvt"
TRADE_AGG = "kraken.trades.agg.1h"
OHLC_REST = "kraken.ohlc.spot"
PAIR_MAP = {"XBTUSD":"BTC-USD-SPOT","XXBTZUSD":"BTC-USD-SPOT","ETHUSD":"ETH-USD-SPOT","SOLUSD":"SOL-USD-SPOT","XRPUSD":"XRP-USD-SPOT","ADAUSD":"ADA-USD-SPOT","AVAXUSD":"AVAX-USD-SPOT","LINKUSD":"LINK-USD-SPOT","XDGUSD":"DOGE-USD-SPOT","LTCUSD":"LTC-USD-SPOT","BCHUSD":"BCH-USD-SPOT"}
def map_pair(wire: str) -> str:
    if wire not in PAIR_MAP:
        raise KeyError(f"unmapped wire {wire}")
    return PAIR_MAP[wire]
def classify_source(source_code: str) -> str:
    if source_code.startswith("kraken.ohlcvt"):
        return "preferred_archive"
    if source_code == TRADE_AGG:
        return "official_aggregate"
    if source_code == OHLC_REST:
        return "official_rest_window"
    return "parallel_or_unknown"
def may_label_as_ohlcvt_zip(source_code: str) -> bool:
    return source_code.startswith("kraken.ohlcvt")
