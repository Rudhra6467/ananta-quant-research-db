CREATE TABLE IF NOT EXISTS ops__activation_charter (
  id TEXT PRIMARY KEY, code TEXT NOT NULL, version TEXT NOT NULL, source_code TEXT NOT NULL,
  snapshot_code TEXT NOT NULL, run_code TEXT NOT NULL, window_start TEXT NOT NULL,
  continuous INTEGER NOT NULL, n3_authorized INTEGER NOT NULL, UNIQUE (code, version)
);
CREATE TABLE IF NOT EXISTS ops__ingest_quality_report (
  id TEXT PRIMARY KEY, run_code TEXT NOT NULL, snapshot_code TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ops__ingest_watermark (
  id TEXT PRIMARY KEY, instrument_code TEXT NOT NULL, source_code TEXT NOT NULL, last_unix INTEGER NOT NULL, UNIQUE (instrument_code, source_code)
);
