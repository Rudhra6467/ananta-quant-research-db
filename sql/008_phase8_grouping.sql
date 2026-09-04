-- Phase 8 grouping contracts. Identity + temporal membership only. No ingest, no aggregation.
CREATE TABLE IF NOT EXISTS research.market_group (
  id uuid PRIMARY KEY,
  code text NOT NULL UNIQUE,
  name text NOT NULL,
  kind text NOT NULL CHECK (kind IN ('market', 'asset_class', 'sector', 'category', 'group')),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS research.group_membership (
  id uuid PRIMARY KEY,
  group_id uuid NOT NULL REFERENCES research.market_group(id),
  member_kind text NOT NULL CHECK (member_kind IN ('instrument', 'asset', 'group')),
  member_instrument_id uuid REFERENCES ref.instrument(id),
  member_asset_id uuid REFERENCES ref.asset(id),
  member_group_id uuid REFERENCES research.market_group(id),
  effective_time timestamptz NOT NULL,
  expiry_time timestamptz,
  knowledge_time timestamptz NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (
    (member_kind = 'instrument' AND member_instrument_id IS NOT NULL AND member_asset_id IS NULL AND member_group_id IS NULL)
    OR (member_kind = 'asset' AND member_asset_id IS NOT NULL AND member_instrument_id IS NULL AND member_group_id IS NULL)
    OR (member_kind = 'group' AND member_group_id IS NOT NULL AND member_instrument_id IS NULL AND member_asset_id IS NULL)
  ),
  CHECK (expiry_time IS NULL OR expiry_time >= effective_time),
  CHECK (member_group_id IS NULL OR member_group_id <> group_id)
);

CREATE INDEX IF NOT EXISTS group_membership_group_time_idx
  ON research.group_membership (group_id, effective_time, knowledge_time);

INSERT INTO ops.schema_gate (id, phase, approved, ingestion_enabled, notes)
VALUES (gen_random_uuid(), 'phase8', true, false, 'Grouping identity and temporal membership only. INGESTION_ENABLED remains false.')
ON CONFLICT (phase) DO UPDATE SET approved = true, ingestion_enabled = false;
