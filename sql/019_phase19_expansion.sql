CREATE TABLE IF NOT EXISTS ops.universe_plan (
  id uuid PRIMARY KEY, code text NOT NULL UNIQUE, target_assets integer, target_years integer, ingested boolean NOT NULL DEFAULT false
);
INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
VALUES (gen_random_uuid(), 'phase19', true, false, 'Universe plan only. ingested false.')
ON CONFLICT (phase) DO UPDATE SET approved = true, ingestion_enabled = false;
