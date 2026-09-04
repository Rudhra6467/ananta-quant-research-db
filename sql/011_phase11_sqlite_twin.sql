CREATE TABLE IF NOT EXISTS research__market_event (
  id TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE,
  kind TEXT NOT NULL CHECK (kind IN ('anomaly', 'break', 'shift', 'regime_transition')),
  subject_kind TEXT NOT NULL, subject_code TEXT NOT NULL,
  onset_time TEXT NOT NULL, event_time TEXT NOT NULL, peak_time TEXT,
  knowledge_time TEXT NOT NULL, notes TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research__event_window (
  id TEXT PRIMARY KEY, event_id TEXT NOT NULL REFERENCES research__market_event(id),
  kind TEXT NOT NULL CHECK (kind IN ('pre', 'event', 'post')),
  start_time TEXT NOT NULL, end_time TEXT NOT NULL, CHECK (end_time >= start_time)
);
CREATE TABLE IF NOT EXISTS research__event_context_link (
  id TEXT PRIMARY KEY, event_id TEXT NOT NULL REFERENCES research__market_event(id),
  source_kind TEXT NOT NULL, source_ref TEXT NOT NULL, knowledge_time TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS trg_mev_no_update BEFORE UPDATE ON research__market_event
BEGIN SELECT RAISE(ABORT, 'append-only research.market_event'); END;
CREATE TRIGGER IF NOT EXISTS trg_mev_no_delete BEFORE DELETE ON research__market_event
BEGIN SELECT RAISE(ABORT, 'append-only research.market_event'); END;
