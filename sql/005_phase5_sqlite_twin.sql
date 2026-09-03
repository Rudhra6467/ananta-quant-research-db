-- Phase 5 current-state / regime twin. Not ingest. Not ranking. Not prediction.
CREATE TABLE IF NOT EXISTS state__regime_family (
  id TEXT PRIMARY KEY,
  code TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS state__market_state_observation (
  id TEXT PRIMARY KEY,
  instrument_id TEXT NOT NULL REFERENCES ref__instrument(id),
  venue_id TEXT NOT NULL REFERENCES ref__venue(id),
  timeframe_id TEXT NOT NULL REFERENCES ref__timeframe(id),
  event_time TEXT NOT NULL,
  knowledge_time TEXT NOT NULL,
  close REAL NOT NULL,
  state_version TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE (instrument_id, venue_id, timeframe_id, event_time, knowledge_time)
);
CREATE TABLE IF NOT EXISTS state__regime_observation (
  id TEXT PRIMARY KEY,
  instrument_id TEXT NOT NULL REFERENCES ref__instrument(id),
  timeframe_id TEXT NOT NULL REFERENCES ref__timeframe(id),
  regime_family TEXT NOT NULL,
  label TEXT NOT NULL,
  value REAL,
  epistemic_status TEXT NOT NULL,
  event_time TEXT NOT NULL,
  knowledge_time TEXT NOT NULL,
  provenance TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE (instrument_id, timeframe_id, regime_family, event_time, knowledge_time)
);
CREATE TABLE IF NOT EXISTS ops__state_compile_watermark (
  id TEXT PRIMARY KEY,
  last_event_time TEXT NOT NULL,
  last_regime_label TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
