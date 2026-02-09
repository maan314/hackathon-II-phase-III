-- Migration: Create conversations and messages tables for AI Chat Agent
-- Version: 003
-- Date: 2026-02-09

-- Drop existing tables if they exist (safe since they're empty)
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;

-- Create conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB
);

-- Create indexes for conversations table
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);

-- Create messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    tool_calls JSONB,
    metadata JSONB
);

-- Create indexes for messages table
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp DESC);

-- Add comments for documentation
COMMENT ON TABLE conversations IS 'Stores conversation threads between users and AI agent';
COMMENT ON TABLE messages IS 'Stores individual messages within conversations';
COMMENT ON COLUMN conversations.user_id IS 'User identifier from JWT token';
COMMENT ON COLUMN conversations.title IS 'Auto-generated from first message or user-provided';
COMMENT ON COLUMN messages.role IS 'Message sender: user or assistant';
COMMENT ON COLUMN messages.tool_calls IS 'JSON array of tool invocations made by agent';
