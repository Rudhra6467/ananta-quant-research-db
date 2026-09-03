# Ananta Database Constitution (locked 2026-09-03)

**Status: ARCHITECTURE LOCKED.** Semantics and invariants are constitutional. Physical tables, indexes, engines, and taxonomies may evolve without redesigning the meaning of truth.

The product is an empirical intelligence platform — a universal financial-world representation — not a feature dump, crash predictor, or trading bot.

## Core flow

```text
MARKET TRUTH                    WORLD / EVENTS
     │                                │
Canonical Facts              Events / Shocks
     │                                │
     └──────────────┬─────────────────┘
                    ▼
              OBSERVATIONS
                    │
     ┌──────────────┼──────────────┐
  Features        State      Relationships
     │              │              │
     └──────────────┼──────────────┘
                    ▼
              Regime / Memory
                    │
           ┌────────┴────────┐
      Hypotheses         Similarity
           │
         Models
           │
      Predictions
           │
       Decisions
           │
        Outcomes
           │
       Validation
           │
        Learning
```

Cross-cutting dimensions (apply everywhere they are applicable):

```text
TIME · SOURCE · PROVENANCE · LINEAGE · CONTEXT · UNCERTAINTY
GROUP / HIERARCHY · COHORT · EXPERIMENT · SNAPSHOT · REPRODUCIBILITY
```

## Constitutional principle

Every observation should carry **time, source, context, state, uncertainty, relationship, and eventual outcome** whenever those concepts apply.

Normalize truth and provenance. Denormalize only for performance. Materialize expensive derived observations only when **requested, promoted, or operationally necessary**.

Lock **semantics and invariants**. Do not permanently lock exact physical tables, indexes, column layouts, storage engines, feature implementations, model architectures, prediction encodings, grouping taxonomies, or ingestion technology.

## Five constitutional pillars

### 1. Temporal truth

Where applicable, knowledge-bearing objects distinguish:

`event_time ≠ knowledge_time`

Ananta must reconstruct: **What was knowable at timestamp T?** Lookahead leakage is forbidden.

### 2. Provenance and lineage

Snapshot/run lineage is necessary but not sufficient. Ananta will support a **generic provenance graph** (reserved abstraction: `ops.lineage_edge` / provenance graph), not a feature-only DAG.

Eventually connectable:

```text
raw → canonical → feature → state → regime → similarity → relationship/hypothesis
    → model → prediction → decision → outcome → validation
```

and:

```text
world event → shock → transmission path → intermediate condition
    → market state → prediction → portfolio impact
```

Preserve parent/child identity, transformation/version, run, dataset snapshot, source, and relevant timestamps. Full graph implementation is a later phase; the **contract is locked now**.

### 3. Hierarchical / group reasoning

First-class grouping is part of market representation (not UI-only):

```text
Market → asset class → sector/category → group → asset → instrument
```

Many-to-many membership, effective/expiry times, historical reconstruction of membership, group-level state/regime/relationships/cohorts, aggregation and drill-down — all reserved. Group classification is **time-dependent knowledge**, not an eternal fact. No group×asset×timeframe×regime Cartesian cube. Same ontology across Crypto → US → Canada → India → Commodities → FX.

### 4. Conditional empirical knowledge

Forbidden as an implicit claim: “RSI(14) predicts returns.”

Required form: evidence conditioned on instrument, timeframe, regime, volatility/liquidity/structure, cross-asset state, world conditions, event proximity, holding period, strategy, experiment cohort — via **predicates, dimensions, and cohort definitions**, with selective materialization only. No unconditional empirical cube.

### 5. Truth vs interpretation

Never collapse:

```text
MARKET FACT → DERIVED OBSERVATION → STATE → INTERPRETATION → PREDICTION → OUTCOME
```

What **happened** must remain separable from what the system **believed**.

## Locked invariants

| Invariant | Rule |
| --- | --- |
| Prediction | Prediction value ≠ uncertainty ≠ reliability ≠ ranking |
| Distributions | Future predictions support point, parametric, empirical, quantile, conformal forms — not fixed q05…q95 columns as the only model |
| Uncertainty vocabulary | UNKNOWN, INSUFFICIENT_EVIDENCE, HIGH_UNCERTAINTY, OUT_OF_DISTRIBUTION, MODEL_DISAGREEMENT — not forced into a single number |
| Negative knowledge | Failed, contradicted, invalidated, decayed, inconclusive results are permanent; never silently deleted |
| Reset | New experiment/cohort/run/snapshot — never erase history or failed experiments |
| Market facts | `market.ohlcv_bar` is one family; trades, quotes, books, funding, OI, liquidations are additional market-truth families later |
| Derived vs raw | Correlation, PCA, entropy, depth imbalance, VPIN-like measures are derived — not stored as raw OHLCV |
| Cross-asset | Derived state snapshots only; never widen bar rows into a multi-asset cube |
| World/scenarios | REALIZED HISTORY ≠ HISTORICAL REPLAY ≠ COUNTERFACTUAL ≠ SYNTHETIC SIMULATION |
| Live path | Reads only bounded `ops.current_*` projections |
| Ingest gate | `INGESTION_ENABLED` remains false until an explicitly approved production-ingest phase |
| Expandability | One market ontology instantiated per market — never throw away and redesign per geography |

## Reserved schemas / abstractions (documented, not fully implemented)

- `world`, `prediction`, `portfolio` (already reserved)
- `ops.lineage_edge` / provenance graph (contract only)
- Group identity + membership relationships (contract only)
- Conditional predicate / cohort definitions (contract only)
- Feature stability/decay measurements as evidence (contract only)
- Cross-asset derived state families (contract only)
- Scenario path identity with snapshot, assumptions, seed, generator (contract only)

## Physical store

One PostgreSQL 16 + TimescaleDB instance. Logical domains are schemas.

## Phase posture

Phases 0–4: fixture-only foundation (architecture, lifecycle proof, market truth, evidence, observation engine).

Phase 5 (next implementation, still fixture-only): market truth → current features → current market state → current regime → bounded operational projection. Live path remains `ops.current_*` only.

Phase 5 does **not** implement production ingest, ranking, predictions, scenarios, paper trading, 10-asset campaign, full microstructure, grouping engine, or ML discovery.
