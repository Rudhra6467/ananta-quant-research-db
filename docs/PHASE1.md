# Phase 1 — fixture lifecycle proof

Status: implemented on branch `work`. Not full-history ingestion.

## What Phase 1 proves

A tiny deterministic BTC 1h fixture can walk the empirical-memory loop:

raw payload → canonical bar (PIT) → requested features only → parameter region → relationship definitions → HISTORICAL + OOS evidence → rank snapshots → current projections → ENTER/WAIT/SKIP → counterfactuals → one-bar incremental update

without:

- downloading exchange history
- materializing RSI(2)…RSI(50) on every bar
- storing a combination cube
- letting the live decision scan raw / observations / evidence

## Fixture

- Code: `fixture-btc-1h-v1`
- 48 synthetic 1h bars starting 2026-01-01 UTC
- Source: `synthetic_fixture`
- Canonicalization version: `canon-v1`
- `as_of_time` = bar close + 1h (bar is visible only after it closes)

## Parameter range vs explosion

RSI period domain is nameable as 2…50 (49 values).

The campaign **requests** only RSI(12)…RSI(17).

Those six exact parameter sets are members of region `RSI(12-17)`.

Feature observations exist only for requested sets. The rest of the family remains a definition, not a table.

## Combinations

Two relationship *definitions*:

- `R_RSI_REGION_OVERSOLD_4H` — median RSI(12–17) < 35 → 4-bar forward return
- `R_RSI14_OVERSOLD_4H` — RSI(14) < 35 → 4-bar forward return

They are claims with terms, not precomputed cells for every threshold × horizon.

## Evidence and ranking

Each relationship gets append-only evidence for HISTORICAL (bars 0–36) and OOS (bars 36–end).

Ranks are snapshots per stage. OOS does not overwrite the historical snapshot.

Current blended score is a projection: `0.4 * historical + 0.6 * oos`.

## Live path

`live_decide` may read only:

- current_market_state
- current_feature_value
- current_regime_state
- operational_applicability

Tests fail if that path touches raw events, feature history, or evidence.

## Incremental update

`incremental_bar` appends one extra closed bar.

Expected new rows: 1 canonical bar + 6 feature observations (the requested region only).

Current state is rebuilt from the new last bar. Historical evidence is not rewritten.

## What this is not

Not edge. Not a strategy enable. Not KEEP. Not 5 years of BTC.

The fixture returns are synthetic. Effects are for schema/process proof only.
