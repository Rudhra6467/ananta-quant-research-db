# Phase 6 verification audit

Status: **COMPLETE**. No Phase 7 implementation.

Verified on `work` tip `0cb2ba6`. Suite: 69 passed, 1 skipped.

## Inventory

Facts (append-only): `research.hypothesis` (identity), `research.hypothesis_status_event`, `research.hypothesis_support_link`.
Definitions: `research.analogue_definition`.
Projections: `analytics.hypothesis_current_status` (rebuildable).
Reused facts: `state.market_state_observation`, `state.regime_observation`.

FKs: hypothesis → relationship_definition; status_event/support_link/current_status → hypothesis.

Live `ops.current_*` unchanged.

## Checks

- Invalid evidence directions rejected. Status history remains queryable.
- Current status = last status event by knowledge_time.
- UPDATE/DELETE of status events blocked.
- Reset cohort does not delete hypothesis events or evidence.
- `memory_as_of(T)` filters `knowledge_time <= T`.
- No analogue scores, grouping, stats engine, predictions, ranking, or ingest.
