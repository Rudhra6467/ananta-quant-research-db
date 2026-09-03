# Implementation phases

Constitution **locked 2026-09-03** (see `DATABASE_CONSTITUTION.md`, `ARCHITECTURE_LOCK_V2.md`).

No phase starts full-market ingestion. A phase is complete only after design, tests, and the completion gate.

| Phase | Name | Status |
| --- | --- | --- |
| 0 | Architecture & constitution | done on `main` |
| 1 | Empirical fixture proof | done on `main` |
| 2 | Persistent market truth foundation | merged to `main` |
| 3 | Fixture evidence persistence | merged to `main` |
| 4 | Feature observation engine | merged to `main` |
| — | Architecture lock v2 (lineage, cohort, group, distributions) | this branch — docs only |
| 5 | Current state / regime / bounded ops projection | not started — fixture only |
| 6–17 | Memory, hypothesis, prediction, scenario, ranking, veto, campaigns | not started |

Phase 5 Forbidden: exchange ingest, ranking, predictions, scenarios, paper, 10-asset campaign, grouping engine, ML discovery.

Phase 0–5 still forbid full-history ingestion.
