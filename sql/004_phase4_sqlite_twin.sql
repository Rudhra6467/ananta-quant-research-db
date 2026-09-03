-- Phase 4 request-driven observation engine. Not a parameter cube. Not ingest.
CREATE TABLE IF NOT EXISTS research__feature_request (
  id TEXT PRIMARY KEY,
  feature_version_id TEXT NOT NULL REFERENCES research__feature_version(id),
  parameter_set_id TEXT NOT NULL REFERENCES research__parameter_set(id),
  signature TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ops__feature_roll_state (
  parameter_set_id TEXT PRIMARY KEY REFERENCES research__parameter_set(id),
  period INTEGER NOT NULL,
  last_event_time TEXT,
  last_close REAL,
  avg_gain REAL,
  avg_loss REAL,
  primed INTEGER NOT NULL,
  seed_closes TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ops__observation_watermark (
  parameter_set_id TEXT PRIMARY KEY REFERENCES research__parameter_set(id),
  last_event_time TEXT NOT NULL,
  last_count INTEGER NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_feature_request_status ON research__feature_request (status);
