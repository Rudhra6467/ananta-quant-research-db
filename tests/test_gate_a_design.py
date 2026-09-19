from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "GATE_A_INGESTION_DESIGN.md").read_text(encoding="utf-8")

def test_gate_a_is_design_only() -> None:
    assert "DESIGN ONLY" in DOC
    assert "INGESTION_ENABLED" in DOC
    assert "false" in DOC.lower()
    assert "No vendor session" in DOC or "no HTTP to an exchange" in DOC

def test_gate_a_has_required_sections() -> None:
    for token in ("CRYPTO_LAB_10", "source_record_id", "checksum", "knowledge_time", "Backfill", "Incremental", "quarantine", "ops.current_*", "Conflict report"):
        assert token in DOC

def test_gate_a_does_not_authorize_gate_b() -> None:
    assert "not authorized" in DOC.lower() or "Not accepted for implementation" in DOC
    assert "CUSUM" in DOC
    assert list((ROOT / "sql").glob("021*")) == []

def test_ten_planned_members_named() -> None:
    for asset in ("BTC", "ETH", "SOL", "XRP", "ADA", "AVAX", "LINK", "DOGE", "LTC", "BCH"):
        assert f"{asset}-USD-SPOT" in DOC
