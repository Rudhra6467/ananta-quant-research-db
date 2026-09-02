"""In-memory empirical memory. Append-only facts; rebuildable current projections."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EmpiricalMemory:
    raw_events: list[dict[str, Any]] = field(default_factory=list)
    canonical_bars: list[dict[str, Any]] = field(default_factory=list)
    dataset_snapshots: list[dict[str, Any]] = field(default_factory=list)
    ingestion_runs: list[dict[str, Any]] = field(default_factory=list)
    canonicalization_runs: list[dict[str, Any]] = field(default_factory=list)

    feature_definitions: dict[str, dict[str, Any]] = field(default_factory=dict)
    parameter_sets: dict[str, dict[str, Any]] = field(default_factory=dict)
    parameter_regions: dict[str, dict[str, Any]] = field(default_factory=dict)
    feature_observations: list[dict[str, Any]] = field(default_factory=list)

    relationship_definitions: dict[str, dict[str, Any]] = field(default_factory=dict)
    experiment_runs: list[dict[str, Any]] = field(default_factory=list)
    experiment_trials: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    ranking_snapshots: list[dict[str, Any]] = field(default_factory=list)
    decisions: list[dict[str, Any]] = field(default_factory=list)
    counterfactuals: list[dict[str, Any]] = field(default_factory=list)

    current_market_state: dict[str, dict[str, Any]] = field(default_factory=dict)
    current_feature_value: dict[str, dict[str, Any]] = field(default_factory=dict)
    current_regime_state: dict[str, dict[str, Any]] = field(default_factory=dict)
    operational_applicability: dict[str, dict[str, Any]] = field(default_factory=dict)
    relationship_current_summary: dict[str, dict[str, Any]] = field(default_factory=dict)

    live_query_log: list[str] = field(default_factory=list)
    compute_log: list[dict[str, Any]] = field(default_factory=list)

    def append_fact(self, bucket: list[dict[str, Any]], row: dict[str, Any]) -> dict[str, Any]:
        bucket.append(row)
        return row

    def live_get(self, name: str, key: str | None = None) -> Any:
        allowed = {
            "current_market_state",
            "current_feature_value",
            "current_regime_state",
            "operational_applicability",
        }
        if name not in allowed:
            raise PermissionError(f"live path may not read {name}")
        self.live_query_log.append(name)
        table = getattr(self, name)
        if key is None:
            return table
        return table.get(key)

    def observation_keys(self) -> set[tuple[str, str]]:
        return {(row["parameter_set"], row["event_time"]) for row in self.feature_observations}
