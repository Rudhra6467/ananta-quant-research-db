from datetime import datetime, timezone
from research_db.activation.charter import SNAPSHOT_CODE, WINDOW_START, default_charter
from research_db.ingest.backfill import BACKFILL_RUN
from research_db.ingest.contract import ProviderKind, RawRecord
from research_db.ingest.kraken_adapter import ReplayOHLCSource
from research_db.ingest.orchestrator import INGESTION_ENABLED, IngestionOrchestrator
from research_db.ingest.snapshot import expected_hours, snapshot_quality
from research_db.persist import open_n2_store

def _rec(sid, close, event, knowledge):
    return RawRecord(source_code="kraken.ohlc.spot", source_record_id=sid, instrument="BTC-USD-SPOT", timeframe="1h", event_time=event, knowledge_time=knowledge, payload={"open": close-1, "high": close+1, "low": close-2, "close": close, "volume": 1}, checksum="c", provider_kind=ProviderKind.REPLAY)

def test_charter_window_expected_count_is_multi_year() -> None:
    assert expected_hours(WINDOW_START, datetime(2026,9,4,16,tzinfo=timezone.utc)) > 40000

def test_page_sized_batch_is_not_charter_complete() -> None:
    recs = [_rec(f"XBTUSD:60:{1630454400+i*3600}", 100+i, datetime.fromtimestamp(1630454400+i*3600, tz=timezone.utc).isoformat(), "2021-09-02T00:00:00+00:00") for i in range(3)]
    batch = IngestionOrchestrator().run(ReplayOHLCSource(recs), run_code=BACKFILL_RUN, snapshot_code=SNAPSHOT_CODE)
    report = snapshot_quality(batch, end=datetime(2026,9,4,16,tzinfo=timezone.utc))
    assert report["snapshot_complete"] is False and report["n3_authorized"] is False
    assert "720" in report["source_limitation"]

def test_revision_hidden_before_knowledge_time() -> None:
    first = _rec("XBTUSD:60:1630454400:a", 100.0, "2021-09-01T00:00:00+00:00", "2021-09-01T00:05:00+00:00")
    later = _rec("XBTUSD:60:1630454400:b", 101.0, "2021-09-01T00:00:00+00:00", "2021-09-01T03:00:00+00:00")
    batch = IngestionOrchestrator().run(ReplayOHLCSource([first, later]), run_code=BACKFILL_RUN+".rev", snapshot_code=SNAPSHOT_CODE)
    store = open_n2_store(); store.persist_charter(default_charter())
    store.persist_snapshot_bars(batch, {"snapshot_complete": False, "source_limitation": "test"})
    early = store.snapshot_bars_as_of(SNAPSHOT_CODE, "2021-09-01T01:00:00+00:00", "BTC-USD-SPOT")
    late = store.snapshot_bars_as_of(SNAPSHOT_CODE, "2021-09-01T04:00:00+00:00", "BTC-USD-SPOT")
    assert len(early)==1 and early[0]["close"]==100.0
    assert any(r["close"]==101.0 for r in late)

def test_idempotent_persist_same_source_record() -> None:
    rec = _rec("XBTUSD:60:1630461600", 99.0, "2021-09-01T02:00:00+00:00", "2021-09-01T02:05:00+00:00")
    orch = IngestionOrchestrator()
    a = orch.run(ReplayOHLCSource([rec]), run_code="a", snapshot_code=SNAPSHOT_CODE)
    b = orch.run(ReplayOHLCSource([rec]), run_code="b", snapshot_code=SNAPSHOT_CODE)
    store = open_n2_store(); n = store.persist_snapshot_bars(a, {}); store.persist_snapshot_bars(b, {})
    assert b.duplicates==1 and n==1

def test_ingest_flag_stays_off() -> None:
    assert INGESTION_ENABLED is False
