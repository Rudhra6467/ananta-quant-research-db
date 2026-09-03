-- Phase 2 market-truth foundation for PostgreSQL 16 + TimescaleDB.
-- Operator apply after 0001. Does not enable exchange ingestion.

CREATE SCHEMA IF NOT EXISTS world;
CREATE SCHEMA IF NOT EXISTS market;
CREATE SCHEMA IF NOT EXISTS feature;

CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

ALTER TABLE ref.instrument
  ADD CONSTRAINT uq_instrument_venue_symbol_kind UNIQUE (venue_id, symbol, kind);

CREATE TABLE IF NOT EXISTS raw.market_event (
  id                  uuid PRIMARY KEY,
  data_source_id      uuid NOT NULL REFERENCES ref.data_source(id),
  source_record_id    text NOT NULL,
  instrument_id       uuid NOT NULL REFERENCES ref.instrument(id),
  timeframe_id        uuid NOT NULL REFERENCES ref.timeframe(id),
  dataset_snapshot_id uuid NOT NULL REFERENCES ops.dataset_snapshot(id),
  ingestion_run_id    uuid NOT NULL REFERENCES ops.ingestion_run(id),
  event_time          timestamptz NOT NULL,
  knowledge_time      timestamptz NOT NULL,
  payload             jsonb NOT NULL,
  checksum            text NOT NULL,
  created_at          timestamptz NOT NULL DEFAULT now(),
  UNIQUE (data_source_id, source_record_id),
  CHECK (knowledge_time >= event_time)
);

CREATE TABLE IF NOT EXISTS market.ohlcv_bar (
  id                       uuid PRIMARY KEY,
  instrument_id            uuid NOT NULL REFERENCES ref.instrument(id),
  venue_id                 uuid NOT NULL REFERENCES ref.venue(id),
  timeframe_id             uuid NOT NULL REFERENCES ref.timeframe(id),
  dataset_snapshot_id      uuid NOT NULL REFERENCES ops.dataset_snapshot(id),
  raw_event_id             uuid NOT NULL REFERENCES raw.market_event(id),
  canonicalization_run_id  uuid NOT NULL REFERENCES ops.canonicalization_run(id),
  event_time               timestamptz NOT NULL,
  knowledge_time           timestamptz NOT NULL,
  open                     numeric NOT NULL,
  high                     numeric NOT NULL,
  low                      numeric NOT NULL,
  close                    numeric NOT NULL,
  volume                   numeric NOT NULL,
  canonicalization_version text NOT NULL,
  created_at               timestamptz NOT NULL DEFAULT now(),
  UNIQUE (instrument_id, venue_id, timeframe_id, event_time, canonicalization_version),
  CHECK (knowledge_time >= event_time),
  CHECK (high >= low),
  CHECK (high >= open AND high >= close),
  CHECK (low <= open AND low <= close)
);

CREATE TABLE IF NOT EXISTS research.parameter_region (
  id         uuid PRIMARY KEY,
  feature_id uuid NOT NULL REFERENCES research.feature_definition(id),
  code       text NOT NULL UNIQUE,
  dimension  text NOT NULL,
  lo         numeric NOT NULL,
  hi         numeric NOT NULL,
  detection  text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (hi >= lo)
);

CREATE TABLE IF NOT EXISTS research.parameter_region_member (
  region_id         uuid NOT NULL REFERENCES research.parameter_region(id),
  parameter_set_id  uuid NOT NULL REFERENCES research.parameter_set(id),
  PRIMARY KEY (region_id, parameter_set_id)
);

CREATE TABLE IF NOT EXISTS research.combination_request (
  id               uuid PRIMARY KEY,
  code             text NOT NULL UNIQUE,
  relationship_id  uuid REFERENCES research.relationship_definition(id),
  request_hash     text NOT NULL UNIQUE,
  specification    jsonb NOT NULL,
  created_at       timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS feature.observation (
  id                  uuid PRIMARY KEY,
  feature_version_id  uuid NOT NULL REFERENCES research.feature_version(id),
  parameter_set_id    uuid NOT NULL REFERENCES research.parameter_set(id),
  instrument_id       uuid NOT NULL REFERENCES ref.instrument(id),
  timeframe_id        uuid NOT NULL REFERENCES ref.timeframe(id),
  dataset_snapshot_id uuid NOT NULL REFERENCES ops.dataset_snapshot(id),
  event_time          timestamptz NOT NULL,
  knowledge_time      timestamptz NOT NULL,
  value               numeric NOT NULL,
  created_at          timestamptz NOT NULL DEFAULT now(),
  UNIQUE (feature_version_id, parameter_set_id, instrument_id, timeframe_id, event_time),
  CHECK (knowledge_time >= event_time)
);

CREATE TABLE IF NOT EXISTS ops.persist_watermark (
  stream        text PRIMARY KEY,
  last_event_time timestamptz NOT NULL,
  last_source_record_id text NOT NULL,
  updated_at    timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_ohlcv_inst_tf_time
  ON market.ohlcv_bar (instrument_id, timeframe_id, event_time);
CREATE INDEX IF NOT EXISTS ix_ohlcv_knowledge
  ON market.ohlcv_bar (knowledge_time);
CREATE INDEX IF NOT EXISTS ix_obs_param_time
  ON feature.observation (parameter_set_id, event_time);
CREATE INDEX IF NOT EXISTS ix_obs_knowledge
  ON feature.observation (knowledge_time);
CREATE INDEX IF NOT EXISTS ix_raw_event_time
  ON raw.market_event (event_time);

SELECT create_hypertable('market.ohlcv_bar', 'event_time', if_not_exists => TRUE, migrate_data => TRUE);
SELECT create_hypertable('feature.observation', 'event_time', if_not_exists => TRUE, migrate_data => TRUE);
SELECT create_hypertable('raw.market_event', 'event_time', if_not_exists => TRUE, migrate_data => TRUE);

CREATE OR REPLACE FUNCTION ops.forbid_fact_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'append-only fact table % does not allow %', TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME, TG_OP;
END;
$$;

DO $$
DECLARE t text;
BEGIN
  FOREACH t IN ARRAY ARRAY['raw.market_event', 'market.ohlcv_bar', 'feature.observation']
  LOOP
    EXECUTE format('DROP TRIGGER IF EXISTS trg_no_update ON %s', t);
    EXECUTE format('DROP TRIGGER IF EXISTS trg_no_delete ON %s', t);
    EXECUTE format('CREATE TRIGGER trg_no_update BEFORE UPDATE ON %s FOR EACH ROW EXECUTE FUNCTION ops.forbid_fact_mutation()', t);
    EXECUTE format('CREATE TRIGGER trg_no_delete BEFORE DELETE ON %s FOR EACH ROW EXECUTE FUNCTION ops.forbid_fact_mutation()', t);
  END LOOP;
END;
$$;

INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
VALUES (
  gen_random_uuid(),
  'phase2',
  true,
  false,
  'Fixture persistence approved. Exchange ingestion remains forbidden.'
)
ON CONFLICT (phase) DO NOTHING;
