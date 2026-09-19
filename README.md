# ananta-quant-research-db

Empirical memory for Ananta.

This repository is **not** a backtester that stores answers. It preserves structured evidence so Ananta can discover, challenge, validate, remember, explain, and update beliefs.

Ananta (trading system) remains System Truth and execution.
This database is research memory.
Agent Ananta reads structured facts; it does not scrape UI and it does not write Mongo.

## Architecture law

```
raw source
  → canonical market facts          (append-only)
  → feature / regime / state facts  (append-only, point-in-time)
  → experiments / trials / evidence (append-only)
  → stage scores / ranks / cohorts  (append-only snapshots)
  → curated current summaries       (rebuildable projections)
  → operational cache               (tiny, versioned, 5-minute path)
  → Ananta decision / paper / live  (separate system)
```

Current score is a **projection**. Historical evidence is never overwritten.

Live 5-minute evaluation may query only operational projections. It must not scan raw candles, feature history, or experiment archives.

## Current status

Phase 0–1: merged to `main` (`24b6e72`).  
Phase 2–4: merged to `main`. Phase 5: current state/regime compiler on `work` (fixture only). Constitution: `docs/DATABASE_CONSTITUTION.md`, `docs/ARCHITECTURE_LOCK_V2.md`.

Allowed now: schemas, deterministic fixture, requested RSI(12–17) observations, fixture evidence, operational projections.

Forbidden: full historical ingestion, combination cubes, KEEP, live capital, exchange ingest.

```bash
python -m pytest
```
