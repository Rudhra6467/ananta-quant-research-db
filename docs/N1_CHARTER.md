# N1 charter — CRYPTO_LAB_10 real tape

Version: `N1.CRYPTO_LAB_10` / `v1`
N3 is **not** authorized by this charter.

Instruments: BTC ETH SOL XRP ADA AVAX LINK DOGE LTC BCH `-USD-SPOT`
Source: `kraken.ohlc.spot` (public OHLC, no credentials)
Venue/market/tf: KRAKEN / spot / 1h
Window start: 2021-09-01T00:00:00Z through last complete 1h bar
Snapshot: `snap-cryptolab10-kraken-1h-v1`
Run: `run-n2-kraken-ohlc-charter-v1`
Endpoint: `https://api.kraken.com/0/public/OHLC`
Continuous: false. Capital/agent/orders: false.
Revisions: new source_record_id + later knowledge_time. No raw UPDATE.
