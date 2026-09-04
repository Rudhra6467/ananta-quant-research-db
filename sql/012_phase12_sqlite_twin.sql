CREATE TABLE IF NOT EXISTS research__cross_subject_link (
  id TEXT PRIMARY KEY, left_kind TEXT NOT NULL, left_code TEXT NOT NULL, relation TEXT NOT NULL,
  right_kind TEXT NOT NULL, right_code TEXT NOT NULL, via TEXT,
  effective_time TEXT NOT NULL, expiry_time TEXT, knowledge_time TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS trg_csl_no_delete BEFORE DELETE ON research__cross_subject_link
BEGIN SELECT RAISE(ABORT, 'append-only research.cross_subject_link'); END;
