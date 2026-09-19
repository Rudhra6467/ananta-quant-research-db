CREATE TABLE IF NOT EXISTS research.cross_subject_link (
  id uuid PRIMARY KEY, left_kind text NOT NULL, left_code text NOT NULL, relation text NOT NULL,
  right_kind text NOT NULL, right_code text NOT NULL, via text,
  effective_time timestamptz NOT NULL, expiry_time timestamptz, knowledge_time timestamptz NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
VALUES (gen_random_uuid(), 'phase12', true, false, 'Declared cross-subject links only. No correlation engine.')
ON CONFLICT (phase) DO UPDATE SET approved = true, ingestion_enabled = false;
