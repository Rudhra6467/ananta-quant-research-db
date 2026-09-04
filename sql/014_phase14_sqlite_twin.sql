CREATE TABLE IF NOT EXISTS research__memory_tier_policy (
  id TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE, tier TEXT NOT NULL,
  horizon TEXT NOT NULL, deletes_raw INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS research__memory_summary (
  id TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE, tier TEXT NOT NULL,
  n INTEGER NOT NULL, mean_close REAL, min_close REAL, max_close REAL,
  start_time TEXT NOT NULL, end_time TEXT NOT NULL, raw_retained INTEGER NOT NULL
);
