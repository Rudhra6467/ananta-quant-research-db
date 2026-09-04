-- Gate C detector overlay. Reuses P11 research.market_event. NOT Phase 21.
CREATE TABLE IF NOT EXISTS research.shift_detector_definition (
  id uuid PRIMARY KEY, code text NOT NULL, version text NOT NULL, kind text NOT NULL,
  params jsonb NOT NULL, windows jsonb NOT NULL, subject_kind text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(), UNIQUE (code, version)
);
CREATE TABLE IF NOT EXISTS research.shift_detection_run (
  id uuid PRIMARY KEY, run_code text NOT NULL UNIQUE, detector_code text NOT NULL, version text NOT NULL,
  snapshot_code text NOT NULL, as_of_knowledge_time timestamptz NOT NULL, subject_kind text NOT NULL,
  subject_code text NOT NULL, input_digest text, status text NOT NULL, live_claim boolean NOT NULL DEFAULT false,
  tape text NOT NULL DEFAULT 'fixture', created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS research.shift_candidate (
  id uuid PRIMARY KEY, candidate_code text NOT NULL UNIQUE, run_code text NOT NULL, event_code text NOT NULL,
  kind text NOT NULL, event_time timestamptz NOT NULL, knowledge_time timestamptz NOT NULL, status text NOT NULL,
  certainty boolean NOT NULL DEFAULT false, live_claim boolean NOT NULL DEFAULT false, tape text NOT NULL DEFAULT 'fixture', note text NOT NULL
);
CREATE TABLE IF NOT EXISTS research.shift_review_event (
  id uuid PRIMARY KEY, candidate_code text NOT NULL, status text NOT NULL, note text NOT NULL,
  knowledge_time timestamptz NOT NULL, live_claim boolean NOT NULL DEFAULT false, created_at timestamptz NOT NULL DEFAULT now()
);
