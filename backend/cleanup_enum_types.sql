-- SQL Script to Clean Up PostgreSQL ENUM Types
-- Run this script to remove ENUM types and prepare for migration

-- Drop commands table if exists (will be recreated by migration)
DROP TABLE IF EXISTS commands CASCADE;

-- Drop ENUM types if they exist
DROP TYPE IF EXISTS commandstatus CASCADE;
DROP TYPE IF EXISTS commandtype CASCADE;

-- Verify cleanup
SELECT typname FROM pg_type WHERE typname IN ('commandstatus', 'commandtype');
-- Should return 0 rows

-- Check existing tables
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
