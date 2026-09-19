# Phase 7 — Quantitative empirical measurement DESIGN

Status: **DESIGN ONLY**. Not implemented. Architecture remains locked.
Phase 6 is COMPLETE and must not be modified unless a defect is found.

Purpose: define how Ananta *represents* empirical measurements about observations, features, states, relationships, and hypotheses — temporally correct, reproducible, conditional, extensible.

Purpose is **not** a statistics warehouse, a cube of every metric × asset × regime, or a measurement engine in this document.

---

## Canonical answers

### 1. Canonical abstraction

An **empirical measurement** is a versioned, requested computation of a *statistic or test* over an identified sample, evaluated at an information set.

It is not a market fact, feature observation, state/regime fact, hypothesis, prediction, or rank.

It is evidence-shaped: append-only, two clocks, provenance, optional condition/cohort, optional distribution payload.

### 2. Observation vs measurement vs experiment vs outcome

| Concept | Meaning |
| --- | --- |
| Observation | What was seen (bar, feature value, state label) |
| Measurement | What we computed *about* a sample of observations |
| Experiment | Isolated cohort/run/window that produced the sample |
| Outcome | Realized subsequent truth used as a measurement target |

P3 `relationship_evidence` is an early scalar measurement. Phase 7 generalizes that shape without replacing it.

### 3. Link to hypotheses / relationships

`research.measurement_request` names what to compute. `research.measurement_observation` may point at hypothesis_id, relationship_id, experiment_run_id, validation_stage_id. A hypothesis is evaluated *by* measurements.

### 4. Link to observations / features / states

Provenance: dataset_snapshot, experiment_run, sample specifier, optional support links (`feature_observation | market_state | regime_state | evidence`). Reuse P6 link pattern. Not the P12 lineage graph. Do not embed raw series in the measurement row.

### 5. Conditions (no cube)

Store `condition_digest` of a declared predicate (asset, timeframe, regime, holding period, cohort). Full predicate engine is Phase 9. Never materialize asset × timeframe × regime × metric × horizon.

### 6. Temporal / reproducibility

event_time + knowledge_time + experiment_run + dataset_snapshot + definition version + optional seed. Recompute appends a new knowledge_time; it does not update the old row.

### 7. Uncertainty ≠ significance ≠ reliability ≠ rank

point_value (nullable) + uncertainty payload + epistemic_status (`UNKNOWN | INSUFFICIENT_EVIDENCE | HIGH_UNCERTAINTY | OBSERVED | INCONCLUSIVE`) + optional test_result payload. A small p-value is not a rank.

### 8. Distributions

Do not fix q05..q95 columns. Optional child `research.measurement_distribution` with representation `empirical | parametric | quantile | conformal` and JSON payload.

### 9. Negative / inconclusive

Append-only. Reset = new run, not DELETE.

### 10–12. Recompute, lookahead, no cube

Deterministic request identity. knowledge_time must dominate inputs. Outcomes only after matured horizon. Only requested definitions are materialized (P4 law).

### 13. Future consumers

P8 group id in digest; P9 predicate; P10 derived-state families; P11 path evidence; P12 measurement as lineage node; P13 calibration measurements; P15 ranking consumes projections.

### 14. Phase 7 vs later

When coding is approved: definition + request + observation fact + optional distribution + current projection + map P3 evidence. Not: bootstrap/Wasserstein/IC engines, grouping, predictions, ranking, ingest.

---

## Object table

| object | purpose | fact/projection | temporal | provenance | conditions | write | read | future consumers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `research.measurement_family` | catalog of kinds | definition | none | version | n/a | insert | research | P7+ |
| `research.measurement_definition` | named statistic + params | definition | none | version | n/a | insert | research | engine later |
| `research.measurement_request` | requested compute | definition | created_at | definition_id | condition_digest | insert | research | avoids cube |
| `research.measurement_observation` | one result | **fact** | two clocks | snapshot/run/hypothesis | condition_digest | append | research | P11–P15 |
| `research.measurement_distribution` | optional distribution | **fact** child | same clocks | parent measurement | inherited | append | research | P13 |
| `analytics.measurement_current` | latest per key | **projection** | watermark | rebuilt | same digest | replace | analytics | P15 |
| `research.relationship_evidence` | P3 scalar evidence | fact | knowledge_time | trial/run | implicit | unchanged | research | mapped |
| `research.hypothesis*` | P6 lifecycle | fact | two clocks | support links | implicit | unchanged | research | evaluated by measurements |

Do not add these to `ops.current_*` in Phase 7.

## A. Boundary

Fixture representation of requested measurements. No live-surface widening. No stats engine in this design checkpoint.

## B. Invariants

observation ≠ measurement ≠ hypothesis ≠ prediction ≠ rank. Append-only negative knowledge. Reset ≠ delete. Two clocks. Requested materialization only.

## C. Deferred

Engines → later P7 implementation or stay as families. Predicates P9. Groups P8. Cross-asset P10. Causal P11. Lineage P12. Predictions P13. Scenarios P14. Ranking P15.

## D. Example flows

1. observations → P3 evidence → P6 hypothesis → P7 effect-size measurement on the same relationship.
2. requested half-life on RSI(14) under a regime digest; decayed status stays a P6 event.
3. n too small → INSUFFICIENT_EVIDENCE fact kept forever.

## E. Schema proposal

Generic columns (`point_value`, `payload`, `epistemic_status`, `condition_digest`). Families distinguish kind. **No migrations in this checkpoint.**

## F. Risks

Per-statistic tables; typed condition columns; writing measurements into live ops; p-value as rank; unrequested computes. Mitigations above. No P2–P6 redesign required.
