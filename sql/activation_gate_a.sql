-- Activation Gate A scaffolding. NOT a Phase 21. Ingest remains disabled.
CREATE TABLE IF NOT EXISTS ops.quarantine_record (
  id uuid PRIMARY KEY, run_code text NOT NULL, source_record_id text NOT NULL,
  reason text NOT NULL, event_time timestamptz, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS ops.ingest_audit (
  id uuid PRIMARY KEY, run_code text NOT NULL, snapshot_code text NOT NULL,
  provider_kind text NOT NULL, accepted integer NOT NULL, quarantined integer NOT NULL,
  duplicates integer NOT NULL, ingestion_enabled boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS ops.source_symbol_map (
  id uuid PRIMARY KEY, source_code text NOT NULL, wire_symbol text NOT NULL,
  instrument_code text NOT NULL, UNIQUE (source_code, wire_symbol)
);
