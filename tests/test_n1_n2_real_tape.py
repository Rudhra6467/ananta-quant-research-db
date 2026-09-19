from datetime import datetime, timezone
import pytest
from research_db.activation.charter import INSTRUMENTS, SYMBOL_MAP, default_charter
from research_db.ingest.contract import IngestDenied, ProviderKind, RawRecord
from research_db.ingest.kraken_adapter import KrakenOHLCSource, ReplayOHLCSource
from research_db.ingest.orchestrator import INGESTION_ENABLED, IngestionOrchestrator
from research_db.ingest.report import quality_report
from research_db.persist import open_n2_store

def _bar(instrument, unix, close, knowledge, source_id=None):
    et = datetime.fromtimestamp(unix, tz=timezone.utc).replace(minute=0, second=0, microsecond=0).isoformat()
    payload = {"open": close-1, "high": close+1, "low": close-2, "close": close, "volume": 10}
    return RawRecord(source_code="kraken.ohlc.spot", source_record_id=source_id or f"XBTUSD:60:{unix}", instrument=instrument, timeframe="1h", event_time=et, knowledge_time=knowledge, payload=payload, checksum="x", provider_kind=ProviderKind.REPLAY)

def test_charter_names_ten_and_is_not_continuous() -> None:
    c = default_charter()
    assert c.instruments == INSTRUMENTS and len(INSTRUMENTS)==10
    assert c.continuous is False and c.n3_authorized is False and INGESTION_ENABLED is False
    assert set(SYMBOL_MAP)==set(INSTRUMENTS)

def test_live_still_denied_without_charter() -> None:
    class Live:
        code="kraken.ohlc.spot"; kind=ProviderKind.LIVE
        def records(self): return []
    with pytest.raises(IngestDenied, match="INGESTION_ENABLED"):
        IngestionOrchestrator().run(Live(), run_code="x", snapshot_code="y")

def test_charter_mismatch_denied() -> None:
    c = default_charter()
    src = KrakenOHLCSource(c, opener=lambda url: {"error":[],"result":{}})
    with pytest.raises(IngestDenied, match="not authorized"):
        IngestionOrchestrator().run(src, run_code="wrong", snapshot_code=c.snapshot_code, charter=c)

def test_mocked_charter_fetch_validates() -> None:
    c = default_charter()
    unix = 1630454400
    def opener(url):
        return {"error":[], "result": {"XXBTZUSD": [[unix,"1","3","0.5","2","1.5","9",4]], "last": unix}}
    src = KrakenOHLCSource(c, max_pages=1, max_bars=1, sleep_s=0, opener=opener)
    batch = IngestionOrchestrator().run(src, run_code=c.run_code, snapshot_code=c.snapshot_code, charter=c)
    assert batch.accepted[0].instrument=="BTC-USD-SPOT"
    assert quality_report(batch)["n3_authorized"] is False

def test_late_revision_does_not_rewrite_earlier_as_of() -> None:
    first = _bar("BTC-USD-SPOT", 1630454400, 100.0, "2021-09-01T00:05:00+00:00", "XBTUSD:60:1630454400:a")
    later = _bar("BTC-USD-SPOT", 1630454400, 101.0, "2021-09-01T02:00:00+00:00", "XBTUSD:60:1630454400:b")
    batch = IngestionOrchestrator().run(ReplayOHLCSource([first, later]), run_code="rev", snapshot_code="snap")
    visible = [r for r in batch.accepted if r.knowledge_time <= "2021-09-01T00:30:00+00:00"]
    assert len(visible)==1 and visible[0].payload["close"]==100.0

def test_idempotent_replay() -> None:
    rec = _bar("ETH-USD-SPOT", 1630454400, 50.0, "2021-09-01T00:05:00+00:00")
    orch = IngestionOrchestrator()
    a = orch.run(ReplayOHLCSource([rec]), run_code="r1", snapshot_code="s")
    b = orch.run(ReplayOHLCSource([rec]), run_code="r2", snapshot_code="s")
    assert len(a.accepted)==1 and b.duplicates==1

def test_persist_charter_keeps_n3_off() -> None:
    store = open_n2_store(); store.persist_charter(default_charter())
    row = store.conn.execute("SELECT continuous, n3_authorized FROM ops__activation_charter").fetchone()
    assert int(row["continuous"])==0 and int(row["n3_authorized"])==0
    assert store.conn.execute("SELECT COUNT(*) AS n FROM ops__source_symbol_map").fetchone()["n"]==10
