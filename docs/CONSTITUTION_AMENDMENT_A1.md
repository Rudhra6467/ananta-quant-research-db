# Constitution Amendment A1 — 2026-09-04

Explicit rewrite to allow progress without unpublished ZIPs.
Does not delete PIT, append-only raw, requested-only features, live-path bounds, or zero capital.

1. Preferred source remains official Kraken OHLCVT ZIPs when they exist.
2. Second official Kraken grain permitted: public Trades aggregated to 1h as `kraken.trades.agg.1h`. Never labeled `kraken.ohlcvt.*`.
3. Foreign venue = parallel world only. Never merged into Kraken identity.
4. Mapping must be explicit (pair → instrument → hour → fields → checksum).
5. When the ZIP later arrives, append it. Do not overwrite trade-agg rows.
6. `complete_archive=1` only on official OHLCVT coverage. `complete_usable` only after named audit. N3 still needs its own grant.
7. Q3 2026 is not a closed archive before 2026-09-30.
8. REST OHLC is not Q2 archive coverage (720-candle cap).
