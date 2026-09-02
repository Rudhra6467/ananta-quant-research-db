# Implementation phases

Constitution roadmap (locked 2026-09-02) supersedes the earlier 0–7 sketch.

No phase starts full-market ingestion. A phase is complete only after design, tests, and the completion gate.

| Phase | Name | Status |
| --- | --- | --- |
| 0 | Architecture & constitution | done on `main` @ 24b6e72 |
| 1 | Empirical fixture proof | done on `main` @ 24b6e72 |
| 2 | Persistent market truth foundation | this branch — fixture persist only |
| 3 | Production market data truth & ingestion | not started |
| 4 | Feature observation engine | not started |
| 5–17 | State, regime, memory, hypothesis, prediction, scenario, ranking, veto, ops projection, campaigns | not started |

Phase 2 allowed: persist the 48-bar synthetic BTC 1h fixture into normalized tables.

Phase 2 Forbidden: exchange ingest, RSI(2..50) materialization, combination cubes, evidence/ranking/paper persistence, KEEP, live capital.

Completion: `tests/test_phase2_persistence.py` plus constitution alignment doc.

Phase 0 / 1 / 2 still forbid full-history ingestion.
