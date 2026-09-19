from pathlib import Path
from datetime import datetime, timezone
from research_db.ingest.contract import ProviderKind
from research_db.ingest.ohlcvt_archive import ARCHIVE_ID, OhlcvtCsvSource
from research_db.ingest.orchestrator import INGESTION_ENABLED, IngestionOrchestrator
from research_db.ingest.snapshot import snapshot_quality
SAMPLE = Path(__file__).parent / "data" / "XBTUSD_60_sample.csv"

def test_archive_source_is_replay_not_live() -> None:
    src = OhlcvtCsvSource({"BTC-USD-SPOT": SAMPLE}, start="2021-09-01T00:00:00+00:00", end="2021-09-01T02:00:00+00:00")
    assert src.kind == ProviderKind.REPLAY and src.code == ARCHIVE_ID
    recs = list(src.records())
    assert len(recs)==2 and recs[0].source_record_id.startswith("ohlcvt:XBTUSD:60:")

def test_archive_idempotent_and_does_not_complete_full_charter() -> None:
    src = OhlcvtCsvSource({"BTC-USD-SPOT": SAMPLE}, start="2021-09-01T00:00:00+00:00", end="2021-09-01T02:00:00+00:00")
    orch = IngestionOrchestrator()
    a = orch.run(src, run_code="arch1", snapshot_code="snap-cryptolab10-kraken-1h-v1")
    b = orch.run(src, run_code="arch2", snapshot_code="snap-cryptolab10-kraken-1h-v1")
    assert len(a.accepted)==2 and b.duplicates==2
    assert snapshot_quality(a, end=datetime(2026,9,4,16,tzinfo=timezone.utc))["snapshot_complete"] is False
    assert INGESTION_ENABLED is False
