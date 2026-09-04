-- Gate E paper overlay. Reuses P18. NOT Phase 21.
CREATE TABLE IF NOT EXISTS research.paper_decision_definition (
  id uuid PRIMARY KEY, code text NOT NULL, version text NOT NULL, policy text NOT NULL,
  question text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), UNIQUE (code, version)
);
CREATE TABLE IF NOT EXISTS research.paper_session_record (
  id uuid PRIMARY KEY, run_code text NOT NULL UNIQUE, definition_code text NOT NULL, version text NOT NULL,
  policy text NOT NULL, action text NOT NULL, subject_code text NOT NULL, snapshot_code text NOT NULL,
  as_of_knowledge_time timestamptz NOT NULL, context_digest text NOT NULL, input_digest text NOT NULL,
  capital numeric NOT NULL DEFAULT 0, live_order boolean NOT NULL DEFAULT false, tape text NOT NULL DEFAULT 'fixture'
);
CREATE TABLE IF NOT EXISTS research.paper_prediction (
  id uuid PRIMARY KEY, run_code text NOT NULL, target text NOT NULL, horizon text NOT NULL,
  uncertainty text NOT NULL, model text NOT NULL, status text NOT NULL
);
CREATE TABLE IF NOT EXISTS research.paper_risk (
  id uuid PRIMARY KEY, run_code text NOT NULL, policy_version text NOT NULL, status text NOT NULL,
  note text NOT NULL, capital numeric NOT NULL DEFAULT 0, executable boolean NOT NULL DEFAULT false
);
CREATE TABLE IF NOT EXISTS research.paper_outcome (
  id uuid PRIMARY KEY, run_code text NOT NULL, event_time timestamptz NOT NULL,
  knowledge_time timestamptz NOT NULL, note text NOT NULL, value double precision
);
CREATE TABLE IF NOT EXISTS research.paper_evaluation (
  id uuid PRIMARY KEY, run_code text NOT NULL, status text NOT NULL, note text NOT NULL,
  knowledge_time timestamptz NOT NULL, input_digest text NOT NULL
);
