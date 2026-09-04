-- Phase 6 hypothesis lifecycle. PostgreSQL 16. No ingest. Not a prediction engine.
CREATE TABLE IF NOT EXISTS research.hypothesis (
  id uuid PRIMARY KEY,
  code text NOT NULL UNIQUE,
  relationship_id uuid NOT NULL REFERENCES research.relationship_definition(id),
  claim_kind text NOT NULL CHECK (claim_kind = 'system_hypothesis'),
  version text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS research.hypothesis_status_event (
  id uuid PRIMARY KEY,
  hypothesis_id uuid NOT NULL REFERENCES research.hypothesis(id),
  status text NOT NULL CHECK (status IN (
    'proposed','under_test','supported','contradicted','inconclusive','invalidated','decayed'
  )),
  event_time timestamptz NOT NULL,
  knowledge_time timestamptz NOT NULL,
  evidence_direction text,
  note text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS research.hypothesis_support_link (
  id uuid PRIMARY KEY,
  hypothesis_id uuid NOT NULL REFERENCES research.hypothesis(id),
  source_kind text NOT NULL CHECK (source_kind IN (
    'evidence','market_state','regime_state','feature_observation'
  )),
  source_id text NOT NULL,
  event_time timestamptz NOT NULL,
  knowledge_time timestamptz NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS research.analogue_definition (
  id uuid PRIMARY KEY,
  code text NOT NULL UNIQUE,
  version text NOT NULL,
  metric_name text NOT NULL,
  description text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS analytics.hypothesis_current_status (
  hypothesis_id uuid PRIMARY KEY REFERENCES research.hypothesis(id),
  status text NOT NULL,
  knowledge_time timestamptz NOT NULL,
  computed_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
VALUES (gen_random_uuid(), 'phase6', true, false, 'Fixture hypothesis lifecycle only. INGESTION_ENABLED remains false.')
ON CONFLICT (phase) DO UPDATE SET approved = true, ingestion_enabled = false;
