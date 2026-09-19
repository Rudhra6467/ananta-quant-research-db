-- N2 charter overlay. Does not enable continuous ingest.
CREATE TABLE IF NOT EXISTS ops.activation_charter (
  id uuid PRIMARY KEY, code text NOT NULL, version text NOT NULL, source_code text NOT NULL,
  snapshot_code text NOT NULL, run_code text NOT NULL, window_start timestamptz NOT NULL,
  continuous boolean NOT NULL DEFAULT false, n3_authorized boolean NOT NULL DEFAULT false, UNIQUE (code, version)
);
CREATE TABLE IF NOT EXISTS ops.ingest_quality_report (
  id uuid PRIMARY KEY, run_code text NOT NULL, snapshot_code text NOT NULL, payload jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS ops.ingest_watermark (
  id uuid PRIMARY KEY, instrument_code text NOT NULL, source_code text NOT NULL, last_unix bigint NOT NULL, UNIQUE (instrument_code, source_code)
);
