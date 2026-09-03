# Architecture lock audit (2026-09-02)

This is an audit, not a build phase. Phase 2 remains fixture-only.

Locked laws:

- A prediction is an empirical claim, not a trusted fact.
- Prediction value ≠ prediction reliability ≠ knowledge ranking.
- Ananta may return UNKNOWN, INSUFFICIENT_EVIDENCE, HIGH_UNCERTAINTY, OUT_OF_DISTRIBUTION, MODEL_DISAGREEMENT.
- Reset means a new experiment cohort / snapshot. It never deletes historical truth or failed experiments.

## Verdict

The foundation can support the 15 future capabilities without a rewrite if we keep facts append-only, identities stable, and later domains as new tables in reserved schemas.

Two contracts would have forced a redesign. They are corrected in this change and nothing else is implemented.

1. `ref.asset.symbol` is no longer globally unique. Identity is `(asset_class, symbol)` so crypto BTC and an equity ticker BTC can coexist.
2. `research.relationship_evidence.direction` now allows `untested|supports|contradicts|inconclusive|invalidated|decayed`.
3. Empty schemas `prediction` and `portfolio` are reserved beside existing `world`.

`market.ohlcv_bar` is one market-fact family. It is not the only allowed market truth.

`research.decision_event` is a TAKE/WAIT/SKIP ledger. It is not the prediction store.

`research.ranking_snapshot.score` is one scoring-model scalar at one as_of. It is not reliability and not the prediction value.

## How each capability attaches later

See the table in-repo. Capabilities 1–15 attach as new tables/rows using existing identities, two clocks, and append-only facts.

## What this change does not do

No prediction tables. No world event rows. No ranking implementation. No paper. No exchange ingest. No 10-asset campaign.
