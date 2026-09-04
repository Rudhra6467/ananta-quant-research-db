CREATE TABLE IF NOT EXISTS research__event_analogue_link (
  id TEXT PRIMARY KEY, event_a TEXT NOT NULL, event_b TEXT NOT NULL,
  basis TEXT NOT NULL, knowledge_time TEXT NOT NULL, CHECK (event_a <> event_b)
);
