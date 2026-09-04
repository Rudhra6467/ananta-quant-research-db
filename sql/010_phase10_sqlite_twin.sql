CREATE TABLE IF NOT EXISTS research__regime_definition (
  id TEXT PRIMARY KEY,
  code TEXT NOT NULL,
  version TEXT NOT NULL,
  family TEXT NOT NULL,
  rules TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE (code, version)
);
