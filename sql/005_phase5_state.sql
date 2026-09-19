-- Phase 5 current-state / regime contracts. PostgreSQL 16. No exchange ingest.
CREATE SCHEMA IF NOT EXISTS state;

CREATE TABLE IF NOT EXISTS state.regime_family (
  id uuid PRIMARY KEY,
  code text NOT NULL UNIQUE,
  description text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS state.market_state_observation (
  id uuid PRIMARY KEY,
  instrument_id uuid NOT NULL REFERENCES ref.instrument(id),
  venue_id uuid NOT NULL REFERENCES ref.venue(id),
  timeframe_id uuid NOT NULL REFERENCES ref.timeframe(id),
  event_time timestamptz NOT NULL,
  knowledge_time timestamptz NOT NULL,
  close numeric NOT NULL,
  state_version text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (instrument_id, venue_id, timeframe_id, event_time, knowledge_time)
);

CREATE TABLE IF NOT EXISTS state.regime_observation (
  id uuid PRIMARY KEY,
  instrument_id uuid NOT NULL REFERENCES ref.instrument(id),
  timeframe_id uuid NOT NULL REFERENCES ref.timeframe(id),
  regime_family text NOT NULL,
  label text NOT NULL,
  value numeric,
  epistemic_status text NOT NULL,
  event_time timestamptz NOT NULL,
  knowledge_time timestamptz NOT NULL,
  provenance jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (instrument_id, timeframe_id, regime_family, event_time, knowledge_time)
);

CREATE TABLE IF NOT EXISTS ops.state_compile_watermark (
  id text PRIMARY KEY,
  last_event_time timestamptz NOT NULL,
  last_regime_label text NOT NULL,
  updated_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
VALUES (gen_random_uuid(), 'phase5', true, false, 'Fixture current-state compiler only. INGESTION_ENABLED remains false.')
ON CONFLICT (phase) DO UPDATE SET approved = true, ingestion_enabled = false;
