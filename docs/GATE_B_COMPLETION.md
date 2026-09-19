# Gate B completion

Architecture freeze: `0871b49`. Fixture/replay only. Not Gate C.

## A. Objects added
- `research.lab_experiment_definition` (code + version)
- `research.lab_cohort`
- `research.lab_input_link`
- `research.lab_result` (append-only)
- Reuses P3 `research.experiment_run` for run identity (`code`, `config_hash`=input_digest)
- `research_db/lab/engine.py` Laboratory
- `open_laboratory_store()`

## B. Experiment lifecycle
define (versioned) → cohort → start_run(as_of) → attach inputs (PIT-checked) → complete(status) → optional rerun (new run_code, same input_digest).
Statuses: supported | contradicted | inconclusive | invalidated | insufficient.
Results are not market truth.

## C. Information-set / PIT
Each run has `as_of` knowledge time. `attach()` raises if `knowledge_time > as_of`.

## D. Provenance / reproducibility
`input_digest` hashes experiment, version, cohort, snapshot, as_of, and attached refs.
Two identical executions get different `run_code` and the same digest. Snapshot is `fixture-btc-1h-v1`.
Reset = new run/cohort, never DELETE.

## E. Fixture demonstration
`EXP_RSI14_FWD_RET@v1` / `COHORT_BTC_1H_A` linked to `H_RSI14_OVERSOLD_4H` and `effect_size.mean_forward_return.v1`.
Result: **inconclusive** (n too small). Not a live-tape claim.

## F. Tests
`tests/test_gate_b_laboratory.py` plus prior suite.

## G. Blocked
Live ingest, connectors, backfill, shift detectors, Agent runtime, paper execution, capital, US/CA/IN DBs, ranking engines, P7 replacement.

## H. Gate C readiness
P11 event representation + this lab exist. Production shift conclusions still need real tape and a separate Gate C authorization.

Gate B ready for review/acceptance.
