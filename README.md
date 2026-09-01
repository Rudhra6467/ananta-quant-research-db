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

## Phase 0 status

Phase 0 is the foundation gate.

Allowed now:

- schemas, identities, lineage, definition stubs
- append-only evidence stubs
- current-state projection stubs
- architecture document and completion tests

Forbidden until a later phase is explicitly approved:

- full historical ingestion
- combinatorial feature materialization
- strategy enablement / KEEP
- live capital
- treating Ananta regime labels as ground truth

See `docs/EMPIRICAL_MEMORY_ARCHITECTURE_V1.md` and `docs/PHASES.md`.

## Layout

```
docs/            architecture and phase gates
research_db/     SQLAlchemy models and config
alembic/         migrations
sql/             readable Phase 0 DDL (same grain as migration)
tests/           static contract tests (no live DB required)
```

## Local bring-up (after Phase 0 approval to run Docker)

```bash
docker compose up -d
python -m pip install -e ".[dev]"
alembic upgrade head
python -m pytest
```

Do not ingest a multi-year dataset in Phase 0.

## Relationship to other repos

| Repo | Role |
| --- | --- |
| `Rudhra6467/Ananta` | Trading system, execution, System Truth |
| `Rudhra6467/ananta-decision-agent` | Interpretation, ranking, marks, proposals |
| `Rudhra6467/ananta-quant-research-db` | Empirical memory and evidence substrate |
