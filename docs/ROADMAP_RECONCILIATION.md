# Roadmap reconciliation (Constitution v2 × Phase 6+)

Status: **docs only**. Architecture remains locked. Phase 6 is **not** approved for implementation.

Original Phase 6 label after lock v2 was a lump:

> 6–17 Memory, hypothesis, prediction, scenario, ranking, veto, campaigns

That label is too coarse. This document assigns every Constitution v2 capability an explicit future home without implementing those systems.

## Original Phase 6 meaning

Before Constitution v2 hardening, Phase 6 meant the first **memory / hypothesis** slice after current-state projections:

- keep historical market-state and regime rows queryable as memory
- treat Ananta regime as a hypothesis, not market truth
- attach hypotheses to relationships/evidence
- accumulate contradiction, invalidation, decay, negative knowledge
- optional similarity / analogue lookup later in the same family

It was **not** originally a grouping engine, prediction engine, scenario generator, lineage graph, or 10-asset campaign.

## Reconciled phase map (6–17)

| Phase | Home | Implement now? |
| --- | --- | --- |
| 6 | Empirical memory + hypothesis lifecycle (fixture) | No — awaiting approval |
| 7 | Quantitative empirical measurements (stats as evidence objects) | No |
| 8 | Grouping / hierarchy identity + temporal membership | No |
| 9 | Conditional / cohort predicates | No |
| 10 | Cross-asset derived state | No |
| 11 | World events + causal transmission paths | No |
| 12 | Universal lineage / provenance graph | No |
| 13 | Prediction architecture (distributions, uncertainty, reliability) | No |
| 14 | Scenarios: replay / counterfactual / synthetic | No |
| 15 | Ranking, promotion, veto, current-knowledge compilation | No |
| 16 | Microstructure market-fact families | No |
| 17 | Multi-market expansion, paper, approved ingest campaigns | No |

Phases 0–5 stay as implemented. Full-history ingest remains forbidden until Phase 17 is explicitly approved.

## Phase 6 recommended scope (pending approval)

In:

- treat existing `state.*_observation` rows as historical memory (no redesign)
- first-class `research.hypothesis` lifecycle around existing relationship/evidence
- fixture-only analogue/similarity *definition* if needed to avoid later redesign
- preserve negative knowledge and PIT on every new object

Out:

- grouping engine
- statistical library / bootstrap engine
- cross-asset PCA
- lineage graph materialization
- prediction tables
- scenario generators
- ranking engine
- paper / 10-asset / exchange ingest
