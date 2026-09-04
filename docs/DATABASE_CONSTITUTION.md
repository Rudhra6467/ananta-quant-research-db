# Ananta Database Constitution (locked 2026-09-03)

**Status: ARCHITECTURE LOCKED.** Semantics and invariants are constitutional. Physical tables, indexes, engines, and taxonomies may evolve without redesigning the meaning of truth.

The product is an empirical intelligence platform — a universal financial-world representation — not a feature dump, crash predictor, or trading bot.

## Core flow

See locked architecture diagrams in-repo. Meaning of truth is unchanged.

## Constitutional principle

Every observation should carry **time, source, context, state, uncertainty, relationship, and eventual outcome** whenever those concepts apply.

Normalize truth and provenance. Denormalize only for performance. Materialize expensive derived observations only when **requested, promoted, or operationally necessary**.

Lock **semantics and invariants**. Do not permanently lock exact physical tables, indexes, column layouts, storage engines, feature implementations, model architectures, prediction encodings, grouping taxonomies, or ingestion technology.

## Five constitutional pillars

### 1. Temporal truth
`event_time ≠ knowledge_time`. Reconstruct what was knowable at T. Lookahead leakage is forbidden.

### 2. Provenance and lineage
Generic provenance graph contract (`ops.lineage_edge`). Full graph later; contract locked.

### 3. Hierarchical / group reasoning
Time-dependent many-to-many membership. No group×asset×timeframe×regime cube.

### 4. Conditional empirical knowledge
No implicit “RSI(14) predicts returns.” Evidence is conditional. Selective materialization only.

### 5. Truth vs interpretation
MARKET FACT → DERIVED OBSERVATION → STATE → INTERPRETATION → PREDICTION → OUTCOME must never collapse.

## Locked invariants

Live path reads only bounded `ops.current_*`. `INGESTION_ENABLED` remains false until an explicitly approved production-ingest phase. Negative knowledge is permanent. Reset is a new cohort, never a delete.

## Physical store

One PostgreSQL 16 + TimescaleDB instance. Logical domains are schemas.

## Phase posture

Phases 0–20 are represented on the fixture laboratory. See `docs/CHECKPOINT_P0_P20.md`.

## Fixture checkpoint (locked 2026-09-04)

Commit `0871b49` is the Phase 0–20 **fixture-architecture completion checkpoint**.

A roadmap phase represented and tested on the fixture is **not** equivalent to that capability being scientifically validated on real market data.

- The fixture proves architecture and control behavior.
- Real data must prove data integrity, statistical validity, reproducibility, computational behavior, and usefulness.

No further fixture-only phase numbers will be invented to extend this list. Work after this checkpoint is an **activation program** and requires explicit approval before each transition.

If an activation requirement conflicts with this constitution, stop and report the conflict. Do not rewrite the constitution to accommodate activation convenience.
