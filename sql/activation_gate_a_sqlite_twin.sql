CREATE TABLE IF NOT EXISTS ops__quarantine_record (
  id TEXT PRIMARY KEY, run_code TEXT NOT NULL, source_record_id TEXT NOT NULL,
  reason TEXT NOT NULL, event_time TEXT, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ops__ingest_audit (
  id TEXT PRIMARY KEY, run_code TEXT NOT NULL, snapshot_code TEXT NOT NULL,
  provider_kind TEXT NOT NULL, accepted INTEGER NOT NULL, quarantined INTEGER NOT NULL,
  duplicates INTEGER NOT NULL, ingestion_enabled INTEGER NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ops__source_symbol_map (
  id TEXT PRIMARY KEY, source_code TEXT NOT NULL, wire_symbol TEXT NOT NULL,
  instrument_code TEXT NOT NULL, UNIQUE (source_code, wire_symbol)
);
