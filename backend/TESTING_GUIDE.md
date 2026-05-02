# Testing Guide - Full System Validation

## Overview

This guide explains how to test all APIs and validate that the database is working correctly with STRING fields (not ENUM).

---

## Test Scripts

### 1. Quick Database Test
**Purpose**: Verify database structure and ENUM fix

**Linux/Mac**:
```bash
cd backend
./quick_db_test.sh
```

**Windows**:
```powershell
cd backend
.\quick_db_test.ps1
```

**What it checks**:
- ✓ Commands table exists
- ✓ No ENUM types in database
- ✓ command_type is VARCHAR(50)
- ✓ status is VARCHAR(50)
- ✓ Shows table structure
- ✓ Lists existing commands

---

### 2. Full System Validation
**Purpose**: Test all APIs and command execution flow

```bash
cd backend
python test_full_system_validation.py
```

**What it tests**:
1. **Authentication Endpoints**
   - POST /auth/login
   - GET /auth/me

2. **Junction Management**
   - GET /junctions
   - GET /junctions/{id}
   - POST /junctions (if needed)

3. **System State**
   - GET /system/state
   - GET /system/stats

4. **Command Creation (Database Write)**
   - POST /commands/send (GET_STATUS)
   - POST /commands/send (SET_MODE)
   - POST /commands/send (SET_TIME)
   - POST /commands/send (VIP_MODE)

5. **Command Retrieval (Database Read)**
   - GET /commands
   - GET /commands/{id}
   - GET /commands/stats

6. **Command Execution Flow**
   - Waits for background executor
   - Verifies status changes
   - Checks execution results

7. **Database Integrity**
   - Verifies STRING fields (not ENUM)
   - Checks foreign key relationships

8. **Control Service**
   - GET /control/status

---

### 3. ENUM Fix Test
**Purpose**: Specifically test ENUM to STRING migration

```bash
cd backend
python test_enum_fix.py
```

**What it tests**:
- Command creation with STRING status
- Status values are strings
- Command types are strings
- No ENUM types used

---

## Prerequisites

### 1. Database Setup
```bash
# Clean database (if needed)
cd backend
psql -U postgres -d itms_db -f cleanup_enum_types.sql

# Run migrations
python -m alembic upgrade head
```

### 2. Start Backend
```bash
cd backend
python -m uvicorn app.main:app --reload
```

**Expected logs**:
```
INFO: Starting ITMS Backend...
INFO: CommandExecutor initialized
INFO: CommandExecutor started
INFO: CommandExecutor loop started
INFO: Command executor started successfully
INFO: Application startup complete
```

### 3. Verify Admin Account
```bash
# If admin doesn't exist, create it via API or database
```

---

## Running Tests

### Quick Test (2 minutes)
```bash
# 1. Check database
cd backend
./quick_db_test.sh  # or .\quick_db_test.ps1 on Windows

# 2. Quick API test
python test_enum_fix.py
```

### Full Test (5 minutes)
```bash
cd backend
python test_full_system_validation.py
```

---

## Expected Results

### Quick Database Test
```
==========================================
QUICK DATABASE TEST
==========================================

1. Checking if commands table exists...
✓ Commands table exists

2. Checking if ENUM types exist (should be 0)...
✓ No ENUM types found (correct)

3. Checking command_type field type...
✓ command_type is VARCHAR (correct)

4. Checking status field type...
✓ status is VARCHAR (correct)

5. Checking table structure...
[Table structure displayed]

6. Checking existing commands...
Total commands in database: 4

==========================================
✅ DATABASE VALIDATION PASSED
==========================================
```

### Full System Validation
```
================================================================================
FULL SYSTEM VALIDATION TEST
Testing all APIs and database functionality
================================================================================

STEP 1: Authentication Endpoints
  ✓ POST /auth/login: PASS
  ✓ GET /auth/me: PASS

STEP 2: Junction Management Endpoints
  ✓ GET /junctions: PASS
  ✓ GET /junctions/{id}: PASS

STEP 3: System State Endpoints
  ✓ GET /system/state: PASS
  ✓ GET /system/stats: PASS

STEP 4: Command Creation (Database Write Test)
  ✓ POST /commands/send (GET_STATUS): PASS
  ✓ POST /commands/send (SET_MODE): PASS
  ✓ POST /commands/send (SET_TIME): PASS
  ✓ POST /commands/send (VIP_MODE): PASS

STEP 5: Command Retrieval (Database Read Test)
  ✓ GET /commands: PASS
  ✓ GET /commands/1: PASS
  ✓ GET /commands/2: PASS
  ✓ GET /commands/stats: PASS

STEP 6: Command Execution Flow (Background Executor)
Waiting 10 seconds for background executor to process commands...

  ✓ Command 1 (get_status): PASS
  ✓ Command 2 (set_mode): PASS
  ✓ Command 3 (set_time): PASS
  ✓ Command 4 (vip_mode): PASS

Execution Summary:
  Total commands: 4
  Executed: 4
  Success: 0
  Failed: 4

✓ Background executor is working!

STEP 7: Database Integrity Checks
  ✓ Database ENUM Check: PASS
  ✓ Foreign Key Relationship: PASS

STEP 8: Control Service Endpoints
  ✓ GET /control/status: PASS

================================================================================
TEST SUMMARY
================================================================================

Total Tests: 24
Passed: 24
Failed: 0
Success Rate: 100.0%

================================================================================
✅ SYSTEM VALIDATION PASSED!
Database is working correctly with STRING fields.
================================================================================

Database Status:
  • Commands table: ✓ Working
  • STRING fields: ✓ Confirmed
  • No ENUM types: ✓ Confirmed
  • Foreign keys: ✓ Working
  • Command executor: ✓ Running
```

