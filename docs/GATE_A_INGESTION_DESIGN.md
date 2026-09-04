# Gate A — Ingestion design

Status: **DESIGN ONLY.** Not accepted for implementation until written approval.  
`INGESTION_ENABLED` remains **false**. No vendor session, no HTTP to an exchange, no backfill job.

Parent: `docs/ACTIVATION_PROGRAM.md`  
Checkpoint: `0871b49` (Phase 0–20 fixture architecture)  
Constitution conflict rule: if this design requires changing PIT, append-only raw facts, live-path bounds, or requested-only materialization — stop and report. Do not rewrite the constitution.

This document does **not** activate Gate B.

---

## 1. Purpose

Define how CRYPTO_LAB_10 would enter Ananta if Gate B is later approved:

raw source → append-only raw fact → canonical OHLCV → existing fixture pipeline.

The fixture already proved that pipeline on 48 synthetic BTC 1H bars. Gate A specifies the real-data contract those tables would have to satisfy.

---

## 2. Universe plan (not ingested)

Code: `CRYPTO_LAB_10` (`ops.universe_plan.ingested = false`)

| # | Asset | Instrument code (planned) | Venue (planned) | Market | Timeframe |
| --- | --- | --- | --- | --- | --- |
| 1 | Bitcoin | BTC-USD-SPOT | KRAKEN | spot | 1h |
| 2 | Ether | ETH-USD-SPOT | KRAKEN | spot | 1h |
| 3 | Solana | SOL-USD-SPOT | KRAKEN | spot | 1h |
| 4 | XRP | XRP-USD-SPOT | KRAKEN | spot | 1h |
| 5 | Cardano | ADA-USD-SPOT | KRAKEN | spot | 1h |
| 6 | Avalanche | AVAX-USD-SPOT | KRAKEN | spot | 1h |
| 7 | Chainlink | LINK-USD-SPOT | KRAKEN | spot | 1h |
| 8 | Dogecoin | DOGE-USD-SPOT | KRAKEN | spot | 1h |
| 9 | Litecoin | LTC-USD-SPOT | KRAKEN | spot | 1h |
| 10 | Bitcoin Cash | BCH-USD-SPOT | KRAKEN | spot | 1h |

Window (planned): laboratory window is **5 years back from activation date**, specified as:

- `event_time` from `2021-09-01T00:00:00Z` inclusive
- through the last complete 1h bar known at run `knowledge_time`

Why Kraken spot 1h: matches Agent Ananta lab-watch / outcome-truth practice (spot, not perpetual). Perps, funding, books, trades are **out of Gate B**. They remain additional market-truth families in the constitution.

BNB is omitted because Kraken spot USD coverage is uneven; BCH is the tenth liquid Kraken-spot substitute. Changing the tenth name is a universe-plan edit, not a schema redesign.

Out of scope for this laboratory:

- US/CA/IN cash equities
- `CRYPTO_FULL`
- sub-hour bars
- options

---

## 3. Identity mapping

Reuse existing `ref.*` grains. Do not invent a second instrument table.

| Concept | Table | Gate A rule |
| --- | --- | --- |
| Asset | `ref.asset` | code = BTC, ETH, … |
| Instrument | `ref.instrument` | `{ASSET}-USD-SPOT` |
| Venue | `ref.venue` | `KRAKEN` |
| Timeframe | `ref.timeframe` | `1h` |
| Data source | `ref.data_source` | `kraken.ohlc.spot` (logical name; no connection now) |
| Snapshot | `ops.dataset_snapshot` | one snapshot per freeze of the lab window |
| Run | `ops.ingestion_run` | one run per attempt; failed runs stay |
| Raw | `raw.market_event` | append-only; checksummed payload |
| Canonical | `market.ohlcv_bar` | one row per instrument/venue/timeframe/event_time/version |

Compound identity stays `asset + quote + market + venue + timeframe`. BTC-USD-SPOT on Kraken is not the same instrument as BTC-USDT-PERP elsewhere.

---

## 4. Source contract (logical)

Vendor: Kraken public OHLC (spot).  
Protocol: HTTPS REST.  
Auth: none for public OHLC.  
Rate limit: design assumes ≤1 request / 2s per process and a single worker.  
Clock: exchange bar close time is `event_time`. Fetch time is **not** `event_time`.

Logical request grain:

- pair (Kraken wire name, e.g. XBTUSD)
- interval = 60
- since = watermark (unix) or window start

Wire name ≠ instrument code. Mapping lives in a **source symbol map** (design object, not implemented):

```text
XBTUSD -> BTC-USD-SPOT
ETHUSD -> ETH-USD-SPOT
...
```

Payload stored in `raw.market_event.payload` is the vendor JSON for that bar, not the canonical OHLCV struct.

`source_record_id` = `{source}:{pair}:{interval}:{event_time}`  
`checksum` = SHA-256 of canonicalized JSON (sorted keys, no whitespace variance).

