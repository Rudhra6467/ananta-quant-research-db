"""Gate D capability catalog. Available vs reserved vs blocked."""
from __future__ import annotations
from dataclasses import dataclass
LAYERS = ("market_truth", "observation", "state", "regime", "shift", "measurement", "hypothesis", "experiment", "prediction", "risk", "decision", "outcome", "provenance")
UNCERTAINTY = ("UNKNOWN", "INSUFFICIENT_EVIDENCE", "HIGH_UNCERTAINTY", "OUT_OF_DISTRIBUTION", "MODEL_DISAGREEMENT")
AVAILABLE = {"current_regime": "regime", "current_market_state": "state", "members_as_of": "observation", "events_as_of": "shift", "measurement_current": "measurement", "hypothesis_current_status": "hypothesis", "lab_result_as_of": "experiment", "shift_candidate_as_of": "shift", "snapshot_identity": "provenance"}
RESERVED = {"prediction_distribution": "prediction", "risk_budget": "risk", "paper_decision_read": "decision", "outcome_attribution": "outcome"}
BLOCKED = {"raw_market_scan": "market_truth", "mutate_hypothesis": "hypothesis", "mutate_experiment": "experiment", "live_order": "decision", "enable_ingestion": "market_truth", "ranking_engine": "decision", "allocate_capital": "risk"}
CATALOG_VERSION = "agent-catalog-d.v1"
@dataclass(frozen=True)
class Capability:
    name: str
    layer: str
    status: str
    mutation: bool = False
def all_capabilities():
    out = []
    for name, layer in AVAILABLE.items():
        out.append(Capability(name, layer, "available", False))
    for name, layer in RESERVED.items():
        out.append(Capability(name, layer, "reserved", False))
    for name, layer in BLOCKED.items():
        mut = name.startswith("mutate") or name in {"live_order", "enable_ingestion", "allocate_capital"}
        out.append(Capability(name, layer, "blocked", mut))
    return out
