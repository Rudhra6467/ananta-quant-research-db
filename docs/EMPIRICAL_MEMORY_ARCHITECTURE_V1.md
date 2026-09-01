# Ananta Empirical Memory Architecture v1

Status: **Phase 0 foundation. Not an ingestion approval.**

This document is the schema contract. Migrations after Phase 0 must not violate it.
Full historical ingestion is forbidden until Phase 1 is explicitly approved.

## 0. Approval gate

Do not:

- ingest exchange history
- materialize every indicator combination
- treat a backtest score as knowledge
- let the 5-minute path scan research facts
- overwrite evidence
- promote KEEP / live enablement from this database

Do:

- preserve immutable evidence
- store current belief as a rebuildable projection
- name combinations without persisting every tick of every combination
- keep Ananta execution and this research memory separate

## 1. What this system is

Observe → represent → relate → test → learn.

We are not building a database of answers. We are building structured empirical memory from which Ananta can discover relationships, test them, challenge them, measure strength, know when they fail, and update belief as new data arrives.

Two jobs:

1. **Historical research memory** — deep. Keep failures. Keep rejected regions. Keep counterfactuals.
2. **Operational memory** — tiny. Current market state + already-discovered applicable relationships.

Simplify what the live loop looks at. Do not delete what the system learned.

## 2. Canonical flow and authority

```
raw source manifests / payloads     authority: source + ingestion_run
        ↓
canonical market facts              authority: canonicalization_run + dataset_snapshot
        ↓
feature / regime / state facts      authority: feature_version + as_of information set
        ↓
experiments / trials / evidence     authority: experiment_run + code/config hash
        ↓
validation + rank snapshots         authority: validation_run + scoring_model_version
        ↓
curated current summaries           projection; rebuildable
        ↓
operational cache                   projection; last-known-valid version
        ↓
Ananta Decision Layer               separate system; consumes structured facts
```

Ananta regime labels are hypotheses, not ground truth. This database may store them as *system* observations with explicit provenance. Market Truth and Outcome Truth stay distinct.

## 3. Three layers

| Layer | Purpose | Mutation |
| --- | --- | --- |
| Historical / empirical memory | Immutable facts: market, features, trials, evidence, decisions, counterfactuals | Append-only. Corrections supersede; they do not UPDATE in place. |
| Curated / derived intelligence | Stage scores, robustness, regions, rank, applicability | Rebuildable projections with watermark + model version |
| Operational / cache | Current state, latest features, eligible relationships | Small upsert keyed by instrument/timeframe; versioned |

The operational path never uses raw payloads or full historical evidence as its primary query layer.

## 4. Point-in-time and look-ahead

Every feature, regime, decision, and score snapshot binds:

- `event_time` — market time the observation is about
- `as_of_time` — latest information legally visible when the value was produced
- `recorded_at` — when this database accepted the row
- `dataset_snapshot_id` — which frozen extract
- version ids for definition, code, and canonicalization

`as_of_time` must not include future prints. A 1h bar used for a decision at 14:00 may not include 14:00–15:00 information. If a source revises a bar, append a new raw/canonical row that supersedes the previous one.

## 5. Feature grain (locked)

`feature_observation` grain:

`(feature_version_id, parameter_set_id, instrument_id, timeframe_id, event_time)`

Rules:

- RSI is a **family**, not one feature. RSI(14) is a parameter set of family RSI.
- RSI period 12–17 may later become a `parameter_region`. The six exact sets remain queryable.
- Phase 0 does **not** persist every period on every bar.
- Persist definitions always. Persist observations only when a campaign or the operational set requests them.
- Compute-on-demand is the default for discovery. Storage is earned.

## 6. Relationships and evidence

A `relationship_definition` is a versioned claim, not a backtest row.

Example claim:

`RSI(period in 12..17) + BTC + 1h + bullish-regime → positive 20-bar expectancy`

Normalized terms live in `relationship_term` so the graph can be projected later.

Evidence is append-only and directional: supports / contradicts / inconclusive.

Current confidence is derived from evidence + scoring model version. It is never a mutable column that replaces history.

Stages coexist as snapshots: HISTORICAL, OOS, FORWARD, PAPER, CURRENT.

Cohort membership (`top 10%`, `next 10–25%`) is tied to the **ranking snapshot that selected it**. Recalculating history must not rewrite who was selected.

## 7. Decisions

Eligible universe, not only fills:

- ENTER
- WAIT
- SKIP

Each `decision_event` stores the information set, policy version, candidate set handle, and operational state version used.

`counterfactual_outcome` is filled when horizons mature. SKIP is evidence.

## 8. Search without combinatorial explosion

Persist the search process:

- parameter_space + dimensions + constraints
- search campaign budget
- candidate_generation_event (grid, LHS, Bayesian, neighborhood)
- trial identity even when not fully evaluated

"Not evaluated due to budget" is coverage evidence, not failure of the relationship.

Do not create a table per combination. Do not create a winner table that deletes losers.

## 9. 5-minute path

Allowed reads:

- `ops.current_market_state`
- `ops.current_feature_value`
- `ops.current_regime_state`
- `ops.operational_relationship_applicability`
- `ops.operational_strategy_eligibility`

Forbidden reads on the live path:

- `raw.*`
- full `core` / feature history
- `research.experiment_trial`
- `research.relationship_evidence`
- historical ranking archives

If a required current row is missing, the decision is UNKNOWN / WAIT, not a historical scan.

## 10. Storage stance

PostgreSQL 16 + TimescaleDB is the system of record for Phase 0–5.

Later, cold raw payloads and bulky trial artifacts may move to object storage with checksum + snapshot pointers. That is not Phase 0.

A property graph engine is not required. Graph views are derived.

## 11. Phase 0 entities actually created

Created now (stubs with locked grain):

**ref:** data_source, venue, asset, instrument, timeframe, market_universe

**ops lineage:** dataset_snapshot, ingestion_run, canonicalization_run, schema_gate

**research definitions:** indicator_definition, feature_definition, feature_version, parameter_definition, parameter_set, relationship_definition, relationship_term, outcome_definition, validation_stage

**research facts (empty-ready):** experiment_run, experiment_trial, relationship_evidence, ranking_snapshot, decision_event, counterfactual_outcome

**projections:** analytics.relationship_current_summary

**ops serving:** current_market_state, current_feature_value, current_regime_state, operational_relationship_applicability

Deferred to later phases (named, not migrated): order book facts, equation lineage, paper fill ledger, parameter_region detection runs, search campaign workers, Timescale hypertables on high-volume facts.

## 12. Rebuild rule

Every projection declares:

1. source fact set
2. transform / scoring version
3. computed_at
4. source watermark or snapshot ids
5. deterministic rebuild procedure

If those five are missing, it is not a projection; it is a hidden source of truth. Forbidden.

## 13. Completion of this document

This file plus `docs/PHASES.md` is the Phase 0 architecture gate.

Implementing additional migrations that add ingestion jobs or enable `INGESTION_ENABLED=true` by default violates this document.
