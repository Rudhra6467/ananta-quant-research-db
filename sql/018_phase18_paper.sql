CREATE TABLE IF NOT EXISTS research.operating_profile (
  id uuid PRIMARY KEY, code text NOT NULL UNIQUE, max_risk text NOT NULL, live_capital boolean NOT NULL DEFAULT false
);
CREATE TABLE IF NOT EXISTS research.paper_decision (
  id uuid PRIMARY KEY, profile_code text NOT NULL, action text NOT NULL,
  knowledge_time timestamptz NOT NULL, reason text NOT NULL, query_name text, capital numeric NOT NULL DEFAULT 0
);
INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
VALUES (gen_random_uuid(), 'phase18', true, false, 'Paper ledger only. live_capital false. INGESTION_ENABLED false.')
ON CONFLICT (phase) DO UPDATE SET approved = true, ingestion_enabled = false;
