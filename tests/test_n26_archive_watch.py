from research_db.activation.archive_watch import ArchiveWatch, classify_probe, default_watch
from research_db.ingest.orchestrator import INGESTION_ENABLED

def test_watch_records_exact_gap_and_forbids_auto_ingest() -> None:
    w = default_watch()
    assert w.missing_start.startswith("2026-04-01")
    assert w.missing_end.startswith("2026-08-05T16")
    assert w.auto_ingest is False and w.load_authorized is False
    assert w.snapshot_complete is False and w.n3_authorized is False
    assert w.load_allowed("Kraken_OHLCVT_Q2_2026.zip") is False
    assert INGESTION_ENABLED is False

def test_probe_does_not_close_gap_without_both_official_files() -> None:
    report = classify_probe({"Kraken_OHLCVT_Q1_2026.zip"})
    assert report["gap_closed"] is False
    assert report["absent"] == ["Kraken_OHLCVT_Q2_2026.zip", "Kraken_OHLCVT_Q3_2026.zip"]
    assert report["n3_authorized"] is False

def test_even_if_both_zips_listed_load_still_requires_authorization() -> None:
    report = classify_probe(set(ArchiveWatch().expected_files))
    assert report["gap_closed"] is True
    assert report["load_authorized"] is False and report["auto_ingest"] is False
