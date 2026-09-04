CREATE TABLE IF NOT EXISTS ops.market_database_plan (
  id uuid PRIMARY KEY, code text NOT NULL UNIQUE, horizon text NOT NULL, created boolean NOT NULL DEFAULT false
);
INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
VALUES (gen_random_uuid(), 'phase20', true, false, 'Multi-market plan only. created false.')
ON CONFLICT (phase) DO UPDATE SET approved = true, ingestion_enabled = false;
