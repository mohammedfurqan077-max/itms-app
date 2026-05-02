# PostgreSQL ENUM Fix - Complete Guide

## Problem

**Error**: `type 'commandstatus' does not exist`

**Root Cause**:
- Command model was using SQLAlchemy ENUM types
- PostgreSQL ENUM types are not compatible with asyncpg driver
- Database does not have ENUM types created
- asyncpg handles ENUMs differently than psycopg2

## Solution

Migrated Command model from PostgreSQL ENUM to STRING fields.

---

## Changes Made

### 1. Command Model (`app/models/command.py`)

**Before**:
```python
from sqlalchemy import Enum as SQLEnum
import enum

class CommandType(str, enum.Enum):
    SET_MODE = "set_mode"
    # ...

class CommandStatus(str, enum.Enum):
    PENDING = "pending"
    # ...

class Command(Base):
    command_type: Mapped[CommandType] = mapped_column(
        SQLEnum(CommandType),
        nullable=False
    )
    
    status: Mapped[CommandStatus] = mapped_column(
        SQLEnum(CommandStatus),
        nullable=False,
        default=CommandStatus.PENDING
    )
```

**After**:
```python
# No enum import needed

class CommandType:
    """Command type constants"""
    SET_MODE = "set_mode"
    # ...

class CommandStatus:
    """Command status constants"""
    PENDING = "pending"
    # ...

class Command(Base):
    command_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending"
    )
```

### 2. Command Service (`app/services/command_service.py`)

**Replaced all ENUM references with strings**:

```python
# Before
command.status = CommandStatus.PENDING
if command.command_type == CommandType.SET_MODE:

# After
command.status = "pending"
if command.command_type == "set_mode":
```

### 3. Command Executor (`app/services/command_executor.py`)

**Replaced all ENUM references with strings**:

```python
# Before
.where(Command.status == CommandStatus.PENDING)
command.status = CommandStatus.EXECUTING

# After
.where(Command.status == "pending")
command.status = "executing"
```

### 4. Migration File (`alembic/versions/004_add_command_model.py`)

**Already using STRING** (no changes needed):
```python
sa.Column('command_type', sa.String(length=50), nullable=False),
sa.Column('status', sa.String(length=50), nullable=False),
```

---

## Step-by-Step Fix Instructions

### Step 1: Backup Database (Optional but Recommended)
```bash
pg_dump -U postgres -d itms_db > backup_before_enum_fix.sql
```

### Step 2: Clean Up Database

**Option A: Using SQL Script**
```bash
cd backend
psql -U postgres -d itms_db -f cleanup_enum_types.sql
```

**Option B: Manual SQL**
```sql
-- Connect to database
psql -U postgres -d itms_db

-- Drop commands table
DROP TABLE IF EXISTS commands CASCADE;

-- Drop ENUM types
DROP TYPE IF EXISTS commandstatus CASCADE;
DROP TYPE IF EXISTS commandtype CASCADE;

-- Verify cleanup
SELECT typname FROM pg_type WHERE typname IN ('commandstatus', 'commandtype');
-- Should return 0 rows

-- Exit
\q
```

### Step 3: Run Migration
```bash
cd backend
python -m alembic upgrade head
```

**Expected Output**:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 003 -> 004, Add command model
```

### Step 4: Verify Tables
```bash
psql -U postgres -d itms_db -c "\dt"
```

**Expected Tables**:
```
 public | alembic_version | table | postgres
 public | commands        | table | postgres
 public | junctions       | table | postgres
 public | system_state    | table | postgres
 public | users           | table | postgres
