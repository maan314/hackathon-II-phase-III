-- Migration: Create tasks table for MCP Task Management System
-- Feature: 3-mcp-task-tools
-- Date: 2026-02-09
-- Purpose: Add tasks table with user isolation and performance indexes

-- Create tasks table
-- This table stores todo items for users, accessed exclusively through MCP tools
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(200) NOT NULL CHECK (length(title) >= 1),
    description TEXT CHECK (description IS NULL OR length(description) <= 2000),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed')),
    due_date TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create index for user task queries (user isolation)
-- This index enables fast filtering of tasks by user_id
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);

-- Create index for chronological ordering
-- This index enables fast sorting by creation date
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);

-- Create composite index for filtered queries
-- This index optimizes queries like "list pending tasks for user"
CREATE INDEX IF NOT EXISTS idx_tasks_user_status ON tasks(user_id, status);

-- Create composite index for user task listing with ordering
-- This index optimizes the most common query pattern: list user's tasks by date
CREATE INDEX IF NOT EXISTS idx_tasks_user_created ON tasks(user_id, created_at DESC);

-- Create trigger function to auto-update updated_at timestamp
-- This ensures updated_at is always current without manual updates
CREATE OR REPLACE FUNCTION update_tasks_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to call the update function before each update
DROP TRIGGER IF EXISTS update_tasks_updated_at_trigger ON tasks;
CREATE TRIGGER update_tasks_updated_at_trigger
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_tasks_updated_at();

-- Add comment to table for documentation
COMMENT ON TABLE tasks IS 'Task management table for MCP tools - stores user todo items with user isolation';
COMMENT ON COLUMN tasks.user_id IS 'User identifier - all queries MUST filter by this for user isolation';
COMMENT ON COLUMN tasks.status IS 'Task status - must be pending or completed';
COMMENT ON COLUMN tasks.created_at IS 'Auto-generated timestamp - immutable';
COMMENT ON COLUMN tasks.updated_at IS 'Auto-updated timestamp via trigger';
