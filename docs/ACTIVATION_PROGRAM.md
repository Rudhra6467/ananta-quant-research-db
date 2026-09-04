# Activation program (design only)

Status: **not started**. Ingestion stays disabled until Gate A is approved.

The numbered roadmap is complete. Do not add Phase 21+.

Fixture representation ≠ scientific validation.

## Gates

### Gate A — Ingestion design (approval required before any vendor connection)

Define, do not implement:

- CRYPTO_LAB_10 universe (assets, venues, timeframes, 5-year window).
- Source/vendor contracts, raw manifests, checksums, replay IDs.
- Validation and reject/quarantine rules.
- Provenance: source → raw → canonical → snapshot → run.
- Backfill vs incremental watermarks.
- Failure handling and idempotent replay.
- Point-in-time / knowledge-time rules for late or revised bars.
- Cost and rate-limit policy.

Keep `INGESTION_ENABLED=false` until this design is accepted in writing.

### Gate B — Real crypto laboratory

Only after Gate A:

- Populate `CRYPTO_LAB_10` (`ops.universe_plan` currently `ingested=false`).
- Run the existing pipeline on real history.
- Prove the fixture architecture survives data quality and scale.
- Do not expand to full crypto.

### Gate C — Shift / event research

Only after Gate B has a usable tape:

- Exercise Phase 11 representation on real events.
- Then, and only then, consider detection research.
- Test onset, peak, pre/post windows, relative thresholds, analogues, false positives, OOS.
- No hardcoded percentage threshold.
- Detection is a research engine, not a rewrite of event identity.

### Gate D — Agent runtime

Only after Gates B–C produce trustworthy current state:

- Agent Ananta may call Phase 16 catalog queries only.
- Phase 17 consult log remains the audit surface.
- Read-only first.
- Responses must carry provenance and knowledge_time.
- Agent cannot write `research.*` or `market.*`.

### Gate E — Paper trading

Only after Gate D:

- Activate SAFE / AVERAGE / AGGRESSIVE ledgers.
- Zero real capital.
- SAFE still cannot TAKE without a later explicit relaxation.
- No venue connectivity until a separate venue-adapter approval.

### Gate F — Scale-out

Only after paper evidence, not after enthusiasm:

- Full crypto universe (`CRYPTO_FULL` currently `ingested=false`).
- After that, separate US / CA / IN systems (`ops.market_database_plan.created=false`).

## Conflict rule

If a gate requires changing constitutional meaning of truth, PIT, append-only evidence, live-path bounds, or requested-only materialization: **stop and report**. Do not patch the constitution.