```

### Step 5: Verify Commands Table Structure
```bash
psql -U postgres -d itms_db -c "\d commands"
```

**Expected Output**:
```
Column         | Type                     | Nullable | Default
---------------+--------------------------+----------+---------
id             | integer                  | not null |
junction_id    | integer                  |          |
command_type   | character varying(50)    | not null |
status         | character varying(50)    | not null |
payload        | text                     |          |
response       | text                     |          |
error_message  | text                     |          |
created_by     | integer                  |          |
retry_count    | integer                  | not null | 0
max_retries    | integer                  | not null | 3
created_at     | timestamp                |          | now()
executed_at    | timestamp                |          |
completed_at   | timestamp                |          |
```

### Step 6: Start Backend
```bash
cd backend
python -m uvicorn app.main:app --reload
```

**Expected Logs**:
```
INFO: Starting ITMS Backend...
INFO: CommandExecutor initialized
INFO: CommandExecutor started
INFO: Application startup complete
```

### Step 7: Test Command Creation

**Login**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@itms.com&password=admin123"
```

**Create Command**:
```bash
export TOKEN="your_token_here"

curl -X POST http://localhost:8000/api/v1/commands/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "get_status",
    "payload": {},
    "execute_immediately": false
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "command_id": 1,
  "status": "pending",
  "message": "Command queued for execution"
}
```

### Step 8: Verify Command in Database
```bash
psql -U postgres -d itms_db -c "SELECT id, command_type, status FROM commands;"
```

**Expected Output**:
```
 id | command_type | status
----+--------------+---------
  1 | get_status   | pending
```

### Step 9: Monitor Executor Logs

Watch the backend logs for command execution:
```
INFO: Found 1 pending command(s) to process
INFO: Picked command for execution: get_status
INFO: Started executing command: get_status
INFO: Command completed successfully: get_status
```

### Step 10: Verify Command Status Changed
```bash
psql -U postgres -d itms_db -c "SELECT id, command_type, status FROM commands;"
```

**Expected Output**:
```
 id | command_type | status
----+--------------+---------
  1 | get_status   | success
```

---

## Valid Values

### Command Types
- `set_mode`
- `set_time`
- `vip_mode`
- `emergency_stop`
- `heartbeat`
- `get_status`

### Command Status
- `pending` - Command created, waiting for execution
- `executing` - Command is being executed
- `success` - Command completed successfully
- `failed` - Command failed
- `timeout` - Command timed out
- `cancelled` - Command was cancelled

---

## Troubleshooting

### Problem: Migration fails with "relation already exists"

**Solution**: Drop the commands table first
```sql
DROP TABLE IF EXISTS commands CASCADE;
```

### Problem: ENUM type still exists

**Solution**: Drop ENUM types manually
```sql
DROP TYPE IF EXISTS commandstatus CASCADE;
DROP TYPE IF EXISTS commandtype CASCADE;
```

### Problem: Commands not being executed

**Solution**: Check executor logs
```bash
# Look for "CommandExecutor started" in logs
# If not present, restart backend
```

### Problem: "Invalid command type" error

**Solution**: Use lowercase string values
```json
{
  "command_type": "get_status"  // ✓ Correct
}
```

NOT:
```json
{
  "command_type": "GET_STATUS"  // ✗ Wrong
}
```

---

## Verification Checklist

- [ ] Database cleaned (no ENUM types)
- [ ] Migration ran successfully
- [ ] Commands table created with STRING fields
- [ ] Backend starts without errors
- [ ] Executor started successfully
- [ ] Command created via API
- [ ] Command status = "pending" in database
- [ ] Executor picked up command (check logs)
- [ ] Command status changed to "success"
- [ ] No ENUM-related errors in logs

---

## Summary

✅ **Fixed Issues**:
- Removed all PostgreSQL ENUM usage
- Migrated to STRING fields
- Updated all queries to use string values
- Migration file already correct
- All services updated

✅ **Benefits**:
- Compatible with asyncpg driver
- No ENUM type management needed
- Simpler database schema
- Easier to add new command types/statuses
- Better compatibility across PostgreSQL versions

✅ **No Breaking Changes**:
- API remains the same
- Command types still validated
- Status values unchanged
- All functionality preserved

The system is now fully compatible with asyncpg and PostgreSQL without ENUM types!
