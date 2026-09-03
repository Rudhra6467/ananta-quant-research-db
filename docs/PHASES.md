# Implementation phases

Constitution roadmap (locked 2026-09-02) supersedes the earlier 0–7 sketch.

No phase starts full-market ingestion. A phase is complete only after design, tests, and the completion gate.

| Phase | Name | Status |
| --- | --- | --- |
| 0 | Architecture & constitution | done on `main` @ 24b6e72 |
| 1 | Empirical fixture proof | done on `main` @ 24b6e72 |
| 2 | Persistent market truth foundation | done on `work` — fixture persist only |
| 3 | Fixture evidence persistence | done on `work` — no exchange ingest |
| 4 | Feature observation engine | this branch — requested RSI(12–17) only |
| 5–17 | State, regime, memory, hypothesis, prediction, scenario, ranking, veto, ops projection, campaigns | not started |

Phase 4 allowed: request catalog, rolling RSI state, requested observations.

Phase 4 Forbidden: exchange ingest, RSI(2..50) cube, ranking engine, paper, predictions, KEEP, live capital.

Phase 0 / 1 / 2 / 3 / 4 still forbid full-history ingestion.

Completion: `tests/test_phase4_observation.py`.
