# Implementation phases

Constitution **locked 2026-09-03** (see `DATABASE_CONSTITUTION.md`, `ARCHITECTURE_LOCK_V2.md`).
Roadmap homes after Phase 5: `docs/ROADMAP_RECONCILIATION.md`.
Master brief: `docs/MASTER_BLUEPRINT.md`.

No phase starts full-market ingestion. A phase is complete only after design, tests, and the completion gate.

| Phase | Name | Status |
| --- | --- | --- |
| 0 | Architecture & constitution | done on `main` |
| 1 | Empirical fixture proof | done on `main` |
| 2 | Persistent market truth foundation | merged to `main` |
| 3 | Fixture evidence persistence | merged to `main` |
| 4 | Feature observation engine | merged to `main` |
| — | Architecture lock v2 | done on `main` |
| 5 | Current state / regime / bounded ops projection | accepted on `work` |
| 6 | Empirical memory + hypothesis lifecycle | COMPLETE on `work` |
| 7 | Quantitative empirical measurements | COMPLETE and frozen on `work` |
| 8 | Grouping identity + temporal membership | implemented on `work` — fixture only |
| 9 | Advanced analytical / feature layer | implemented on `work` — fixture only |
| 10 | Versioned regime definitions | implemented on `work` — fixture only |
| 11 | Event representation (onset/windows/PIT) | implemented on `work` — fixture annotation only |
| 12 | Declared cross-subject links | implemented on `work` — no correlation engine |
| 13 | Event analogue definition links | implemented on `work` — no similarity scores |
| 14 | Memory tiers + summaries, raw retained | implemented on `work` |
| 15 | Access/mutation policy | implemented on `work` |
| 16 | Read-only query catalog | implemented on `work` — no agent runtime |
| 17 | Catalog-only agent consult log | implemented on `work` — no mutation |
| 18 | Paper profile ledger, zero capital | implemented on `work` |
| 19 | Universe plan registry | implemented on `work` — not ingested |
| 20 | Market DB plan registry | implemented on `work` — not created |

Phase 5 Forbidden remains: exchange ingest, ranking, predictions, scenarios, paper, 10-asset campaign, grouping engine beyond identity/membership, ML discovery.

Phase 0–20 still forbid full-history ingestion.
