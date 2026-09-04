CREATE SCHEMA IF NOT EXISTS interface;
CREATE TABLE IF NOT EXISTS interface.query_catalog (
  id uuid PRIMARY KEY, name text NOT NULL UNIQUE, mutation boolean NOT NULL DEFAULT false
);
INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
VALUES (gen_random_uuid(), 'phase16', true, false, 'Read-only query catalog. No agent runtime.')
ON CONFLICT (phase) DO UPDATE SET approved = true, ingestion_enabled = false;