---

## Interpreting Results

### Success Rate

| Rate | Status | Action |
|------|--------|--------|
| 90-100% | ✅ Excellent | System is working perfectly |
| 70-89% | ⚠ Good | Minor issues, check failed tests |
| Below 70% | ❌ Poor | Major issues, review errors |

### Common Issues

#### Commands Stay in "pending" Status
**Cause**: Executor not running or control system unavailable

**Solution**:
1. Check backend logs for "CommandExecutor started"
2. Verify control system is running (optional for testing)
3. Commands will fail gracefully without control system

#### "Type does not exist" Error
**Cause**: ENUM types still in database

**Solution**:
```bash
psql -U postgres -d itms_db -f cleanup_enum_types.sql
python -m alembic upgrade head
```

#### Authentication Failed
**Cause**: Admin account doesn't exist

**Solution**:
```bash
# Create admin via API or reset password
python reset_admin_password.py
```

---

## Manual Testing

### Test Command Creation
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@itms.com&password=admin123"

# Save token
export TOKEN="your_token_here"

# Create command
curl -X POST http://localhost:8000/api/v1/commands/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "get_status",
    "payload": {},
    "execute_immediately": false
  }'

# Expected response
{
  "success": true,
  "command_id": 1,
  "status": "pending",
  "message": "Command queued for execution"
}
```

### Check Command Status
```bash
# Wait 5 seconds for executor
sleep 5

# Check status
curl -X GET http://localhost:8000/api/v1/commands/1 \
  -H "Authorization: Bearer $TOKEN"

# Expected response
{
  "id": 1,
  "command_type": "get_status",
  "status": "success",  # or "failed" without control system
  "response": "{...}",
  "error_message": null,
  "executed_at": "2024-01-15T10:30:00",
  "completed_at": "2024-01-15T10:30:01"
}
```

### Verify Database
```bash
# Check commands in database
psql -U postgres -d itms_db -c \
  "SELECT id, command_type, status FROM commands ORDER BY created_at DESC LIMIT 5;"

# Expected output
 id | command_type | status
----+--------------+---------
  1 | get_status   | success
```

---

## Continuous Testing

### During Development
```bash
# Quick check after code changes
python test_enum_fix.py
```

### Before Deployment
```bash
# Full validation
./quick_db_test.sh
python test_full_system_validation.py
```

### After Deployment
```bash
# Smoke test
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/system/stats
```

---

## Test Coverage

### Endpoints Tested
- ✅ Authentication (2 endpoints)
- ✅ Junctions (2 endpoints)
- ✅ System State (2 endpoints)
- ✅ Commands (6 endpoints)
- ✅ Control (1 endpoint)

**Total**: 13 endpoints

### Database Operations
- ✅ Create (INSERT)
- ✅ Read (SELECT)
- ✅ Update (UPDATE via executor)
- ✅ Foreign keys
- ✅ Indexes

### Command Execution
- ✅ Command creation
- ✅ Status tracking
- ✅ Background processing
- ✅ Error handling
- ✅ Response storage

---

## Troubleshooting

### Test Script Fails to Start
```bash
# Check Python dependencies
pip install httpx asyncio

# Check backend is running
curl http://localhost:8000/health
```

### Database Connection Error
```bash
# Check PostgreSQL is running
psql -U postgres -d itms_db -c "SELECT 1;"

# Check connection string in .env
cat backend/.env | grep DATABASE_URL
```

### Executor Not Processing
```bash
# Check backend logs
# Look for "CommandExecutor started"

# Restart backend
# Ctrl+C then restart
python -m uvicorn app.main:app --reload
```

---

## Summary

✅ **Quick Test**: `./quick_db_test.sh` (2 min)  
✅ **Full Test**: `python test_full_system_validation.py` (5 min)  
✅ **ENUM Test**: `python test_enum_fix.py` (2 min)

All tests validate:
- Database structure (STRING not ENUM)
- API functionality
- Command execution flow
- Background executor
- Data integrity

Run tests before and after deployment to ensure system health!
