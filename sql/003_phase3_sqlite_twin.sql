-- Phase 3 fixture evidence. Append-only research facts. Not ranking. Not ingest.
CREATE TABLE IF NOT EXISTS research__validation_stage (
  id TEXT PRIMARY KEY,
  code TEXT NOT NULL UNIQUE,
  sort_order INTEGER NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research__experiment_run (
  id TEXT PRIMARY KEY,
  code TEXT NOT NULL UNIQUE,
  dataset_snapshot_id TEXT REFERENCES ops__dataset_snapshot(id),
  code_commit TEXT,
  config_hash TEXT,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research__experiment_trial (
  id TEXT PRIMARY KEY,
  experiment_run_id TEXT NOT NULL REFERENCES research__experiment_run(id),
  relationship_id TEXT REFERENCES research__relationship_definition(id),
  instrument_id TEXT REFERENCES ref__instrument(id),
  timeframe_id TEXT REFERENCES ref__timeframe(id),
  validation_stage_id TEXT REFERENCES research__validation_stage(id),
  status TEXT NOT NULL,
  skip_reason TEXT,
  window_start INTEGER,
  window_end INTEGER,
  created_at TEXT NOT NULL,
  UNIQUE (experiment_run_id, relationship_id, validation_stage_id)
);
CREATE TABLE IF NOT EXISTS research__relationship_evidence (
  id TEXT PRIMARY KEY,
  relationship_id TEXT NOT NULL REFERENCES research__relationship_definition(id),
  trial_id TEXT REFERENCES research__experiment_trial(id),
  validation_stage_id TEXT REFERENCES research__validation_stage(id),
  experiment_run_id TEXT REFERENCES research__experiment_run(id),
  dataset_snapshot_id TEXT REFERENCES ops__dataset_snapshot(id),
  direction TEXT NOT NULL,
  sample_size INTEGER,
  effect REAL,
  uncertainty REAL,
  payload TEXT NOT NULL,
  knowledge_time TEXT NOT NULL,
  supersedes_id TEXT REFERENCES research__relationship_evidence(id),
  created_at TEXT NOT NULL,
  UNIQUE (trial_id),
  CHECK (direction IN ('untested','supports','contradicts','inconclusive','invalidated','decayed'))
);
CREATE TABLE IF NOT EXISTS analytics__relationship_current_summary (
  relationship_id TEXT PRIMARY KEY REFERENCES research__relationship_definition(id),
  status TEXT NOT NULL,
  blended_score REAL,
  historical_effect REAL,
  oos_effect REAL,
  scoring_model_version TEXT NOT NULL,
  source_watermark TEXT,
  computed_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_evidence_rel_stage ON research__relationship_evidence (relationship_id, validation_stage_id);
CREATE INDEX IF NOT EXISTS ix_evidence_knowledge ON research__relationship_evidence (knowledge_time);
CREATE INDEX IF NOT EXISTS ix_trial_run ON research__experiment_trial (experiment_run_id);
CREATE TRIGGER IF NOT EXISTS trg_evidence_no_update BEFORE UPDATE ON research__relationship_evidence
BEGIN SELECT RAISE(ABORT, 'append-only research.relationship_evidence'); END;
CREATE TRIGGER IF NOT EXISTS trg_evidence_no_delete BEFORE DELETE ON research__relationship_evidence
BEGIN SELECT RAISE(ABORT, 'append-only research.relationship_evidence'); END;
CREATE TRIGGER IF NOT EXISTS trg_trial_no_update BEFORE UPDATE ON research__experiment_trial
BEGIN SELECT RAISE(ABORT, 'append-only research.experiment_trial'); END;
CREATE TRIGGER IF NOT EXISTS trg_trial_no_delete BEFORE DELETE ON research__experiment_trial
BEGIN SELECT RAISE(ABORT, 'append-only research.experiment_trial'); END;
CREATE TRIGGER IF NOT EXISTS trg_run_no_delete BEFORE DELETE ON research__experiment_run
BEGIN SELECT RAISE(ABORT, 'append-only research.experiment_run'); END;
