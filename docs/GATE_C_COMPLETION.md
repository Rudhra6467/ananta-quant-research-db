# Gate C completion

Architecture freeze: `0871b49`. Fixture/replay only. Not Gate D.

## Objects added or reused
Added: `research.shift_detector_definition`, `research.shift_detection_run`, `research.shift_candidate`, `research.shift_review_event`.
Reused: P11 EventMemory (`E_BREAK_T20`, `E_SHIFT_T24`); Gate B Laboratory.

## Detector specification / version
`DET_ANNOTATED_SHIFT@v1` — method `annotated_replay`. Not CUSUM. Not production.

## PIT / information set
Scan includes only events with `knowledge_time <= run.as_of`. Early as_of sees zero later annotations.

## Event and provenance
Candidate stores event_code, clocks, run, snapshot, detector version, params, windows, input_digest.

## False-positive / inconclusive
Review statuses: detected | false_positive | inconclusive | invalidated. `certainty=false`, `live_claim=false`.

## Reproducibility
Rerun = new run_code, same input_digest.

## Fixture demonstration
On `fixture-btc-1h-v1`, detector surfaces annotated events at bar-24 as_of. Lab `EXP_SHIFT_ANNOTATION` is **inconclusive** — detection is not confirmation.

## Tests
`tests/test_gate_c_shift.py` plus prior suite.

## Blocked
Live ingest, connectors, production detectors, Agent runtime, paper/orders/capital, US/CA/IN, ranking, Phase 21.

## Gate D dependencies
P16 catalog and P17 consult exist. Real-tape current state does not. Gate D runtime is not started.

Gate C ready for review/acceptance.
