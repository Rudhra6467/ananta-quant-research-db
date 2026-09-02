from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "EMPIRICAL_MEMORY_ARCHITECTURE_V1.md"


def test_architecture_doc_exists_and_gates_ingestion() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert text.startswith("# Ananta Empirical Memory Architecture v1")
    required = [
        "Approval gate",
        "Canonical flow and authority",
        "Three layers",
        "Point-in-time and look-ahead",
        "Feature grain",
        "Relationships and evidence",
        "5-minute path",
        "Phase 0 entities actually created",
        "Not an ingestion approval",
        "Full historical ingestion is forbidden",
    ]
    missing = [item for item in required if item not in text]
    assert missing == []


def test_phases_doc_has_phase0_gate() -> None:
    text = (ROOT / "docs" / "PHASES.md").read_text(encoding="utf-8")
    assert "full-history ingestion" in text
    assert "Forbidden" in text
