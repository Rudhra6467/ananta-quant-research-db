# Implementation phases

No phase starts full-market ingestion. Promotion requires the completion test of the prior phase.

| Phase | Name | Allowed | Forbidden | Completion test |
| --- | --- | --- | --- | --- |
| 0 | Foundation | Docs, schemas, identities, evidence stubs, current-state stubs, static tests | Ingest 5y data, enable strategies, KEEP | Architecture doc + Phase 0 DDL/models + tests pass without a live market feed |
| 1 | Canonical market facts | Small fixture bars (BTC 1h sample), raw→canonical lineage, PIT fields | Broad universe ingest | One fixture snapshot reconstructs a bar with source + canonicalization run |
| 2 | Features on demand | Feature definitions + compute for a campaign; persist only requested observations | Persist every RSI period on every 1m bar | RSI(12–17) on fixture BTC 1h can be computed and attributed |
| 3 | Evidence + decisions | Trials, ENTER/WAIT/SKIP, counterfactual stubs on fixture | Promote a relationship to operational eligibility | Immutable evidence rows; current summary rebuilds from them |
| 4 | Ranking snapshots | Historical vs OOS score snapshots, frozen cohort membership | Overwrite a historical rank | Rank trajectory queryable; cohort tied to snapshot time |
| 5 | Operational projections | current_market_state + applicability for fixture | Live evaluator scans research facts | Query-plan contract: live path hits only ops projections |
| 6 | Forward bookkeeping | 30–40 day window protocol, frozen candidates | Change parameters mid-forward | Protocol encoded; no retroactive cohort rewrite |
| 7 | Paper cohorts | Two paper bands from a named ranking snapshot | Live capital, autonomy | Paper facts append; ranks update as new snapshots |

Phase 0 is **not** permission to implement Phases 1–7 in the same change.
