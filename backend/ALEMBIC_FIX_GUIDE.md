# Alembic Migration Fix - ENUM Duplication Issue

## Problem

When running the migration `004_add_command_model.py`, PostgreSQL throws an error:
```
ERROR: type "commandtype" already exists
ERROR: type "commandstatus" already exists
```

This happens when:
1. Migration was partially run before
2. ENUMs were created but table creation failed
3. Trying to re-run the migration

---

## Solution Applied

The migration has been fixed to be **idempotent** (can run multiple times safely).

### Changes Made

#### 1. ENUM Creation with Error Handling
**Before:**
```sql
CREATE TYPE commandtype AS ENUM (...)
```

**After:**
```sql
DO $$ BEGIN
    CREATE TYPE commandtype AS ENUM (...);
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
```

This uses PostgreSQL's exception handling to:
- Try to create the ENUM
- If it already exists, silently ignore the error
- Continue with the migration

#### 2. Table Creation with Check
**Before:**
```python
op.create_table('commands', ...)
```

**After:**
```python
connection = op.get_bind()
inspector = sa.inspect(connection)

if 'commands' not in inspector.get_table_names():
    op.create_table('commands', ...)
```

This checks if the table exists before creating it.

#### 3. ENUM Reference with `create_type=False`
**Before:**
```python
sa.Enum(..., name='commandtype')
```

**After:**
```python
sa.Enum(..., name='commandtype', create_type=False)
```

This tells SQLAlchemy to use the existing ENUM type instead of trying to create it.

#### 4. Safe Downgrade
**Before:**
```python
op.drop_index('idx_command_type_status', table_name='commands')
```

**After:**
```python
if 'commands' in inspector.get_table_names():
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('commands')]
    if 'idx_command_type_status' in existing_indexes:
        op.drop_index('idx_command_type_status', table_name='commands')
```

This checks if table and indexes exist before dropping them.

---

## How to Use

### If Migration Failed Previously

#### Option 1: Clean Slate (Recommended for Development)

```bash
# 1. Drop the ENUMs manually
psql -U postgres -d itms_db -c "DROP TYPE IF EXISTS commandtype CASCADE;"
psql -U postgres -d itms_db -c "DROP TYPE IF EXISTS commandstatus CASCADE;"

# 2. Drop the table if it exists
psql -U postgres -d itms_db -c "DROP TABLE IF EXISTS commands CASCADE;"

# 3. Run migration again
cd backend
alembic upgrade head
```

#### Option 2: Use Fixed Migration (Works with Existing ENUMs)

```bash
# Just run the migration - it will handle existing ENUMs
cd backend
alembic upgrade head
```

The fixed migration will:
- Skip ENUM creation if they already exist
- Skip table creation if it already exists
- Create only what's missing

---

### Fresh Installation

```bash
# Run all migrations
cd backend
alembic upgrade head
```

The migration will work correctly on a fresh database.

---

## Verification

### Check Current Migration Version
```bash
cd backend
alembic current
```

**Expected Output:**
```
004 (head)
```

### Check ENUMs Exist
```bash
psql -U postgres -d itms_db -c "\dT+ commandtype"
psql -U postgres -d itms_db -c "\dT+ commandstatus"
```

**Expected Output:**
```
List of data types
 Schema |     Name      | Internal name | Size | Elements | Access privileges | Description 
--------+---------------+---------------+------+----------+-------------------+-------------
 public | commandtype   | commandtype   | 4    | set_mode +|                   | 
        |               |               |      | set_time +|                   | 
        |               |               |      | vip_mode +|                   | 
        |               |               |      | ...       |                   | 
```

### Check Table Exists
```bash
psql -U postgres -d itms_db -c "\d commands"
```

**Expected Output:**
```
Table "public.commands"
    Column     |            Type             | Collation | Nullable | Default 
---------------+-----------------------------+-----------+----------+---------
 id            | integer                     |           | not null | 
 junction_id   | integer                     |           |          | 
 command_type  | commandtype                 |           | not null | 
 status        | commandstatus               |           | not null | 
 ...
```

### Check Indexes
```bash
psql -U postgres -d itms_db -c "\d commands" | grep "Indexes:"
```

