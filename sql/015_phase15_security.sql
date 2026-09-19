CREATE TABLE IF NOT EXISTS ops.access_grant (
  id uuid PRIMARY KEY, role text NOT NULL, surface text NOT NULL, action text NOT NULL
);
CREATE TABLE IF NOT EXISTS ops.access_forbid (
  id uuid PRIMARY KEY, role text NOT NULL, surface text NOT NULL, action text NOT NULL
);
INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
VALUES (gen_random_uuid(), 'phase15', true, false, 'Access policy. Agent has no write. INGESTION_ENABLED false.')
ON CONFLICT (phase) DO UPDATE SET approved = true, ingestion_enabled = false;
