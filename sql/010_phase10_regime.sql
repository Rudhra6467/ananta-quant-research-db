-- Phase 10 versioned regime definitions. Does not replace state observations.
CREATE TABLE IF NOT EXISTS research.regime_definition (
  id uuid PRIMARY KEY,
  code text NOT NULL,
  version text NOT NULL,
  family text NOT NULL,
  rules jsonb NOT NULL,
  status text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (code, version)
);

INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
VALUES (gen_random_uuid(), 'phase10', true, false, 'Versioned regime definitions only. INGESTION_ENABLED false.')
ON CONFLICT (phase) DO UPDATE SET approved = true, ingestion_enabled = false;
