# Phase 5 — Current market state, regime, bounded ops projection

Status: implemented on `work`. Fixture only.

Compiler path:

market truth (last fixture bar)
→ requested feature observations RSI(12–17)
→ current market state
→ current regime (`rsi_region`)
→ upsert `ops.current_*`

Historical state/regime rows live in schema `state` (append-only facts).
Live path still reads only `ops.current_*`.

Regime is a system representation (hypothesis), not market truth and not a prediction.

Forbidden: exchange ingest, ranking, prediction, scenarios, paper, 10-asset campaign, lineage graph, grouping engine.
