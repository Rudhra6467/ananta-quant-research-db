# Architecture lock audit (2026-09-02)

This is an audit, not a build phase. Phase 2 remains fixture-only.

Locked laws:

- A prediction is an empirical claim, not a trusted fact.
- Prediction value ≠ prediction reliability ≠ knowledge ranking.
- Ananta may return UNKNOWN, INSUFFICIENT_EVIDENCE, HIGH_UNCERTAINTY, OUT_OF_DISTRIBUTION, MODEL_DISAGREEMENT.
- Reset means a new experiment cohort / snapshot. It never deletes historical truth or failed experiments.

## Verdict

The foundation can support the 15 future capabilities without a rewrite if we keep facts append-only, identities stable, and later domains as new tables in reserved schemas.

Two contracts would have forced a redesign. They are corrected in this change and nothing else is implemented.

1. `ref.asset.symbol` is no longer globally unique. Identity is `(asset_class, symbol)` so crypto BTC and an equity ticker BTC can coexist.
2. `research.relationship_evidence.direction` now allows `untested|supports|contradicts|inconclusive|invalidated|decayed`.
3. Empty schemas `prediction` and `portfolio` are reserved beside existing `world`.

`market.ohlcv_bar` is one market-fact family. It is not the only allowed market truth.

`research.decision_event` is a TAKE/WAIT/SKIP ledger. It is not the prediction store.

`research.ranking_snapshot.score` is one scoring-model scalar at one as_of. It is not reliability and not the prediction value.

## How each capability attaches later

| # | Capability | How the current foundation supports it | Blocker removed / still open |
| --- | --- | --- | --- |
| 1 | World / external conditions | Schema `world` exists. Later: versioned condition_definition + condition_observation with event_time + knowledge_time + source. No per-disaster tables. | Open table, not a redesign. |
| 2 | Shock → path → condition → market response | Later graph of typed links (condition → condition / market / asset) using stable ids. Market responses reuse `market.*` facts. | Do not store paths as columns on bars. |
| 3 | Scenario / counterfactual experiments | `experiment_run` + `dataset_snapshot` + `counterfactual_outcome` already isolate a cohort. Scenarios become an experiment kind with assumed shocks, not overwritten history. | Do not reuse decision_event as a scenario. |
| 4 | Portfolio exposure / impact | Schema `portfolio` reserved. Holdings are identities + weights as-of knowledge_time. Impact joins scenario output to holdings. | Asset identity now class-scoped. |
| 5 | Prediction → outcome → error → validation | Schema `prediction` reserved. Separate rows: claim, mature window, observed outcome, error, validation_stage. Outcome is market/world truth, never the claim row mutated. | Do not put predictions in `feature.observation`. |
| 6 | Uncertainty / confidence | Prediction row carries uncertainty + epistemic_status. Numeric value may be null when status is not a number. | Feature values stay numeric; predictions must not. |
| 7 | Model disagreement | Multiple claims can share target/horizon and differ by model_id / source. Disagreement is derived, not a single blended cell that erases rivals. | Need future model identity table; not required to persist now. |
| 8 | Reliability ≠ prediction value | Reliability is a rating object built from evidence dimensions. Ranking snapshot remains a dated projection of one scoring model. | Never write reliability onto the prediction value column. |
| 9 | Multi-factor ranking | Ranking snapshot already keys relationship × stage × scoring_model_version × as_of. Dimension breakdowns attach as child rows later. | Single `score` is a projection, not the dimension store. |
| 10 | Decay / invalidation / current relevance | Evidence direction now includes `invalidated` and `decayed`. Current relevance lives in rebuildable `analytics` / `ops` projections. | Historical evidence rows stay append-only. |
| 11 | Experiment isolation and reset | Reset = new `experiment_run` + new snapshot/cohort label. `status` may be abandoned. DELETE of raw/market/feature facts is forbidden. | No erase API will be added. |
| 12 | Negative knowledge | `contradicts`, `inconclusive`, `invalidated`, failed trials, SKIP/WAIT counterfactuals. Insufficient evidence is a valid result. | Do not delete failed runs. |
| 13 | PIT reconstruction at T | Facts expose event_time + knowledge_time (Phase 2) or as_of_time (projections). Query: knowledge_time <= T. Definitions are versioned. | Later world/prediction rows must use the same two clocks. |
| 14 | Reproducibility | Snapshot + feature/relationship versions + parameter_set + experiment code_commit/config_hash + raw→canon lineage. | Model/code commit must be stored on the experiment when predictions exist. |
| 15 | Multi-market expansion | Venue + asset_class + instrument.kind (spot today; future/option/swap later). New market-fact tables per family (trades, funding, options chain) rather than widening OHLCV. | Quote asset is nullable so non-spot contracts can exist later. |

## What this change does not do

No prediction tables. No world event rows. No ranking implementation. No paper. No exchange ingest. No 10-asset campaign.
