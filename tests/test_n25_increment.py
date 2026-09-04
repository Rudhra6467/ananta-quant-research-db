from pathlib import Path
from research_db.ingest.orchestrator import INGESTION_ENABLED

def test_increment_audit_does_not_claim_charter_complete() -> None:
    doc = (Path(__file__).resolve().parents[1] / "docs" / "N25_INCREMENT.md").read_text()
    assert "Kraken_OHLCVT_Q1_2026.zip" in doc
    assert "absent" in doc
    assert "2026-04-01T00:00Z" in doc
    assert "complete=0" in doc
    assert INGESTION_ENABLED is False
