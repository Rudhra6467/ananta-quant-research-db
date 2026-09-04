from research_db.ingest.source_map import TRADE_AGG, may_label_as_ohlcvt_zip
from research_db.ingest.trade_agg import aggregate_trades, bar_to_record, Q2TradeAggCharter, hour_floor
from research_db.ingest.orchestrator import IngestionOrchestrator, INGESTION_ENABLED
from research_db.lab.n3_gate import N3_EXECUTION_AUTHORIZED

def test_aggregate_builds_hour_bar_and_skips_empty() -> None:
    t0 = 1775001600
    trades = [(100.0, 1.0, t0 + 10), (101.0, 2.0, t0 + 20), (99.5, 0.5, t0 + 50), (102.0, 1.0, t0 + 3610)]
    bars = aggregate_trades(trades, wire="LTCUSD")
    assert len(bars) == 2
    assert bars[0]["open"] == 100.0 and bars[0]["high"] == 101.0 and bars[0]["low"] == 99.5
    rec = bar_to_record(bars[0], knowledge_time="2026-09-04T00:00:00+00:00", instrument="LTC-USD-SPOT")
    assert rec.source_code == TRADE_AGG and rec.payload["not_ohlcvt_zip"] is True
    assert may_label_as_ohlcvt_zip(rec.source_code) is False
    assert hour_floor(t0 + 10) == t0

def test_q2_charter_denied_until_authorized_and_n3_stays_off() -> None:
    denied = Q2TradeAggCharter(authorized=False)
    assert denied.authorizes(source_code=TRADE_AGG, snapshot_code=denied.snapshot_code, run_code="run-n27-kraken-trades-agg-q2-v1") is False
    ok = Q2TradeAggCharter(authorized=True, instruments=("LTC-USD-SPOT",))
    assert ok.authorizes(source_code=TRADE_AGG, snapshot_code=ok.snapshot_code, run_code="run-n27-kraken-trades-agg-q2-v1") is True
    assert INGESTION_ENABLED is False and N3_EXECUTION_AUTHORIZED is False

def test_orchestrator_accepts_replay_agg_without_global_ingest_flag() -> None:
    t0 = 1775001600
    rec = bar_to_record(aggregate_trades([(80.0, 1.0, t0 + 1)], wire="LTCUSD")[0], knowledge_time="2026-09-04T20:00:00+00:00", instrument="LTC-USD-SPOT")
    class _Prov:
        code = TRADE_AGG
        kind = "replay"
        def records(self):
            yield rec
    batch = IngestionOrchestrator().run(_Prov(), run_code="run-n27-kraken-trades-agg-q2-v1", snapshot_code="snap-cryptolab10-kraken-1h-v1")
    assert len(batch.accepted) == 1 and batch.accepted[0].source_code == TRADE_AGG
