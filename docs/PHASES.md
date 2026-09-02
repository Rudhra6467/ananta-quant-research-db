# Implementation phases

No phase starts full-market ingestion. Promotion requires the completion test of the prior phase.

| Phase | Name | Allowed | Forbidden | Completion test |
| --- | --- | --- | --- | --- |
| 0 | Foundation | Docs, schemas, identities, evidence stubs, current-state stubs, static tests | Ingest 5y data, enable strategies, KEEP | Architecture doc + Phase 0 DDL/models + tests pass without a live market feed |
| 1 | Fixture lifecycle proof | Deterministic BTC 1h fixture; raw→canonical PIT; requested RSI(12–17) only; region; two relationships; HISTORICAL+OOS evidence; rank snapshots; live ENTER/WAIT/SKIP; one-bar increment | Exchange ingest, combination cubes, KEEP | Tests in `tests/test_phase1_lifecycle.py` pass without a market feed |
| 2 | Features on demand | Feature definitions + compute for a campaign; persist only requested observations | Persist every RSI period on every 1m bar | RSI(12–17) on fixture BTC 1h can be computed and attributed |
| 3 | Evidence + decisions | Trials, ENTER/WAIT/SKIP, counterfactual stubs on fixture | Promote a relationship to operational eligibility | Immutable evidence rows; current summary rebuilds from them |
| 4 | Ranking snapshots | Historical vs OOS score snapshots, frozen cohort membership | Overwrite a historical rank | Rank trajectory queryable; cohort tied to snapshot time |
| 5 | Operational projections | current_market_state + applicability for fixture | Live evaluator scans research facts | Query-plan contract: live path hits only ops projections |
| 6 | Forward bookkeeping | 30–40 day window protocol, frozen candidates | Change parameters mid-forward | Protocol encoded; no retroactive cohort rewrite |
| 7 | Paper cohorts | Two paper bands from a named ranking snapshot | Live capital, autonomy | Paper facts append; ranks update as new snapshots |

Phase 1 on the fixture is a **process proof** of later stages (features, evidence, ranks, live path) in memory. It does not complete Phases 2–7 against Postgres, and it is not permission to ingest a market universe.

Phase 0 / 1 still forbid full-history ingestion.
