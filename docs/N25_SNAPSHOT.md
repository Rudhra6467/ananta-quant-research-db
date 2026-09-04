# N2.5 CRYPTO_LAB_10 snapshot

Charter `N1.CRYPTO_LAB_10/v1`. Snapshot `snap-cryptolab10-kraken-1h-v1`. N3 not authorized.

## Source limitation
Kraken `GET /0/public/OHLC` returns at most 720 completed 1h candles (~30d). `since=` does not retrieve 2021 history. Bars were not manufactured.

Public OHLCVT ZIP (Kraken support 360047124832) is the realistic deep-history path and was not loaded here. Public `/Trades` can start at 2021-09-01 but tick reconstruction of 5y×10 is out of this pass.

## Completed in this pass
Restartable backfill runner. Per-instrument quality + gap classes. Named snapshot persist + `snapshot_bars_as_of`. PIT revision test. Idempotent re-persist.
REST reachable tape: 720×10 = 7200 bars, 2026-08-05→2026-09-04, 0 quarantines.

## Completeness
Each instrument: 720 acquired vs ~43800 expected. `snapshot_status.complete=0`.
Leading missing hours = charter start → 2026-08-05 (provider depth).

N3 remains off.
