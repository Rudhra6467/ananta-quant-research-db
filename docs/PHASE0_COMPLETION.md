# Phase 0 completion checklist

Date: 2026-09-01  
Gate: foundation only. Ingestion remains off.

- [x] Architecture v1 written with three-layer split and approval gate
- [x] README states this is evidence memory, not an answer store
- [x] Schemas declared: `ref`, `raw`, `core`, `research`, `analytics`, `ops`
- [x] Identity / lineage tables exist as models + DDL
- [x] Versioned research definition stubs exist
- [x] Append-only evidence / decision / rank snapshot stubs exist
- [x] Rebuildable current-state and applicability stubs exist
- [x] `INGESTION_ENABLED` defaults false
- [x] Static tests cover architecture headings and model contract
- [ ] Live Timescale upgrade in a Docker-capable environment (operator)
- [ ] Human approval to start Phase 1 fixture ingest

Operator: do not load exchange history until Phase 1 is explicitly approved.
