-- Gate F readiness overlay. NOT Phase 21. ingested remains false.
CREATE TABLE IF NOT EXISTS ops.scaleout_instrument_plan (
  id uuid PRIMARY KEY, code text NOT NULL UNIQUE, venue text NOT NULL, market text NOT NULL,
  ingested boolean NOT NULL DEFAULT false, fixture boolean NOT NULL DEFAULT false
);
CREATE TABLE IF NOT EXISTS ops.scaleout_world (
  id uuid PRIMARY KEY, code text NOT NULL UNIQUE, isolated boolean NOT NULL
);
CREATE TABLE IF NOT EXISTS ops.scaleout_lineage (
  id uuid PRIMARY KEY, step text NOT NULL UNIQUE, status text NOT NULL
);
CREATE TABLE IF NOT EXISTS ops.production_checklist (
  id uuid PRIMARY KEY, item text NOT NULL UNIQUE, state text NOT NULL
);
