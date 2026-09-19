# Phase 6 — Memory / Hypothesis

Status: implemented on `work`. Fixture only. Architecture locked.

## Object plan

| object/table | purpose | invariants | write | read | relation to P2–5 |
| --- | --- | --- | --- | --- | --- |
| `state.market_state_observation` | historical market-state memory | already append-only; event_time + knowledge_time | none in P6 | `memory_as_of(T)` | reuse P5 |
| `state.regime_observation` | historical regime memory (system hypothesis labels) | append-only; not market truth | none in P6 | `memory_as_of(T)` | reuse P5 |
| `research.hypothesis` | first-class claim wrapper around a relationship | claim_kind=system_hypothesis; not a prediction; not market truth | insert identity only | research | FK to P2 `relationship_definition` |
| `research.hypothesis_status_event` | lifecycle: proposed/under_test/supported/contradicted/inconclusive/invalidated/decayed | append-only; event_time + knowledge_time; never overwrite | append | research | links optional evidence row (P3) |
| `research.hypothesis_support_link` | provenance to evidence / state / regime / feature obs | append-only; source_kind constrained | append | research | P3 evidence, P5 state, P4 feature ids |
| `research.analogue_definition` | similarity identity only | no scores, no engine | insert definition | research | prevents later incompatible semantics |
| `analytics.hypothesis_current_status` | latest status projection | rebuildable; not live ops | replace projection | analytics | derived from status events |
| `ops.current_*` | unchanged live surface | not widened | none | live | P2/P5 |

Forbidden: grouping, stats engine, cross-asset, lineage graph, predictions, scenarios, ranking, paper, ingest.
