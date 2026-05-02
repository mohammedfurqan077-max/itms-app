# ENUM Fix - Quick Reference Card

## 🚨 Problem
```
ERROR: type 'commandstatus' does not exist
```

## ✅ Solution
Migrated from PostgreSQL ENUM to STRING fields.

---

## 🔧 Quick Fix (3 Steps)

### 1. Clean Database
```bash
cd backend
psql -U postgres -d itms_db -f cleanup_enum_types.sql
```

### 2. Run Migration
```bash
python -m alembic upgrade head
```

### 3. Start & Test
```bash
# Terminal 1: Start backend
python -m uvicorn app.main:app --reload

# Terminal 2: Run test
python test_enum_fix.py
```

---

## 📝 What Changed

| Before (ENUM) | After (STRING) |
|---------------|----------------|
| `CommandStatus.PENDING` | `"pending"` |
| `CommandStatus.EXECUTING` | `"executing"` |
| `CommandStatus.SUCCESS` | `"success"` |
| `CommandType.SET_MODE` | `"set_mode"` |
| `CommandType.GET_STATUS` | `"get_status"` |

---

## 🎯 Valid Values

### Command Types
```
"set_mode"
"set_time"
"vip_mode"
"emergency_stop"
"heartbeat"
"get_status"
```

### Status Values
```
"pending"      → Created, waiting
"executing"    → Currently running
"success"      → Completed successfully
"failed"       → Failed to execute
"timeout"      → Execution timed out
"cancelled"    → Manually cancelled
```

---

## 🧪 Test Command

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=admin@itms.com&password=admin123"

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

# Expected: {"success": true, "command_id": 1, "status": "pending"}
```

---

## ✅ Verification Checklist

```bash
# 1. No ENUM types
psql -U postgres -d itms_db -c \
  "SELECT typname FROM pg_type WHERE typname IN ('commandstatus', 'commandtype');"
# Expected: 0 rows

# 2. Commands table exists
psql -U postgres -d itms_db -c "\dt commands"
# Expected: Table exists

# 3. Correct field types
psql -U postgres -d itms_db -c "\d commands"
# Expected: command_type and status are VARCHAR(50)

# 4. Backend starts
python -m uvicorn app.main:app --reload
# Expected: "CommandExecutor started"

# 5. Test passes
python test_enum_fix.py
# Expected: "All tests passed!"
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Migration fails | Run cleanup script first |
| ENUM still exists | `DROP TYPE commandstatus CASCADE;` |
| Commands not executing | Check executor logs |
| "Invalid command type" | Use lowercase strings |

---

## 📚 Documentation

- **Complete Guide**: `backend/ENUM_FIX_GUIDE.md`
- **Summary**: `ENUM_FIX_COMPLETE.md`
- **Test Script**: `backend/test_enum_fix.py`
- **Cleanup SQL**: `backend/cleanup_enum_types.sql`

---

## 🎉 Success Indicators

✅ Backend starts without errors  
✅ "CommandExecutor started" in logs  
✅ Commands created with status="pending"  
✅ Executor processes commands  
✅ Status changes to "success"  
✅ No ENUM errors in logs  

---

**Status**: ✅ Fixed  
**Time to Fix**: ~5 minutes  
**Breaking Changes**: None
