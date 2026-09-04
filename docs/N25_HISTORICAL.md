# N2.5-HISTORICAL — Kraken OHLCVT archive

Charter `N1.CRYPTO_LAB_10/v1`. Snapshot `snap-cryptolab10-kraken-1h-v1`. N3 not started.

## Archive
Public Drive `1ptNqWYidLkhb2VAKuLCxmp2OXEfGO-AP` / `Kraken_OHLCVT.zip` (7,885,068,519 bytes). No credentials. Range-extracted `master_q4/*USD_60.csv` for the ten instruments.

## Event-time coverage in charter window
Charter 2021-09-01Z → 2026-09-04T16:00Z ≈ 43,913 hours.
Archive in-window ~37,970/instrument (AVAX 35,285 from listing 2021-12-21). Archive ends **2025-12-31T23:00Z** for all ten.

## Official limitation
REST resumes 2026-08-05T17:00Z. **Gap 2026-01-01 → 2026-08-05 (~5,201 hours)** is missing provider/archive data. Not filled. Not substituted. Snapshot is not charter-complete.

AVAX pre-2021-12-21 = listing gap. Intra-archive holes recorded (BTC 22, BCH 116, XRP 74).

## Provenance
source `kraken.ohlcvt.master_q4`; id `ohlcvt:{wire}:60:{unix}`; knowledge_time `2026-01-01T00:05:00Z`. Idempotent replay.

N3 not authorized.
