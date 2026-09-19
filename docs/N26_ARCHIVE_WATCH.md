# N2.6 — Deferred Archive Completion Watch

Not continuous market ingestion. Not N3.
Frozen snapshot `snap-cryptolab10-kraken-1h-v1` remains **audited incomplete**.

## Missing interval
`2026-04-01T00:00:00Z` → `2026-08-05T16:00:00Z`

## Expected official sources
Folder: https://drive.google.com/drive/folders/15RSlNuW_h0kVM8or8McOGOMfHeBFvFGI

| File | Status at freeze |
| --- | --- |
| Kraken_OHLCVT_Q2_2026.zip | unpublished |
| Kraken_OHLCVT_Q3_2026.zip | unpublished |

## Watch rules
1. Record the gap. Do not invent bars.
2. Probe the official folder only when asked.
3. `auto_ingest = false`. A new zip is not permission to load it.
4. Loading requires explicit written authorization.
5. After an authorized load, rerun the full snapshot audit.
6. `complete` stays 0 until 2021-09-01Z → last complete hour passes.
7. N3 stays blocked while complete=0.
