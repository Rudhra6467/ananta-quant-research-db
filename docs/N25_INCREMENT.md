# N2.5-INCREMENT — official Q1 2026 OHLCVT

Charter `N1.CRYPTO_LAB_10/v1`. Snapshot `snap-cryptolab10-kraken-1h-v1`. `complete=0`. N3 not started.

## Official increment found
Public folder: `https://drive.google.com/drive/folders/15RSlNuW_h0kVM8or8McOGOMfHeBFvFGI`
File: `Kraken_OHLCVT_Q1_2026.zip` (id `15QxEf_-rRS-Yt7uERCI41HMcQQPKzSHq`, 545,431,093 bytes, listed 26 Apr 2026).
No credentials. Range-extracted the ten `*USD_60.csv` members.

## Q1 2026 load (all ten instruments)
Each file: **2,160** hourly bars, `2026-01-01T00:00Z` → `2026-03-31T23:00Z`, intra-quarter holes **0**.
Expected Q1 hours = 90 × 24 = 2,160. Complete quarter.

Source: `kraken.ohlcvt.q1_2026`. Record id `ohlcvt:{wire}:60:{unix}` (same scheme; no overwrite of master_q4/REST ids).

## Official files NOT present in that folder (2026-09-04)
- `Kraken_OHLCVT_Q2_2026.zip` — absent
- `Kraken_OHLCVT_Q3_2026.zip` — absent (quarter still in progress)

Kraken publishes increments at quarter end. Q2 2026 ended 2026-06-30; it is still unpublished in the official folder.

## Remaining gap (do not fill)
**2026-04-01T00:00Z → 2026-08-05T16:00Z** (~2,944 hours)

REST still covers only 2026-08-05T17:00Z → last complete hour.

## Charter completeness question
Can the ten-instrument snapshot cover 2021-09-01T00:00Z → last complete hour without invented bars?

**NO.** `snapshot_status.complete` stays **0**.

Covered with official provenance:
- master_q4 archive: 2021-09-01 → 2025-12-31 (listing/intra holes already audited)
- Q1 2026 increment: 2026-01-01 → 2026-03-31
- REST: ~2026-08-05 → 2026-09-04

Uncovered: 2026-04-01 → 2026-08-05 16:00Z.

N3 not authorized.
