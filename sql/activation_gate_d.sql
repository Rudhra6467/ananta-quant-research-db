-- Gate D read-only agent catalog. NOT runtime. NOT Phase 21.
CREATE TABLE IF NOT EXISTS interface.agent_capability (
  id uuid PRIMARY KEY, name text NOT NULL UNIQUE, layer text NOT NULL, status text NOT NULL, mutation boolean NOT NULL DEFAULT false
);
CREATE TABLE IF NOT EXISTS interface.agent_context (
  id uuid PRIMARY KEY, subject_code text NOT NULL, snapshot_code text NOT NULL,
  as_of_knowledge_time timestamptz NOT NULL, catalog_version text NOT NULL, uncertainty text NOT NULL,
  digest text NOT NULL, live_claim boolean NOT NULL DEFAULT false, mutated boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS interface.agent_context_item (
  id uuid PRIMARY KEY, context_digest text NOT NULL, capability text NOT NULL, layer text NOT NULL, ref text NOT NULL, knowledge_time timestamptz NOT NULL
);
