from datetime import datetime

from research_db.lifecycle.engine import (
    LIVE_TABLES,
    RSI_REGION,
    incremental_bar,
    possible_rsi_space_size,
    requested_parameter_sets,
    run_fixture_lifecycle,
)
from research_db.lifecycle.features import rsi
from research_db.lifecycle.fixture import BARS, CANONICALIZATION_VERSION, FIXTURE_CODE, HORIZON_BARS


def test_rsi_known_vector() -> None:
    closes = [44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28]
    values = rsi(closes, 14)
    assert values[14] is not None
    assert 60 < values[14] < 80


def test_raw_to_canonical_lineage() -> None:
    memory = run_fixture_lifecycle()
    assert memory.dataset_snapshots[0]["id"] == FIXTURE_CODE
    assert memory.ingestion_runs[0]["status"] == "complete"
    assert memory.canonicalization_runs[0]["version"] == CANONICALIZATION_VERSION
    assert len(memory.raw_events) == BARS
    assert len(memory.canonical_bars) == BARS
    bar = memory.canonical_bars[0]
    raw = memory.raw_events[0]
    assert bar["source_record_id"] == raw["source_record_id"]
    assert bar["close"] == raw["payload"]["close"]
    event = datetime.fromisoformat(bar["event_time"])
    as_of = datetime.fromisoformat(bar["as_of_time"])
    assert as_of > event


def test_parameter_region_not_exploded() -> None:
    memory = run_fixture_lifecycle()
    assert memory.parameter_regions["RSI(12-17)"]["members"] == [f"RSI({p})" for p in RSI_REGION]
    stored_sets = set(memory.parameter_sets)
    assert stored_sets == set(requested_parameter_sets())
    assert possible_rsi_space_size() > len(stored_sets)
    observed_sets = {row["parameter_set"] for row in memory.feature_observations}
    assert observed_sets == stored_sets
    assert len(memory.feature_observations) < possible_rsi_space_size() * BARS


def test_combinations_are_definitions_not_cubes() -> None:
    memory = run_fixture_lifecycle()
    assert "R_RSI_REGION_OVERSOLD_4H" in memory.relationship_definitions
    assert "R_RSI14_OVERSOLD_4H" in memory.relationship_definitions
    assert not hasattr(memory, "combination_cube")


def test_evidence_and_ranks_are_snapshots() -> None:
    memory = run_fixture_lifecycle()
    stages = {e["stage"] for e in memory.evidence}
    assert stages == {"HISTORICAL", "OOS"}
    assert all(e["direction"] in {"supports", "contradicts", "inconclusive"} for e in memory.evidence)
    hist_ranks = [r for r in memory.ranking_snapshots if r["stage"] == "HISTORICAL"]
    oos_ranks = [r for r in memory.ranking_snapshots if r["stage"] == "OOS"]
    assert len(hist_ranks) == 2
    assert len(oos_ranks) == 2
    first = hist_ranks[0]
    assert first["stage"] == "HISTORICAL"
    assert any(r["relationship"] == first["relationship"] and r["stage"] == "OOS" for r in oos_ranks)


def test_live_path_uses_only_operational_tables() -> None:
    memory = run_fixture_lifecycle()
    assert memory.decisions
    assert memory.decisions[0]["action"] in {"ENTER", "WAIT", "SKIP"}
    assert set(memory.live_query_log) <= LIVE_TABLES
    assert "feature_observations" not in memory.live_query_log
    assert "evidence" not in memory.live_query_log
    assert "raw_events" not in memory.live_query_log


def test_counterfactuals_cover_decision_universe() -> None:
    memory = run_fixture_lifecycle()
    paths = {row["action_path"] for row in memory.counterfactuals}
    assert paths == {"ENTER", "WAIT", "SKIP"}
    assert all(row["horizon_bars"] == HORIZON_BARS for row in memory.counterfactuals)


def test_incremental_update_does_not_rescan_for_live_state() -> None:
    memory = run_fixture_lifecycle()
    before_raw = len(memory.raw_events)
    before_obs = len(memory.feature_observations)
    memory.live_query_log.clear()
    result = incremental_bar(memory)
    assert result["new_canonical_bars"] == 1
    assert result["new_feature_observations"] == len(RSI_REGION)
    assert len(memory.raw_events) == before_raw + 1
    assert len(memory.feature_observations) == before_obs + len(RSI_REGION)
    state = next(iter(memory.current_market_state.values()))
    assert state["event_time"] == result["current_event_time"]
    assert memory.operational_applicability
    assert memory.relationship_current_summary
