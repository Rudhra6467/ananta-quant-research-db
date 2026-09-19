-- Phase 11 event representation. Not a detector. No ingest.
CREATE TABLE IF NOT EXISTS research.market_event (
  id uuid PRIMARY KEY, code text NOT NULL UNIQUE,
  kind text NOT NULL CHECK (kind IN ('anomaly', 'break', 'shift', 'regime_transition')),
  subject_kind text NOT NULL, subject_code text NOT NULL,
  onset_time timestamptz NOT NULL, event_time timestamptz NOT NULL, peak_time timestamptz,
  knowledge_time timestamptz NOT NULL, notes text NOT NULL DEFAULT '', created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS research.event_window (
  id uuid PRIMARY KEY, event_id uuid NOT NULL REFERENCES research.market_event(id),
  kind text NOT NULL CHECK (kind IN ('pre', 'event', 'post')),
  start_time timestamptz NOT NULL, end_time timestamptz NOT NULL, CHECK (end_time >= start_time)
);
CREATE TABLE IF NOT EXISTS research.event_context_link (
  id uuid PRIMARY KEY, event_id uuid NOT NULL REFERENCES research.market_event(id),
  source_kind text NOT NULL, source_ref text NOT NULL, knowledge_time timestamptz NOT NULL
);
INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
VALUES (gen_random_uuid(), 'phase11', true, false, 'Event representation only. No detector. INGESTION_ENABLED false.')
ON CONFLICT (phase) DO UPDATE SET approved = true, ingestion_enabled = false;
