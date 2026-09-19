CREATE TABLE IF NOT EXISTS ops__universe_plan (
  id TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE, target_assets INTEGER, target_years INTEGER, ingested INTEGER NOT NULL
);
