from pathlib import Path
from research_db.activation.direction import IMPLEMENT_SCALING_OPTIMIZER, N3_IS_LABORATORY_NOT_ACQUISITION, N5A_MAY_FOLLOW_N3, N5B_REQUIRES_N4, SCALING_TIERS
from research_db.lab.n3_gate import N3_EXECUTION_AUTHORIZED
from research_db.ingest.orchestrator import INGESTION_ENABLED
DOC = (Path(__file__).resolve().parents[1] / "docs" / "DIRECTION_LOCK.md").read_text()

def test_direction_lock_text() -> None:
    assert "N3 is **not** acquisition" in DOC
    assert "N5a" in DOC and "N5b" in DOC
    assert N3_IS_LABORATORY_NOT_ACQUISITION and N5A_MAY_FOLLOW_N3 and N5B_REQUIRES_N4
    assert IMPLEMENT_SCALING_OPTIMIZER is False
    assert SCALING_TIERS[0] == "permanent_truth"
    assert N3_EXECUTION_AUTHORIZED is False and INGESTION_ENABLED is False
