-- Migration: Rename metadata to extra_data to avoid SQLAlchemy reserved word conflict
-- Version: 004
-- Date: 2026-02-10

-- Rename metadata column in conversations table
ALTER TABLE conversations
RENAME COLUMN metadata TO extra_data;

-- Rename metadata column in messages table
ALTER TABLE messages
RENAME COLUMN metadata TO extra_data;

-- Add comments for documentation
COMMENT ON COLUMN conversations.extra_data IS 'Additional metadata stored as JSON (renamed from metadata to avoid SQLAlchemy conflicts)';
COMMENT ON COLUMN messages.extra_data IS 'Additional metadata stored as JSON (renamed from metadata to avoid SQLAlchemy conflicts)';

-- Verify migration
DO $$
BEGIN
    RAISE NOTICE 'Migration 004 completed successfully';
    RAISE NOTICE 'Renamed conversations.metadata -> conversations.extra_data';
    RAISE NOTICE 'Renamed messages.metadata -> messages.extra_data';
END $$;
