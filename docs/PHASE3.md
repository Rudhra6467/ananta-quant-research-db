# Phase 3 — Fixture evidence persistence

Status: implemented on `work`. Not production ingest. Not ranking.

Persist Phase 1 experiment runs, trials, and relationship evidence for the 48-bar synthetic BTC 1h fixture.

Allowed: append-only evidence, validation stages, reset-as-new-cohort, incremental FORWARD row, PIT by knowledge_time, rebuildable current summaries.

Forbidden: exchange connections, INGESTION_ENABLED=true, ranking engine, paper trading, prediction tables, 10-asset campaign, Cartesian cubes, deleting failed experiments.
