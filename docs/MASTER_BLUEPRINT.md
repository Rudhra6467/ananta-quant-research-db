# Ananta Database — Master Blueprint

Status: Canonical governing brief. Updated 2026-09-04 after fixture freeze.  
Layers: Constitution (invariants) | Fixture roadmap (complete) | Activation program (next).  
A future item is not permission to implement it.  
Fixture representation ≠ scientific validation on real data.

## Purpose

Time-aware, provenance-preserving, evidence-oriented market memory — not a price warehouse.

Loop: Observe → Validate → Preserve → Derive → Measure → Detect State → Detect Change → Compare → Test → Learn → Expose Evidence → Agent Reasoning → Outcome → New Evidence.

Laboratory first: ~5 years, ~10 crypto assets. Database ≠ Agent.

## Invariants

- Identity ≠ market fact ≠ observation ≠ measurement ≠ evidence ≠ hypothesis ≠ prediction ≠ rank ≠ projection.
- event/effective time ≠ knowledge time. No lookahead.
- Append-only evidence. Reset = new run, not DELETE.
- Live path reads only `ops.current_*`.
- Requested materialization only. No Cartesian cubes.
- Observation → association → hypothesis → test → OOS. Correlation ≠ causation.
- Compound identity. Lineage graph reserved.
- `INGESTION_ENABLED=false` until an ingest *activation gate* is approved in writing.

## Fixture checkpoint

Commit `0871b49` completes Phases 0–20 **on the 48-bar fixture**.  
See `docs/CHECKPOINT_P0_P20.md` and `docs/DATABASE_CONSTITUTION.md`.

Do not invent Phase 21+.

## Destination vs laboratory

| Layer | What the fixture proved | What real data must prove |
| --- | --- | --- |
| Architecture | Tables, PIT, append-only, live-path denial | Data integrity at scale |
| Features / measures | Requested-only compute | Statistical usefulness |
| Groups / events | Identity + windows + as-of | Membership and shifts in the world |
| Agent / paper | Catalog + ledger + zero capital | Decision quality |
| Universe / markets | Plan rows exist | Ingested / created systems |

## Reliability order

Correctness → PIT → reproducibility → scientific validity → scale.

Postgres 16 + Timescale in production; SQLite twin in CI.

## Roadmap (repo reality)

| Phase | Intent | Status |
| --- | --- | --- |
| 0–7 | Foundation through requested measurements | COMPLETE / FROZEN |
| 8 | Group identity + temporal membership | fixture implemented |
| 9 | Requested RET(1) / RANGE_VOL(1) | fixture implemented |
| 10 | Versioned regime definitions | fixture implemented |
| 11 | Event identity + windows | fixture annotation only |
| 12 | Declared cross-subject links | fixture implemented |
| 13 | Analogue pairs, no scores | fixture implemented |
| 14 | Memory tiers, raw retained | fixture implemented |
| 15 | Access / mutation policy | fixture implemented |
| 16 | Read-only query catalog | fixture implemented |
| 17 | Consult log, no mutation | fixture implemented |
| 18 | Paper ledger, capital=0 | fixture implemented |
| 19 | CRYPTO_LAB_10 / FULL plans | not ingested |
| 20 | US / CA / IN plans | not created |

## Activation program (current command)

Documents: `docs/ACTIVATION_PROGRAM.md`, `docs/GATE_A_INGESTION_DESIGN.md`, `docs/GATE_B_LABORATORY_DESIGN.md`, `docs/GATE_C_SHIFT_DESIGN.md`, `docs/GATE_D_AGENT_DESIGN.md`, `docs/GATE_E_PAPER_DESIGN.md`, `docs/GATE_F_SCALEOUT_DESIGN.md`.

| Gate | Intent | Status |
| --- | --- | --- |
| A | Ingestion design for CRYPTO_LAB_10 | DESIGN published — not implementation-approved |
| B | Populate laboratory on real Kraken spot 1h | DESIGN only — blocked on A acceptance |
| C | Exercise events; detection research later | DESIGN only — blocked on B tape |
| D | Agent Ananta read-only via catalog | DESIGN only — blocked on B–C |
| E | Paper profiles, zero capital | DESIGN only — blocked on D |
| F | CRYPTO_FULL then US/CA/IN DBs | DESIGN only — blocked on paper evidence |

## Current command

Do not add fixture phases.  
Do not connect an exchange.  
Do not flip `INGESTION_ENABLED`.  
If an activation step conflicts with the constitution: stop and report. Do not rewrite the constitution.

Next *implementation* requires written acceptance of Gate A, then a separate Gate B authorization.
