CREATE TABLE IF NOT EXISTS ops__market_database_plan (
  id TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE, horizon TEXT NOT NULL, created INTEGER NOT NULL
);
