CREATE TABLE IF NOT EXISTS interface__consult_event (
  id TEXT PRIMARY KEY, query_name TEXT NOT NULL, knowledge_time TEXT NOT NULL,
  payload TEXT NOT NULL, mutated INTEGER NOT NULL
);
