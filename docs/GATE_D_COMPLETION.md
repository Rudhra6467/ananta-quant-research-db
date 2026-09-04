# Gate D completion

Architecture freeze: `0871b49`. Read-only catalog. Not Gate E. Not runtime.

## Objects / interfaces added
- `research_db/agent/catalog.py` capability catalog v1
- `research_db/agent/context.py` PIT AgentContext
- `interface.agent_capability`, `interface.agent_context`, `interface.agent_context_item`
- `open_agent_catalog_store()`

## Reused
P16 QueryCatalog, P17 AgentConsult, Gate B/C surfaces, fixture snapshot.

## Capability catalog
Available: current_regime, current_market_state, members_as_of, events_as_of, measurement_current, hypothesis_current_status, lab_result_as_of, shift_candidate_as_of, snapshot_identity.
Reserved: prediction_distribution, risk_budget, paper_decision_read, outcome_attribution.
Blocked: raw_market_scan, mutate_*, live_order, enable_ingestion, ranking_engine, allocate_capital.

## Read-only / PIT
No writes. decide/mutate denied. observe requires knowledge_time ≤ as_of.

## Uncertainty
UNKNOWN, INSUFFICIENT_EVIDENCE, HIGH_UNCERTAINTY, OUT_OF_DISTRIBUTION, MODEL_DISAGREEMENT.
Fixture uses INSUFFICIENT_EVIDENCE.

## Fixture demo
Bar-10 context accepts snapshot + state. E_SHIFT_T24 later knowledge_time is rejected.

## Blocked
Runtime, ingest, orders, capital, ranking, US/CA/IN, Phase 21.

## Gate E readiness
P18 paper ledger exists (capital=0). Gate E not started.

Gate D ready for review/acceptance.
