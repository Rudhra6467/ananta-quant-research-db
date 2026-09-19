from pathlib import Path
import pytest
from research_db.lab.n3_gate import N3_EXECUTION_AUTHORIZED
from research_db.lab.n4_gate import N4Denied, N4_EXECUTION_AUTHORIZED, execute_n4
from research_db.lab.n5_gate import N5Denied, N5_EXECUTION_AUTHORIZED, execute_n5
from research_db.activation.archive_watch import classify_probe
from research_db.ingest.orchestrator import INGESTION_ENABLED

def test_n4_n5_briefs_exist_and_are_design_only() -> None:
    root = Path(__file__).resolve().parents[1] / "docs"
    assert "DESIGN ONLY" in (root / "N4_SHIFT_DESIGN.md").read_text()
    assert "DESIGN ONLY" in (root / "N5_AGENT_DESIGN.md").read_text()
    assert N3_EXECUTION_AUTHORIZED is False
    assert N4_EXECUTION_AUTHORIZED is False
    assert N5_EXECUTION_AUTHORIZED is False
    assert INGESTION_ENABLED is False

def test_n4_n5_execution_denied() -> None:
    with pytest.raises(N4Denied):
        execute_n4()
    with pytest.raises(N5Denied):
        execute_n5()

def test_watch_still_sees_q2_q3_absent() -> None:
    report = classify_probe({"Kraken_OHLCVT_Q1_2026.zip"})
    assert report["gap_closed"] is False
