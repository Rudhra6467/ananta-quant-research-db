CREATE TABLE IF NOT EXISTS research__shift_detector_definition (
  id TEXT PRIMARY KEY, code TEXT NOT NULL, version TEXT NOT NULL, kind TEXT NOT NULL,
  params TEXT NOT NULL, windows TEXT NOT NULL, subject_kind TEXT NOT NULL, created_at TEXT NOT NULL, UNIQUE (code, version)
);
CREATE TABLE IF NOT EXISTS research__shift_detection_run (
  id TEXT PRIMARY KEY, run_code TEXT NOT NULL UNIQUE, detector_code TEXT NOT NULL, version TEXT NOT NULL,
  snapshot_code TEXT NOT NULL, as_of_knowledge_time TEXT NOT NULL, subject_kind TEXT NOT NULL, subject_code TEXT NOT NULL,
  input_digest TEXT, status TEXT NOT NULL, live_claim INTEGER NOT NULL, tape TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research__shift_candidate (
  id TEXT PRIMARY KEY, candidate_code TEXT NOT NULL UNIQUE, run_code TEXT NOT NULL, event_code TEXT NOT NULL,
  kind TEXT NOT NULL, event_time TEXT NOT NULL, knowledge_time TEXT NOT NULL, status TEXT NOT NULL,
  certainty INTEGER NOT NULL, live_claim INTEGER NOT NULL, tape TEXT NOT NULL, note TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research__shift_review_event (
  id TEXT PRIMARY KEY, candidate_code TEXT NOT NULL, status TEXT NOT NULL, note TEXT NOT NULL,
  knowledge_time TEXT NOT NULL, live_claim INTEGER NOT NULL, created_at TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS trg_srev_no_delete BEFORE DELETE ON research__shift_review_event
BEGIN SELECT RAISE(ABORT, 'append-only research.shift_review_event'); END;
CREATE TRIGGER IF NOT EXISTS trg_scand_no_delete BEFORE DELETE ON research__shift_candidate
BEGIN SELECT RAISE(ABORT, 'append-only research.shift_candidate'); END;
