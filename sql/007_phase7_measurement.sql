-- Phase 7 measurement contracts. PostgreSQL 16. Requested facts only. No ingest.
CREATE TABLE IF NOT EXISTS research.measurement_family (
  id uuid PRIMARY KEY,
  code text NOT NULL UNIQUE,
  description text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS research.measurement_definition (
  id uuid PRIMARY KEY,
  code text NOT NULL UNIQUE,
  family_id uuid NOT NULL REFERENCES research.measurement_family(id),
  param_schema jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS research.measurement_request (
  id uuid PRIMARY KEY,
  definition_id uuid NOT NULL REFERENCES research.measurement_definition(id),
  code text NOT NULL UNIQUE,
  status text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS research.measurement_observation (
  id uuid PRIMARY KEY,
  definition_id uuid NOT NULL REFERENCES research.measurement_definition(id),
  relationship_id uuid REFERENCES research.relationship_definition(id),
  hypothesis_id uuid REFERENCES research.hypothesis(id),
  experiment_run_id uuid,
  dataset_snapshot_id uuid,
  point_value numeric,
  sample_size integer,
  epistemic_status text NOT NULL,
  evidence_direction text,
  condition_digest text NOT NULL,
  event_time timestamptz NOT NULL,
  knowledge_time timestamptz NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS research.measurement_distribution (
  id uuid PRIMARY KEY,
  measurement_observation_id uuid NOT NULL REFERENCES research.measurement_observation(id),
  representation text NOT NULL,
  payload jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS analytics.measurement_current (
  definition_id uuid NOT NULL REFERENCES research.measurement_definition(id),
  relationship_id uuid,
  condition_digest text NOT NULL,
  point_value numeric,
  epistemic_status text NOT NULL,
  knowledge_time timestamptz NOT NULL,
  computed_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (definition_id, condition_digest, relationship_id)
);

INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
VALUES (gen_random_uuid(), 'phase7', true, false, 'Fixture measurement representation only. INGESTION_ENABLED remains false.')
ON CONFLICT (phase) DO UPDATE SET approved = true, ingestion_enabled = false;
