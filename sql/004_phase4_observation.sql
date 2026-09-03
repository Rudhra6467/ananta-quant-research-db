-- Phase 4 observation-engine contracts. PostgreSQL 16. No exchange ingest.
CREATE TABLE IF NOT EXISTS research.feature_request (
  id uuid PRIMARY KEY,
  feature_version_id uuid NOT NULL REFERENCES research.feature_version(id),
  parameter_set_id uuid NOT NULL REFERENCES research.parameter_set(id),
  signature text NOT NULL UNIQUE,
  status text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS ops.feature_roll_state (
  parameter_set_id uuid PRIMARY KEY REFERENCES research.parameter_set(id),
  period integer NOT NULL,
  last_event_time timestamptz,
  last_close numeric,
  avg_gain numeric,
  avg_loss numeric,
  primed boolean NOT NULL DEFAULT false,
  seed_closes jsonb NOT NULL DEFAULT '[]'::jsonb,
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS ops.observation_watermark (
  parameter_set_id uuid PRIMARY KEY REFERENCES research.parameter_set(id),
  last_event_time timestamptz NOT NULL,
  last_count integer NOT NULL,
  updated_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
VALUES (gen_random_uuid(), 'phase4', true, false, 'Fixture observation engine only. INGESTION_ENABLED remains false.')
ON CONFLICT (phase) DO UPDATE SET approved = true, ingestion_enabled = false;
