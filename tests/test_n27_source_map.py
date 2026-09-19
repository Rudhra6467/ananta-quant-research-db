from pathlib import Path
from research_db.ingest.source_map import map_pair, may_label_as_ohlcvt_zip, classify_source, TRADE_AGG
from research_db.lab.n3_gate import N3_EXECUTION_AUTHORIZED
def test_trade_agg_is_not_the_zip() -> None:
    assert may_label_as_ohlcvt_zip(TRADE_AGG) is False
    assert classify_source(TRADE_AGG) == "official_aggregate"
    assert map_pair("XBTUSD") == "BTC-USD-SPOT"
def test_amendment_and_plan_exist() -> None:
    root = Path(__file__).resolve().parents[1] / "docs"
    assert "kraken.trades.agg.1h" in (root / "CONSTITUTION_AMENDMENT_A1.md").read_text()
    assert "kraken.trades.agg.1h" in (root / "N27_MULTI_SOURCE_PLAN.md").read_text()
    assert N3_EXECUTION_AUTHORIZED is False
