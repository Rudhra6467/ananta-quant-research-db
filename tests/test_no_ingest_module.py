from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_no_market_ingest_package() -> None:
    forbidden = [
        ROOT / "ingestion" / "load_history.py",
        ROOT / "ingestion" / "binance.py",
        ROOT / "research_db" / "ingest.py",
    ]
    existing = [str(path) for path in forbidden if path.exists()]
    assert existing == []
