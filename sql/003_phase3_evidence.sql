-- Phase 3 evidence contracts for PostgreSQL 16. No exchange ingest.
CREATE SCHEMA IF NOT EXISTS research;
CREATE SCHEMA IF NOT EXISTS analytics;

ALTER TABLE research.relationship_evidence
  ADD COLUMN IF NOT EXISTS knowledge_time timestamptz;
ALTER TABLE research.relationship_evidence
  ADD COLUMN IF NOT EXISTS experiment_run_id uuid REFERENCES research.experiment_run(id);
ALTER TABLE research.relationship_evidence
  ADD COLUMN IF NOT EXISTS dataset_snapshot_id uuid REFERENCES ops.dataset_snapshot(id);

ALTER TABLE research.experiment_trial
  ADD COLUMN IF NOT EXISTS validation_stage_id uuid REFERENCES research.validation_stage(id);
ALTER TABLE research.experiment_trial
  ADD COLUMN IF NOT EXISTS window_start integer;
ALTER TABLE research.experiment_trial
  ADD COLUMN IF NOT EXISTS window_end integer;

CREATE INDEX IF NOT EXISTS ix_relationship_evidence_rel_stage
  ON research.relationship_evidence (relationship_id, validation_stage_id);
CREATE INDEX IF NOT EXISTS ix_relationship_evidence_knowledge
  ON research.relationship_evidence (knowledge_time);

INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
VALUES (gen_random_uuid(), 'phase3', true, false, 'Fixture evidence only. INGESTION_ENABLED remains false.')
ON CONFLICT (phase) DO UPDATE SET approved = true, ingestion_enabled = false;
