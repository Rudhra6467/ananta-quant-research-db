# N2 real-tape ingestion — ready for review

Freeze `0871b49`. Charter `N1.CRYPTO_LAB_10/v1`. N3 not authorized.

## Proof run (page-1, not the 5-year window)
Run `run-n2-kraken-ohlc-charter-v1.page1-proof`
Snapshot `snap-cryptolab10-kraken-1h-v1`
7200 acquired, 7200 accepted, 0 quarantined, 0 duplicates, 0 mapping failures, 0 revisions.
Event window 2026-08-05T17:00Z → 2026-09-04T16:00Z (720 bars × 10 instruments).
Knowledge time 2026-09-04T17:19:43Z.
Gaps intra-page: 0. Completeness vs 2021-09-01 charter window: incomplete.

## PIT
Same event_time, two record ids, later knowledge_time. Earlier as_of sees only first close.

## Idempotency
Same (source, source_record_id) duplicates, does not double-accept.

## Global flag
INGESTION_ENABLED remains false. Bare live provider denied.

N2 real-tape ingestion ready for review/acceptance.
