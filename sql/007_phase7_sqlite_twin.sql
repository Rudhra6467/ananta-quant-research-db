-- Phase 7 measurement twin. Append-only facts. Not a stats engine. Not ingest.
CREATE TABLE IF NOT EXISTS research__measurement_family (
  id TEXT PRIMARY KEY,
  code TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research__measurement_definition (
  id TEXT PRIMARY KEY,
  code TEXT NOT NULL UNIQUE,
  family_id TEXT NOT NULL REFERENCES research__measurement_family(id),
  param_schema TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research__measurement_request (
  id TEXT PRIMARY KEY,
  definition_id TEXT NOT NULL REFERENCES research__measurement_definition(id),
  code TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research__measurement_observation (
  id TEXT PRIMARY KEY,
  definition_id TEXT NOT NULL REFERENCES research__measurement_definition(id),
  relationship_id TEXT REFERENCES research__relationship_definition(id),
  hypothesis_id TEXT,
  experiment_run_id TEXT,
  dataset_snapshot_id TEXT,
  point_value REAL,
  sample_size INTEGER,
  epistemic_status TEXT NOT NULL,
  evidence_direction TEXT,
  condition_digest TEXT NOT NULL,
  event_time TEXT NOT NULL,
  knowledge_time TEXT NOT NULL,
  payload TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research__measurement_distribution (
  id TEXT PRIMARY KEY,
  measurement_observation_id TEXT NOT NULL REFERENCES research__measurement_observation(id),
  representation TEXT NOT NULL,
  payload TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS analytics__measurement_current (
  definition_id TEXT NOT NULL,
  relationship_id TEXT NOT NULL,
  condition_digest TEXT NOT NULL,
  point_value REAL,
  epistemic_status TEXT NOT NULL,
  knowledge_time TEXT NOT NULL,
  computed_at TEXT NOT NULL,
  PRIMARY KEY (definition_id, condition_digest, relationship_id)
);
CREATE TRIGGER IF NOT EXISTS trg_mobs_no_update BEFORE UPDATE ON research__measurement_observation
BEGIN SELECT RAISE(ABORT, 'append-only research.measurement_observation'); END;
CREATE TRIGGER IF NOT EXISTS trg_mobs_no_delete BEFORE DELETE ON research__measurement_observation
BEGIN SELECT RAISE(ABORT, 'append-only research.measurement_observation'); END;
CREATE TRIGGER IF NOT EXISTS trg_mdist_no_update BEFORE UPDATE ON research__measurement_distribution
BEGIN SELECT RAISE(ABORT, 'append-only research.measurement_distribution'); END;
CREATE TRIGGER IF NOT EXISTS trg_mdist_no_delete BEFORE DELETE ON research__measurement_distribution
BEGIN SELECT RAISE(ABORT, 'append-only research.measurement_distribution'); END;
