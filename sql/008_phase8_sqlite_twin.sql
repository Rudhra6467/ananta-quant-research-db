-- Phase 8 grouping twin. Append-only membership facts. Not aggregation. Not ingest.
CREATE TABLE IF NOT EXISTS research__market_group (
  id TEXT PRIMARY KEY,
  code TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('market', 'asset_class', 'sector', 'category', 'group')),
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research__group_membership (
  id TEXT PRIMARY KEY,
  group_id TEXT NOT NULL REFERENCES research__market_group(id),
  member_kind TEXT NOT NULL CHECK (member_kind IN ('instrument', 'asset', 'group')),
  member_instrument_id TEXT,
  member_asset_id TEXT,
  member_group_id TEXT REFERENCES research__market_group(id),
  member_code TEXT NOT NULL,
  effective_time TEXT NOT NULL,
  expiry_time TEXT,
  knowledge_time TEXT NOT NULL,
  created_at TEXT NOT NULL,
  CHECK (
    (member_kind = 'instrument' AND member_instrument_id IS NOT NULL AND member_asset_id IS NULL AND member_group_id IS NULL)
    OR (member_kind = 'asset' AND member_asset_id IS NOT NULL AND member_instrument_id IS NULL AND member_group_id IS NULL)
    OR (member_kind = 'group' AND member_group_id IS NOT NULL AND member_instrument_id IS NULL AND member_asset_id IS NULL)
  ),
  CHECK (expiry_time IS NULL OR expiry_time >= effective_time),
  CHECK (member_group_id IS NULL OR member_group_id <> group_id)
);
CREATE TRIGGER IF NOT EXISTS trg_gm_no_update BEFORE UPDATE ON research__group_membership
BEGIN SELECT RAISE(ABORT, 'append-only research.group_membership'); END;
CREATE TRIGGER IF NOT EXISTS trg_gm_no_delete BEFORE DELETE ON research__group_membership
BEGIN SELECT RAISE(ABORT, 'append-only research.group_membership'); END;
