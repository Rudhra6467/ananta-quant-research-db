CREATE TABLE IF NOT EXISTS research.memory_tier_policy (
  id uuid PRIMARY KEY, code text NOT NULL UNIQUE, tier text NOT NULL,
  horizon text NOT NULL, deletes_raw boolean NOT NULL DEFAULT false
);
CREATE TABLE IF NOT EXISTS research.memory_summary (
  id uuid PRIMARY KEY, code text NOT NULL UNIQUE, tier text NOT NULL,
  n integer NOT NULL, mean_close numeric, min_close numeric, max_close numeric,
  start_time timestamptz NOT NULL, end_time timestamptz NOT NULL, raw_retained boolean NOT NULL
);
INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
VALUES (gen_random_uuid(), 'phase14', true, false, 'Memory tiers. Raw retained. INGESTION_ENABLED false.')
ON CONFLICT (phase) DO UPDATE SET approved = true, ingestion_enabled = false;
