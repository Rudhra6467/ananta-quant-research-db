CREATE TABLE IF NOT EXISTS research__operating_profile (
  id TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE, max_risk TEXT NOT NULL, live_capital INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS research__paper_decision (
  id TEXT PRIMARY KEY, profile_code TEXT NOT NULL, action TEXT NOT NULL,
  knowledge_time TEXT NOT NULL, reason TEXT NOT NULL, query_name TEXT, capital REAL NOT NULL
);
