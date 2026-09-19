CREATE TABLE IF NOT EXISTS research__lab_experiment_definition (
  id TEXT PRIMARY KEY, code TEXT NOT NULL, version TEXT NOT NULL, question TEXT NOT NULL,
  snapshot_code TEXT NOT NULL, hypothesis_code TEXT, measurement_code TEXT, status TEXT NOT NULL,
  created_at TEXT NOT NULL, UNIQUE (code, version)
);
CREATE TABLE IF NOT EXISTS research__lab_cohort (
  id TEXT PRIMARY KEY, code TEXT NOT NULL, experiment_code TEXT NOT NULL, version TEXT NOT NULL,
  note TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research__lab_input_link (
  id TEXT PRIMARY KEY, run_code TEXT NOT NULL, source_kind TEXT NOT NULL, source_ref TEXT NOT NULL, knowledge_time TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research__lab_result (
  id TEXT PRIMARY KEY, run_code TEXT NOT NULL, experiment_code TEXT NOT NULL, version TEXT NOT NULL,
  cohort_code TEXT NOT NULL, snapshot_code TEXT NOT NULL, as_of_knowledge_time TEXT NOT NULL,
  status TEXT NOT NULL, note TEXT NOT NULL, input_digest TEXT NOT NULL, tape TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS trg_labres_no_delete BEFORE DELETE ON research__lab_result
BEGIN SELECT RAISE(ABORT, 'append-only research.lab_result'); END;
CREATE TRIGGER IF NOT EXISTS trg_labcoh_no_delete BEFORE DELETE ON research__lab_cohort
BEGIN SELECT RAISE(ABORT, 'append-only research.lab_cohort'); END;
