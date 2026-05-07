-- Cleanup script to remove all PostgreSQL ENUM types
-- Run this if you have existing ENUM types in your database

-- Drop all tables that might have ENUM dependencies
DROP TABLE IF EXISTS commands CASCADE;
DROP TABLE IF EXISTS system_state CASCADE;
DROP TABLE IF EXISTS junctions CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS user_permissions CASCADE;
DROP TABLE IF EXISTS permissions CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop all ENUM types
DROP TYPE IF EXISTS commandstatus CASCADE;
DROP TYPE IF EXISTS commandtype CASCADE;
DROP TYPE IF EXISTS junctionstatus CASCADE;
DROP TYPE IF EXISTS userstatus CASCADE;
DROP TYPE IF EXISTS userrole CASCADE;

-- Drop alembic version table to start fresh
DROP TABLE IF EXISTS alembic_version CASCADE;

-- Verify all ENUM types are gone
SELECT typname FROM pg_type WHERE typtype = 'e';
