-- Phase 9 requested analytical features. No cube. No ingest. No group aggregation.
INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
VALUES (gen_random_uuid(), 'phase9', true, false, 'Requested RET(1) and RANGE_VOL(1) only. INGESTION_ENABLED false.')
ON CONFLICT (phase) DO UPDATE SET approved = true, ingestion_enabled = false;
