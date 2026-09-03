-- Phase 2 foundation contracts only. No new operational domains implemented.

CREATE SCHEMA IF NOT EXISTS world;
CREATE SCHEMA IF NOT EXISTS prediction;
CREATE SCHEMA IF NOT EXISTS portfolio;

ALTER TABLE ref.asset DROP CONSTRAINT IF EXISTS asset_symbol_key;
ALTER TABLE ref.asset DROP CONSTRAINT IF EXISTS uq_asset_symbol;
ALTER TABLE ref.asset DROP CONSTRAINT IF EXISTS uq_asset_symbol_key;
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conrelid = 'ref.asset'::regclass AND contype = 'u'
      AND pg_get_constraintdef(oid) ILIKE '%(symbol)%'
      AND pg_get_constraintdef(oid) NOT ILIKE '%asset_class%'
  ) THEN
    EXECUTE (
      SELECT format('ALTER TABLE ref.asset DROP CONSTRAINT %I', conname)
      FROM pg_constraint
      WHERE conrelid = 'ref.asset'::regclass AND contype = 'u'
        AND pg_get_constraintdef(oid) ILIKE '%(symbol)%'
        AND pg_get_constraintdef(oid) NOT ILIKE '%asset_class%'
      LIMIT 1
    );
  END IF;
END$$;
ALTER TABLE ref.asset ADD CONSTRAINT uq_asset_class_symbol UNIQUE (asset_class, symbol);

ALTER TABLE ref.instrument ALTER COLUMN quote_asset_id DROP NOT NULL;

ALTER TABLE research.relationship_evidence DROP CONSTRAINT IF EXISTS evidence_direction;
ALTER TABLE research.relationship_evidence DROP CONSTRAINT IF EXISTS ck_relationship_evidence_evidence_direction;
ALTER TABLE research.relationship_evidence
  ADD CONSTRAINT ck_relationship_evidence_evidence_direction
  CHECK (direction in ('untested','supports','contradicts','inconclusive','invalidated','decayed'));
