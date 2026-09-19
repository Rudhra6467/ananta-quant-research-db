-- Phase 6 hypothesis twin. Append-only events. Not ranking. Not ingest. Not prediction.
CREATE TABLE IF NOT EXISTS research__hypothesis (
  id TEXT PRIMARY KEY,
  code TEXT NOT NULL UNIQUE,
  relationship_id TEXT NOT NULL REFERENCES research__relationship_definition(id),
  claim_kind TEXT NOT NULL CHECK (claim_kind = 'system_hypothesis'),
  version TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research__hypothesis_status_event (
  id TEXT PRIMARY KEY,
  hypothesis_id TEXT NOT NULL REFERENCES research__hypothesis(id),
  status TEXT NOT NULL CHECK (status IN (
    'proposed','under_test','supported','contradicted','inconclusive','invalidated','decayed'
  )),
  event_time TEXT NOT NULL,
  knowledge_time TEXT NOT NULL,
  evidence_direction TEXT,
  note TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research__hypothesis_support_link (
  id TEXT PRIMARY KEY,
  hypothesis_id TEXT NOT NULL REFERENCES research__hypothesis(id),
  source_kind TEXT NOT NULL CHECK (source_kind IN (
    'evidence','market_state','regime_state','feature_observation'
  )),
  source_id TEXT NOT NULL,
  event_time TEXT NOT NULL,
  knowledge_time TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research__analogue_definition (
  id TEXT PRIMARY KEY,
  code TEXT NOT NULL UNIQUE,
  version TEXT NOT NULL,
  metric_name TEXT NOT NULL,
  description TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS analytics__hypothesis_current_status (
  hypothesis_id TEXT PRIMARY KEY REFERENCES research__hypothesis(id),
  status TEXT NOT NULL,
  knowledge_time TEXT NOT NULL,
  computed_at TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS trg_hsev_no_update BEFORE UPDATE ON research__hypothesis_status_event
BEGIN SELECT RAISE(ABORT, 'append-only research.hypothesis_status_event'); END;
CREATE TRIGGER IF NOT EXISTS trg_hsev_no_delete BEFORE DELETE ON research__hypothesis_status_event
BEGIN SELECT RAISE(ABORT, 'append-only research.hypothesis_status_event'); END;
CREATE TRIGGER IF NOT EXISTS trg_hsl_no_update BEFORE UPDATE ON research__hypothesis_support_link
BEGIN SELECT RAISE(ABORT, 'append-only research.hypothesis_support_link'); END;
CREATE TRIGGER IF NOT EXISTS trg_hsl_no_delete BEFORE DELETE ON research__hypothesis_support_link
BEGIN SELECT RAISE(ABORT, 'append-only research.hypothesis_support_link'); END;
