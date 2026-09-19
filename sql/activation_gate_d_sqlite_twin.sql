CREATE TABLE IF NOT EXISTS interface__agent_capability (
  id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, layer TEXT NOT NULL, status TEXT NOT NULL, mutation INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS interface__agent_context (
  id TEXT PRIMARY KEY, subject_code TEXT NOT NULL, snapshot_code TEXT NOT NULL,
  as_of_knowledge_time TEXT NOT NULL, catalog_version TEXT NOT NULL, uncertainty TEXT NOT NULL,
  digest TEXT NOT NULL, live_claim INTEGER NOT NULL, mutated INTEGER NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS interface__agent_context_item (
  id TEXT PRIMARY KEY, context_digest TEXT NOT NULL, capability TEXT NOT NULL, layer TEXT NOT NULL, ref TEXT NOT NULL, knowledge_time TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS trg_actx_no_delete BEFORE DELETE ON interface__agent_context
BEGIN SELECT RAISE(ABORT, 'append-only interface.agent_context'); END;