Duplicate `(data_source_id, source_record_id)` is rejected by existing unique constraint. A **revision** is a new raw row with a new `source_record_id` suffix `:revN` and later `knowledge_time`. Canonicalization then writes a new `market.ohlcv_bar` row with a new `canonicalization_version` if OHLC actually changed. Prior canonical rows stay. PIT reads use `knowledge_time <= T`.

---

## 5. Validation before canonicalization

A raw row may be stored and still fail promotion. Failed promotion is negative knowledge, not a delete.

Reject / quarantine if any:

- missing O/H/L/C
- H < max(O,C) or L > min(O,C)
- H < L
- volume < 0
- event_time not aligned to 1h UTC close
- event_time outside the approved lab window
- pair not in CRYPTO_LAB_10 map
- checksum mismatch on replay
- knowledge_time < event_time

Quarantine is a run status + notes on `ops.ingestion_run`, plus the raw row remaining in place. Do not invent a “fix in place” update.

---

## 6. Provenance chain (already contracted)

```text
ref.data_source
  -> raw.market_event (source_record_id, checksum, payload, event_time, knowledge_time)
    -> ops.ingestion_run
      -> ops.dataset_snapshot
        -> ops.canonicalization_run
          -> market.ohlcv_bar (raw_event_id, canonicalization_version)
```

Gate B must fill these FKs. Gate A forbids a connector that writes `market.ohlcv_bar` without a raw parent.

---

## 7. Backfill vs incremental

| Mode | When | Rule |
| --- | --- | --- |
| Backfill | first approved Gate B run | walk the 5-year window per instrument, oldest → newest, snapshot code `LAB10_BACKFILL_v1` |
| Incremental | later | watermark = max(event_time) per instrument already canonicalized; fetch only newer complete bars |
| Replay | checksum or vendor disagreement | new ingestion_run; never UPDATE raw |

Incremental must not rescan the full 5-year set. That is the same incrementality law the fixture already tests.

A bar is “complete” only after its `event_time` (hour close). Partial hours are not stored as canonical facts.

---

## 8. Point-in-time / late data

- `event_time` = bar close (market clock).
- `knowledge_time` = when Ananta could have known the payload (ingest receive time, or vendor revision time if later).
- Queries that reconstruct “what was knowable at T” filter `knowledge_time <= T`.
- Vendor revisions do not overwrite history.
- Live path still cannot read `raw.*` or `market.*`; it stays on `ops.current_*` after compile.

No conflict with the constitution: this is the existing two-clock model applied to vendor data.

---

## 9. Failure handling

| Failure | Action |
| --- | --- |
| HTTP 429 | stop worker; record run `status=rate_limited`; do not spin |
| HTTP 5xx / timeout | retry at most 3 times with backoff; then `status=failed` |
| Partial page | do not canonicalize; rerun that since-cursor |
| Mapping miss | quarantine pair; do not invent an instrument |
| Process crash | rerun is idempotent because raw unique key and canonical unique key hold |

Failed runs are retained. Reset = new snapshot/run, never truncate.

---

## 10. Cost and compute

Gate B budget (design, not a purchase):

- 10 pairs × ~43,800 hourly bars / 5y ≈ 438k raw rows
- one worker, public REST only
- no parallel full-universe scrape
- no sub-hour
- feature compute remains request-driven (RSI 12–17, RET(1), RANGE_VOL(1) unless a later request list is approved)

This is small enough that Timescale hypertables are optional at first. Do not build a second warehouse.

---

## 11. Explicitly forbidden until later gates

- Setting any `ops.schema_gate.ingestion_enabled = true`
- Exchange SDK in the repo
- API keys
- Writing production bars
- Ranking / prediction / CUSUM
- Agent runtime
- Paper venue adapters
- Expanding to CRYPTO_FULL or US/CA/IN

---

## 12. Acceptance tests for this design (documentation)

A design is complete when it states all of:

1. Universe members and window
2. Source and symbol map
3. Raw vs canonical grain
4. Checksum and revision rule
5. Validation rejects
6. Backfill vs incremental vs replay
7. Two-clock PIT
8. Failure / idempotency
9. Cost bound
10. Ingest remains disabled

Implementation of a connector is **not** an acceptance test for Gate A.

---

## 13. Conflict report

Checked against the locked constitution:

| Topic | Conflict? |
| --- | --- |
| Two-clock PIT | No — reused |
| Append-only raw | No — revisions are new rows |
| Live path `ops.current_*` | No — ingest does not grant live scans of raw |
| Requested-only features | No — ingest stops at canonical bars |
| CRYPTO_LAB_10 size | No — plan row already exists, `ingested=false` |
| Separate US/CA/IN DBs | No — not requested here |

No constitution change is required to accept this design.

---

## 14. What happens after written approval

Only then may Gate B start, and only as:

1. Flip ingest gate for a **named** run/snapshot, not a global forever-on switch if the existing column is global — prefer run-scoped enable recorded on `ops.ingestion_run`.
2. Implement the Kraken public OHLC adapter behind the existing tables.
3. Backfill CRYPTO_LAB_10.
4. Prove fixture tests still pass and new integration tests cover 10 instruments × PIT.

That work is **not authorized** by publication of this file.
