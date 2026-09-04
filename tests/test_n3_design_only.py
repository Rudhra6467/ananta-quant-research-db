from pathlib import Path
import pytest
from research_db.ingest.orchestrator import INGESTION_ENABLED
from research_db.lab.n3_gate import N3Denied, N3_EXECUTION_AUTHORIZED, execute_n3, assert_n3_may_run
from research_db.activation.archive_watch import default_watch
DOC = (Path(__file__).resolve().parents[1] / "docs" / "N3_LABORATORY_DESIGN.md").read_text()

def test_n3_brief_is_design_only() -> None:
    assert "DESIGN ONLY" in DOC and "Gate B" in DOC
    assert "EXP_N3_PIPELINE_SURVIVAL" in DOC
    assert INGESTION_ENABLED is False and N3_EXECUTION_AUTHORIZED is False

def test_n3_execution_denied_while_snapshot_incomplete() -> None:
    with pytest.raises(N3Denied, match="incomplete"):
        assert_n3_may_run(snapshot_complete=False)
    with pytest.raises(N3Denied):
        execute_n3()
    w = default_watch()
    assert w.n3_authorized is False and w.snapshot_complete is False
