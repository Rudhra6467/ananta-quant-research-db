-- Gate B laboratory overlays. Reuses research.experiment_run (P3). NOT Phase 21.
CREATE TABLE IF NOT EXISTS research.lab_experiment_definition (
  id uuid PRIMARY KEY, code text NOT NULL, version text NOT NULL, question text NOT NULL,
  snapshot_code text NOT NULL, hypothesis_code text, measurement_code text, status text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(), UNIQUE (code, version)
);
CREATE TABLE IF NOT EXISTS research.lab_cohort (
  id uuid PRIMARY KEY, code text NOT NULL, experiment_code text NOT NULL, version text NOT NULL,
  note text NOT NULL DEFAULT '', created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS research.lab_input_link (
  id uuid PRIMARY KEY, run_code text NOT NULL, source_kind text NOT NULL, source_ref text NOT NULL, knowledge_time timestamptz NOT NULL
);
CREATE TABLE IF NOT EXISTS research.lab_result (
  id uuid PRIMARY KEY, run_code text NOT NULL, experiment_code text NOT NULL, version text NOT NULL,
  cohort_code text NOT NULL, snapshot_code text NOT NULL, as_of_knowledge_time timestamptz NOT NULL,
  status text NOT NULL, note text NOT NULL, input_digest text NOT NULL, tape text NOT NULL DEFAULT 'fixture',
  created_at timestamptz NOT NULL DEFAULT now()
);
