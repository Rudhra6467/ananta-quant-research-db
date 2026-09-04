"""Authorized Q2 trade-agg runner. Restartable. Does not start N3."""
from __future__ import annotations
import json, sqlite3, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from research_db.ingest.source_map import PAIR_MAP, TRADE_AGG
from research_db.ingest.trade_agg import Q2_END_UNIX, Q2_START_UNIX, aggregate_trades
ENDPOINT = "https://api.kraken.com/0/public/Trades"
PAIRS = ["ADAUSD", "LINKUSD", "AVAXUSD", "LTCUSD", "BCHUSD", "XDGUSD", "XRPUSD", "SOLUSD", "ETHUSD", "XBTUSD"]
EXPECTED_HOURS = 2184
def fetch_page(pair: str, since, retries: int = 8):
    q = urllib.parse.urlencode({"pair": pair, "since": since})
    req = urllib.request.Request(f"{ENDPOINT}?{q}", headers={"User-Agent": "ananta-n27-q2"})
    delay = 3.0
    last_err = None
    for _ in range(retries):
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        err = data.get("error") or []
        if not err:
            result = data["result"]
            last = result.get("last")
            rows = next(v for k, v in result.items() if k != "last")
            return rows, last
        last_err = err
        if any("Too many requests" in str(e) for e in err):
            time.sleep(delay)
            delay = min(delay * 1.7, 30.0)
            continue
        raise RuntimeError(str(err))
    raise RuntimeError(str(last_err))
def open_db(db: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE IF NOT EXISTS watermark(pair TEXT PRIMARY KEY, since TEXT, pages INTEGER, last_ts REAL)")
    conn.execute("CREATE TABLE IF NOT EXISTS bars(source_code TEXT, source_record_id TEXT PRIMARY KEY, instrument TEXT, event_unix INTEGER, open REAL, high REAL, low REAL, close REAL, volume REAL, trades INTEGER)")
    return conn
def run_pair(pair: str, db: Path, sleep_s: float = 1.2, max_pages: int | None = None) -> dict:
    conn = open_db(db)
    wm = conn.execute("SELECT since, pages, last_ts FROM watermark WHERE pair=?", (pair,)).fetchone()
    since = wm[0] if wm else str(Q2_START_UNIX)
    pages = wm[1] if wm else 0
    last_ts = wm[2] if wm else float(Q2_START_UNIX)
    ticks = []
    done = last_ts >= Q2_END_UNIX - 1
    while not done:
        if max_pages is not None and pages >= max_pages:
            break
        rows, last = fetch_page(pair, since)
        pages += 1
        if not rows:
            done = True
            break
        for row in rows:
            ts = float(row[2])
            if Q2_START_UNIX <= ts < Q2_END_UNIX:
                ticks.append((float(row[0]), float(row[1]), ts))
                if ts > last_ts:
                    last_ts = ts
        since = str(int(last_ts) + 1)
        conn.execute("INSERT INTO watermark(pair,since,pages,last_ts) VALUES(?,?,?,?) ON CONFLICT(pair) DO UPDATE SET since=excluded.since, pages=excluded.pages, last_ts=excluded.last_ts", (pair, since, pages, last_ts))
        conn.commit()
        print({"pair": pair, "pages": pages, "last_ts": last_ts}, flush=True)
        if last_ts >= Q2_END_UNIX - 1:
            done = True
            break
        time.sleep(sleep_s)
    bars = aggregate_trades(ticks, wire=pair)
    inst = PAIR_MAP[pair]
    for b in bars:
        conn.execute("INSERT OR REPLACE INTO bars VALUES(?,?,?,?,?,?,?,?,?,?)", (TRADE_AGG, f"tradesagg:{pair}:60:{b['event_unix']}", inst, b["event_unix"], b["open"], b["high"], b["low"], b["close"], b["volume"], b["trades"]))
    conn.commit()
    n_bars = conn.execute("SELECT COUNT(*) FROM bars WHERE instrument=?", (inst,)).fetchone()[0]
    conn.close()
    return {"pair": pair, "instrument": inst, "pages": pages, "bars": n_bars, "expected_hours": EXPECTED_HOURS, "last_ts": last_ts, "done": done, "source_code": TRADE_AGG}
