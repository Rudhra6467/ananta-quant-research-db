CREATE TABLE IF NOT EXISTS research.event_analogue_link (
  id uuid PRIMARY KEY,
  event_a_id uuid NOT NULL REFERENCES research.market_event(id),
  event_b_id uuid NOT NULL REFERENCES research.market_event(id),
  basis text NOT NULL, knowledge_time timestamptz NOT NULL,
  CHECK (event_a_id <> event_b_id)
);
INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
VALUES (gen_random_uuid(), 'phase13', true, false, 'Analogue definition links only. No similarity scores.')
ON CONFLICT (phase) DO UPDATE SET approved = true, ingestion_enabled = false;
