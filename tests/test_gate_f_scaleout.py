from pathlib import Path
import pytest
from research_db.ingest.orchestrator import INGESTION_ENABLED
from research_db.persist import LiveQueryDenied, open_scaleout_store
from research_db.scaleout.engine import CROSS_ASSET, LAB10, ONTOLOGY, ScaleoutRegistry, WORLDS, fixture_scale_demo
ROOT = Path(__file__).resolve().parents[1]

def test_lab10_planned_not_ingested() -> None:
    reg = ScaleoutRegistry()
    assert len(LAB10) == 10 and ONTOLOGY[-1] == "instrument"
    assert reg.ingested() is False

def test_quality_quarantines_bad_and_duplicate() -> None:
    reg = ScaleoutRegistry(); seen=set()
    ok = {"open":1,"high":2,"low":0.5,"close":1.2,"volume":3}
    a = reg.quality_check(ok, event_time="2026-01-01T00:00:00+00:00", knowledge_time="2026-01-01T00:00:01+00:00", seen=seen)
    seen.add("2026-01-01T00:00:00+00:00")
    b = reg.quality_check(ok, event_time="2026-01-01T00:00:00+00:00", knowledge_time="2026-01-01T00:00:01+00:00", seen=seen)
    assert a["ok"] is True and b["quarantine"] is True

def test_worlds_isolated_and_cross_asset_not_a_cube() -> None:
    assert "COUNTERFACTUAL" in WORLDS
    assert CROSS_ASSET["correlation_matrix"] == "deferred_no_cube"

def test_multi_subject_path_is_inconclusive_not_performance() -> None:
    reg, demo = fixture_scale_demo()
    assert set(demo["members"]) == {"BTC-USD-SPOT","ETH-USD-SPOT"}
    assert demo["lab"]["status"] == "inconclusive" and demo["paper"]["capital"] == 0 and demo["ingested"] is False

def test_persist_checklist_ingest_off() -> None:
    reg, _ = fixture_scale_demo()
    store = open_scaleout_store()
    stats = store.persist_scaleout(reg)
    assert stats["instruments"] == 10 and stats["ingested"] == 0
    assert store.conn.execute("SELECT COUNT(*) AS n FROM ops__production_checklist").fetchone()["n"] >= 10
    assert int(store.conn.execute("SELECT ingestion_enabled FROM ops__schema_gate WHERE phase='activation_f'").fetchone()["ingestion_enabled"]) == 0
    with pytest.raises(LiveQueryDenied):
        store.live().execute("SELECT code FROM ops__scaleout_instrument_plan")
    assert INGESTION_ENABLED is False and list((ROOT/"sql").glob("021*")) == []
