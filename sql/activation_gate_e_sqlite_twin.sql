CREATE TABLE IF NOT EXISTS research__paper_decision_definition (
  id TEXT PRIMARY KEY, code TEXT NOT NULL, version TEXT NOT NULL, policy TEXT NOT NULL, question TEXT NOT NULL, created_at TEXT NOT NULL, UNIQUE (code, version)
);
CREATE TABLE IF NOT EXISTS research__paper_session_record (
  id TEXT PRIMARY KEY, run_code TEXT NOT NULL UNIQUE, definition_code TEXT NOT NULL, version TEXT NOT NULL,
  policy TEXT NOT NULL, action TEXT NOT NULL, subject_code TEXT NOT NULL, snapshot_code TEXT NOT NULL,
  as_of_knowledge_time TEXT NOT NULL, context_digest TEXT NOT NULL, input_digest TEXT NOT NULL,
  capital REAL NOT NULL, live_order INTEGER NOT NULL, tape TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research__paper_prediction (
  id TEXT PRIMARY KEY, run_code TEXT NOT NULL, target TEXT NOT NULL, horizon TEXT NOT NULL, uncertainty TEXT NOT NULL, model TEXT NOT NULL, status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research__paper_risk (
  id TEXT PRIMARY KEY, run_code TEXT NOT NULL, policy_version TEXT NOT NULL, status TEXT NOT NULL, note TEXT NOT NULL, capital REAL NOT NULL, executable INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS research__paper_outcome (
  id TEXT PRIMARY KEY, run_code TEXT NOT NULL, event_time TEXT NOT NULL, knowledge_time TEXT NOT NULL, note TEXT NOT NULL, value REAL
);
CREATE TABLE IF NOT EXISTS research__paper_evaluation (
  id TEXT PRIMARY KEY, run_code TEXT NOT NULL, status TEXT NOT NULL, note TEXT NOT NULL, knowledge_time TEXT NOT NULL, input_digest TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS trg_psess_no_delete BEFORE DELETE ON research__paper_session_record
BEGIN SELECT RAISE(ABORT, 'append-only research.paper_session_record'); END;
CREATE TRIGGER IF NOT EXISTS trg_peval_no_delete BEFORE DELETE ON research__paper_evaluation
BEGIN SELECT RAISE(ABORT, 'append-only research.paper_evaluation'); END;
