import pytest
from research_db.ingest.contract import IngestDenied, ProviderKind
from research_db.ingest.fixture_adapter import FixtureSource
from research_db.ingest.orchestrator import INGESTION_ENABLED, IngestionOrchestrator
from research_db.ingest.validate import validate_ohlcv
from research_db.lab.engine import ExperimentSpec, LaboratoryDenied
from research_db.paper.engine import PaperLedger
from research_db.persist import LiveQueryDenied, open_activation_store
from research_db.shift.engine import ShiftReview
class LiveProvider:
    code = "kraken"
    kind = ProviderKind.LIVE
    def records(self):
        return []
def test_ingestion_enabled_is_false() -> None:
    assert INGESTION_ENABLED is False
def test_live_provider_denied() -> None:
    with pytest.raises(IngestDenied):
        IngestionOrchestrator().run(LiveProvider(), run_code="x", snapshot_code="y")
def test_fixture_adapter_is_not_live_truth() -> None:
    src = FixtureSource()
    assert src.kind == ProviderKind.FIXTURE
    recs = src.records()
    assert recs and recs[0].provider_kind == "fixture"
    orch = IngestionOrchestrator()
    batch = orch.run(src, run_code="FIX_A1", snapshot_code="FIXTURE")
    assert batch.accepted and batch.provider_kind == "fixture"
    batch2 = orch.run(src, run_code="FIX_A2", snapshot_code="FIXTURE")
    assert batch2.accepted == [] and batch2.duplicates == len(batch.accepted)
def test_validation_quarantines_bad_bar() -> None:
    bad = validate_ohlcv({"open": 1, "high": 0.5, "low": 2, "close": 1, "volume": 1}, event_time="2026-01-01T00:00:00+00:00", knowledge_time="2026-01-01T00:00:01+00:00")
    assert bad.ok is False
def test_persist_audit_keeps_ingest_off() -> None:
    store = open_activation_store()
    orch = IngestionOrchestrator()
    orch.run(FixtureSource(), run_code="FIX_A1", snapshot_code="FIXTURE")
    stats = store.persist_ingest_batch(orch)
    assert stats["ingestion_enabled"] == 0
    row = store.conn.execute("SELECT ingestion_enabled, provider_kind FROM ops__ingest_audit").fetchone()
    assert int(row["ingestion_enabled"]) == 0 and row["provider_kind"] == "fixture"
    with pytest.raises(LiveQueryDenied):
        store.live().execute("SELECT run_code FROM ops__ingest_audit")
def test_lab_experiment_keeps_negative_results() -> None:
    spec = ExperimentSpec("EXP_FIXTURE_RSI", "FIXTURE", "Does RSI region associate with next-hour return?")
    spec.record("inconclusive", "n too small on 48 bars")
    with pytest.raises(LaboratoryDenied):
        spec.record("win", "no")
def test_shift_review_is_not_a_live_claim() -> None:
    row = ShiftReview().note("regime_transition", "E_SHIFT_T24", "fixture annotation only")
    assert row["live_claim"] is False
def test_paper_information_set_zero_capital() -> None:
    d = PaperLedger().decide("AVERAGE", "WAIT", "2026-01-03T00:00:00+00:00", "insufficient evidence", "current_regime", information_set={"as_of": "2026-01-03T00:00:00+00:00", "queries": ["current_regime"]})
    assert d["capital"] == 0 and d["live_order"] is False
