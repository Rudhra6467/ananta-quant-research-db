# Architecture Lock v2 (2026-09-03)

This document hardens the constitution before Phase 5. It is **not** an implementation phase.

## What changed in contracts

1. **Universal lineage** — Generic `ops.lineage_edge` / provenance-graph abstraction locked; not feature-specific.
2. **Conditional/cohort knowledge** — Empirical claims must be conditionable; no unconditional “X predicts Y” as the only form; no Cartesian cube.
3. **Prediction distributions** — Extensible distribution representations reserved; fixed quantile columns are not the sole abstraction.
4. **Feature stability/decay** — Quantitative measurements reserved as evidence, not a magic score.
5. **Cross-asset derived state** — Correlation/PCA/network measures reserved as derived state, not market OHLCV.
6. **World/scenario separation** — REALIZED / REPLAY / COUNTERFACTUAL / SYNTHETIC kept distinct.
7. **Microstructure families** — Reserved under market truth; interpretation stays downstream.
8. **Grouping / hierarchy (5A)** — Market→class→sector→group→asset→instrument with temporal many-to-many membership.
9. **Uncertainty, negative knowledge, reset, PIT, reproducibility** — Reaffirmed as permanent laws.
10. **Expandability** — One ontology across crypto → equities → FX → rates → commodities → options.

## Why each prevents redesign

Without lineage: later causal/path questions force ad-hoc foreign keys and per-domain DAGs.  
Without conditionality: evidence tables become unconditional and cannot answer regime/asset-specific questions without rewrite.  
Without distribution-ready predictions: a point-estimate-only schema forces destructive migration.  
Without derived-state separation: cross-asset metrics pollute bar grain.  
Without world/scenario kinds: history and simulation collapse.  
Without microstructure families: options/depth force widening OHLCV.  
Without grouping: multi-market hierarchy becomes per-country hard-codes.  
Without negative knowledge / reset / PIT: the system cannot learn from failure or reconstruct past knowledge.

## Reserved vs implemented

| Capability | Status |
| --- | --- |
| Phases 0–4 fixture foundation | **Implemented** |
| Lineage graph tables | Reserved (contract) |
| Group membership engine | Reserved (contract) |
| Conditional predicate store | Reserved (contract) |
| Prediction engine / tables | Reserved (not Phase 5) |
| Ranking engine | Not implemented |
| Scenario generation | Reserved |
| Microstructure ingest | Reserved |
| Production exchange ingest | Forbidden until approved |
| Paper / 10-asset campaign | Not implemented |

## Phase 4 unchanged

Observation engine remains request-driven RSI(12–17), fixture-only, no cube, no ingest.

## Phase 5 bound

Fixture-only current state / regime / memory projection onto `ops.current_*`. No ranking, prediction, scenario, paper, or production ingest.
