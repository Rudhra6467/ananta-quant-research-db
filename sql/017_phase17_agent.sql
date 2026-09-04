CREATE TABLE IF NOT EXISTS interface.consult_event (
  id uuid PRIMARY KEY, query_name text NOT NULL, knowledge_time timestamptz NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb, mutated boolean NOT NULL DEFAULT false
);
INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
VALUES (gen_random_uuid(), 'phase17', true, false, 'Catalog consult log. No mutation. INGESTION_ENABLED false.')
ON CONFLICT (phase) DO UPDATE SET approved = true, ingestion_enabled = false;
