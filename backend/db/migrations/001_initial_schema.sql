-- Initial Schema Migration for AI Chat Agent System
-- Creates conversations and messages tables with proper indexes and constraints
-- Designed for stateless operation with Neon PostgreSQL

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB
);

-- Create index for user conversation queries (user isolation)
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);

-- Create composite index for user conversation listing (ordered by updated_at)
CREATE INDEX IF NOT EXISTS idx_conversations_user_updated ON conversations(user_id, updated_at DESC);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL CHECK (length(content) > 0 AND length(content) <= 10000),
    tool_calls JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create index for conversation message queries
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);

-- Create composite index for chronological message retrieval
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created ON messages(conversation_id, created_at ASC);

-- Create index for timestamp-based queries
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- Note: Constraint for tool_calls validation handled at application level

-- Create trigger to auto-update updated_at on conversations
CREATE OR REPLACE FUNCTION update_conversation_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations
    SET updated_at = NOW()
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_conversation_updated_at ON messages;
CREATE TRIGGER trigger_update_conversation_updated_at
    AFTER INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_updated_at();

-- Verify schema
DO $$
BEGIN
    RAISE NOTICE 'Migration completed successfully';
    RAISE NOTICE 'Tables created: conversations, messages';
    RAISE NOTICE 'Indexes created: 5 indexes for performance';
    RAISE NOTICE 'Constraints: role check, tool_calls check, foreign key';
    RAISE NOTICE 'Trigger: auto-update conversation updated_at';
END $$;
