"""Restartable charter backfill. Not continuous ingest."""
from __future__ import annotations
from research_db.activation.charter import ActivationCharter, default_charter
from research_db.ingest.kraken_adapter import KrakenOHLCSource
from research_db.ingest.orchestrator import IngestionOrchestrator
from research_db.ingest.snapshot import snapshot_quality
BACKFILL_RUN = "run-n2-kraken-ohlc-charter-v1.backfill"

def run_backfill(*, charter=None, max_pages=1, since_unix=None, orch=None, opener=None):
    charter = charter or default_charter()
    orch = orch or IngestionOrchestrator()
    src = KrakenOHLCSource(charter, since_unix=since_unix, max_pages=max_pages, sleep_s=1.05, opener=opener)
    batch = orch.run(src, run_code=BACKFILL_RUN if max_pages > 1 else BACKFILL_RUN + ".page", snapshot_code=charter.snapshot_code, charter=charter)
    report = snapshot_quality(batch)
    report["pages_fetched"] = src.pages_fetched
    report["watermarks"] = src.watermarks
    report["mapping_failures"] = src.mapping_failures
    return batch, report
