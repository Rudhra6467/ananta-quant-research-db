# Implementation phases

Constitution roadmap (locked 2026-09-02) supersedes the earlier 0–7 sketch.

No phase starts full-market ingestion. A phase is complete only after design, tests, and the completion gate.

| Phase | Name | Status |
| --- | --- | --- |
| 0 | Architecture & constitution | done on `main` @ 24b6e72 |
| 1 | Empirical fixture proof | done on `main` @ 24b6e72 |
| 2 | Persistent market truth foundation | done on `work` — fixture persist only |
| 3 | Fixture evidence persistence | this branch — no exchange ingest |
| 4 | Feature observation engine | not started |
| 5–17 | State, regime, memory, hypothesis, prediction, scenario, ranking, veto, ops projection, campaigns | not started |

Phase 3 allowed: persist fixture experiment runs, trials, and append-only evidence.

Phase 3 forbidden: exchange ingest, ranking engine, paper, predictions, KEEP, live capital.

Completion: `tests/test_phase3_evidence.py`.
