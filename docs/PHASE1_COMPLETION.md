# Phase 1 completion checklist

Date: 2026-09-02  
Gate: fixture lifecycle only. Exchange ingestion remains off.

- [x] Deterministic BTC 1h fixture with source + snapshot + canonicalization run
- [x] Point-in-time: `as_of_time` after bar close
- [x] RSI family defined; only periods 12–17 persisted
- [x] Parameter region `RSI(12-17)` with exact member sets
- [x] Two relationship definitions, no combination cube
- [x] HISTORICAL and OOS evidence rows (append-only)
- [x] Rank snapshots per stage
- [x] Current projections + operational applicability
- [x] ENTER / WAIT / SKIP decision from operational tables only
- [x] Counterfactual paths for ENTER, WAIT, SKIP
- [x] Incremental one-bar update without live-path history scan
- [x] Tests in `tests/test_phase1_lifecycle.py`
- [ ] Operator Docker/Timescale persist of the same fixture (optional, later)
- [ ] Human approval to start Phase 2 (on-demand feature campaigns beyond the fixture)

`INGESTION_ENABLED` stays false. This fixture is code, not a market feed.