**Expected Output:**
```
Indexes:
    "commands_pkey" PRIMARY KEY, btree (id)
    "ix_commands_id" btree (id)
    "ix_commands_junction_id" btree (junction_id)
    "ix_commands_command_type" btree (command_type)
    "ix_commands_status" btree (status)
    "ix_commands_created_by" btree (created_by)
    "ix_commands_created_at" btree (created_at)
    "idx_command_junction_status" btree (junction_id, status)
    "idx_command_type_status" btree (command_type, status)
```

---

## Troubleshooting

### Issue: "relation 'commands' already exists"

**Cause:** Table was created but migration wasn't marked as complete.

**Solution:**
```bash
# Mark migration as complete without running it
alembic stamp 004
```

### Issue: "type 'commandtype' already exists"

**Cause:** Using old migration file.

**Solution:**
1. Ensure you're using the fixed migration file
2. Or drop the ENUMs and re-run:
```bash
psql -U postgres -d itms_db -c "DROP TYPE IF EXISTS commandtype CASCADE;"
psql -U postgres -d itms_db -c "DROP TYPE IF EXISTS commandstatus CASCADE;"
alembic upgrade head
```

### Issue: "cannot drop type commandtype because other objects depend on it"

**Cause:** Table is using the ENUM.

**Solution:**
```bash
# Drop table first, then ENUMs
psql -U postgres -d itms_db -c "DROP TABLE IF EXISTS commands CASCADE;"
psql -U postgres -d itms_db -c "DROP TYPE IF EXISTS commandtype CASCADE;"
psql -U postgres -d itms_db -c "DROP TYPE IF EXISTS commandstatus CASCADE;"
alembic upgrade head
```

### Issue: Migration hangs or times out

**Cause:** Database lock or connection issue.

**Solution:**
```bash
# Check for locks
psql -U postgres -d itms_db -c "SELECT * FROM pg_locks WHERE NOT granted;"

# Kill blocking queries if needed
psql -U postgres -d itms_db -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'itms_db' AND pid <> pg_backend_pid();"

# Try again
alembic upgrade head
```

---

## Testing the Fix

### Test 1: Fresh Database
```bash
# Drop and recreate database
dropdb itms_db
createdb itms_db

# Run migrations
cd backend
alembic upgrade head

# Verify
alembic current
# Should show: 004 (head)
```

### Test 2: Idempotency (Run Twice)
```bash
# Run migration
alembic upgrade head

# Run again (should not error)
alembic downgrade 003
alembic upgrade head

# Verify
alembic current
# Should show: 004 (head)
```

### Test 3: Partial State Recovery
```bash
# Create ENUMs manually
psql -U postgres -d itms_db -c "CREATE TYPE commandtype AS ENUM ('set_mode', 'set_time', 'vip_mode', 'emergency_stop', 'heartbeat', 'get_status');"

# Run migration (should not error)
alembic upgrade head

# Verify
alembic current
# Should show: 004 (head)
```

---

## Key Improvements

### ✅ Idempotent
- Can run multiple times without errors
- Checks for existing objects before creating

### ✅ Safe
- Won't fail if ENUMs already exist
- Won't fail if table already exists
- Won't fail if indexes already exist

### ✅ Recoverable
- Can recover from partial migration failures
- Can handle manual ENUM creation
- Can handle manual table creation

### ✅ Production-Ready
- Safe for production deployments
- No data loss on re-run
- Proper error handling

---

## Summary

**Problem:** ENUM duplication causing migration failures

**Solution:** 
1. Use PostgreSQL exception handling for ENUM creation
2. Check table existence before creation
3. Use `create_type=False` for ENUM references
4. Safe downgrade with existence checks

**Result:** Migration is now idempotent and safe to run multiple times

---

## Quick Commands

```bash
# Clean slate (development)
psql -U postgres -d itms_db -c "DROP TYPE IF EXISTS commandtype CASCADE;"
psql -U postgres -d itms_db -c "DROP TYPE IF EXISTS commandstatus CASCADE;"
psql -U postgres -d itms_db -c "DROP TABLE IF EXISTS commands CASCADE;"
alembic upgrade head

# Or just run (with fixed migration)
alembic upgrade head

# Verify
alembic current
psql -U postgres -d itms_db -c "\d commands"
```

---

**Status:** Migration fixed and tested ✅
