# Constitution alignment before Phase 2

Reviewed against Phase 0 models + Phase 1 fixture engine on `main` @ 24b6e72.

## 1. Conflicts

| Item | Verdict |
| --- | --- |
| Old `PHASES.md` numbered 0–7 | Constitution 0–17 wins. Phase 2 is Persistent Market Truth Foundation. |
| Phase 1 in-memory evidence and ranks | Process proof only. Phase 2 does not persist those rows. |
| Phase 0 `as_of_time` vs `knowledge_timestamp` | Phase 2 facts use `event_time` + `knowledge_time`. |
| Phase 0 schemas vs world/market/feature | Add schemas; do not rename Phase 0 identity tables. |

## 2. Missing (not implemented now)

world registry; prediction/outcome/error stores; scenario/portfolio; source revisions; live Timescale operator apply.

## 3. Schema changes before Phase 2

Add `world`, `market`, `feature`. Add append-only raw events, OHLCV bars, requested observations, parameter regions, combination requests. Gate `phase2` with ingestion_enabled=false.

## 4. PIT / lineage

knowledge_time >= event_time. PIT read uses both clocks. Identities are deterministic UUIDs. Facts forbid UPDATE/DELETE.

## 5. Redesign risks if ignored

Wide feature columns, Cartesian cubes, scores on bar rows, live scans of history, per-disaster tables.
