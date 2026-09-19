# Gate B — Real crypto laboratory (design only)

Status: **DESIGN ONLY.** Blocked until Gate A is accepted in writing and Gate B is separately authorized.  
No backfill job ships with this file.

## Goal

Populate `CRYPTO_LAB_10` through the existing raw → canonical path and run the already-built pipeline on real 1h Kraken spot history.

## Must prove

- 10 instruments persist with compound identity.
- ~5-year window (`2021-09-01Z` → last complete hour) survives PIT filters.
- Incremental watermark does not rescan the full window.
- Fixture tests still pass.
- `ops.universe_plan.ingested` flips to true **only after** a successful named snapshot, not before the first bar.
- Live path still cannot read `raw.*` / `market.*`.

## Must not do

- CRYPTO_FULL
- Perps / books / sub-hour
- Feature cube
- Agent runtime
- Venue paper
- Constitution edits
