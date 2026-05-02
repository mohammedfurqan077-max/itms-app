# Command Executor - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Start the Backend
```bash
cd backend
python -m uvicorn app.main:app --reload
```

**Expected Output**:
```
INFO: Starting ITMS Backend...
INFO: CommandExecutor initialized
INFO: CommandExecutor started
INFO: CommandExecutor loop started
INFO: Command executor started successfully
INFO: Application startup complete
```

✅ If you see "Command executor started successfully", the system is ready!

---

### Step 2: Login and Get Token
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@itms.com&password=admin123"
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Save the token**:
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### Step 3: Create Your First Command
```bash
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

**Response**:
```json
{
  "success": true,
  "command_id": 1,
  "status": "pending",
  "message": "Command queued for execution"
}
```

✅ Command created! The background executor will pick it up within 2 seconds.

---

### Step 4: Check Command Status
```bash
# Replace 1 with your command_id
curl -X GET http://localhost:8000/api/v1/commands/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Response (After ~2 seconds)**:
```json
{
  "id": 1,
  "junction_id": 1,
  "command_type": "get_status",
  "status": "success",
  "response": "{\"success\": true, \"data\": {...}}",
  "error_message": null,
  "executed_at": "2024-01-15T10:30:00",
  "completed_at": "2024-01-15T10:30:01"
}
```

✅ Command executed successfully!

---

### Step 5: Run Full Test Suite
```bash
cd backend
python test_command_executor.py
```

**Expected Output**:
```
================================================================================
COMMAND EXECUTOR SYSTEM TEST
================================================================================

STEP 1: Login as admin
✓ Login successful

STEP 2: Test Background Command Execution
1. Creating command: GET_STATUS
   ✓ Command created: ID=1, Status=pending

...

STEP 4: Test Summary
Total Commands: 5
Successful: 5
Failed: 0
Success Rate: 100.0%
```

✅ All tests passed!

---

## 📋 Command Types Cheat Sheet

### 1. Get Status
```bash
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

### 2. Set Mode
```bash
curl -X POST http://localhost:8000/api/v1/commands/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "set_mode",
    "payload": {"mode": "auto_circle"},
    "execute_immediately": false
  }'
```

**Valid modes**: `manual`, `auto_circle`, `auto_jump`, `blinker`, `vip`

### 3. Set Manual Times
```bash
curl -X POST http://localhost:8000/api/v1/commands/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "set_time",
    "payload": {
      "lane1": 30,
      "lane2": 45,
      "lane3": 30,
      "lane4": 45
    },
    "execute_immediately": false
  }'
```

### 4. VIP Mode (Activate)
```bash
curl -X POST http://localhost:8000/api/v1/commands/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "vip_mode",
    "payload": {
      "active": true,
      "lanes_to_green": [1, 2]
    },
    "execute_immediately": false
  }'
```

### 5. VIP Mode (Deactivate)
```bash
curl -X POST http://localhost:8000/api/v1/commands/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "vip_mode",
    "payload": {
      "active": false
    },
    "execute_immediately": false
  }'
```

### 6. Emergency Stop
```bash
curl -X POST http://localhost:8000/api/v1/commands/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "emergency_stop",
    "payload": {},
    "execute_immediately": false
  }'
```

---

## 🔍 Monitoring

### Watch Logs in Real-Time
```bash
# In the terminal where backend is running
# You'll see:
INFO: Found 1 pending command(s) to process
INFO: Picked command for execution: get_status
INFO: Started executing command: get_status
INFO: Command completed successfully: get_status
```

### Check All Commands
```bash
curl -X GET "http://localhost:8000/api/v1/commands?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Statistics
```bash
curl -X GET http://localhost:8000/api/v1/commands/stats \
  -H "Authorization: Bearer $TOKEN"
```

---

## ⚙️ Configuration

### Change Poll Interval
Edit `backend/app/services/command_executor.py`:
```python
executor = CommandExecutor(poll_interval=5)  # Poll every 5 seconds
```

### Change Batch Size
Edit `backend/app/services/command_executor.py` in `_process_pending_commands()`:
```python
.limit(200)  # Process up to 200 commands per iteration
```

### Change Control System URL
Edit `backend/.env`:
```
CONTROL_SYSTEM_URL=http://192.168.1.100:5000
```

---

## 🐛 Troubleshooting

### Problem: Commands stay in PENDING status
**Solution**: Check if executor started successfully in logs

### Problem: Commands fail with "Connection refused"
**Solution**: Control system is not running. This is normal in development without hardware.

### Problem: "Junction not found" error
**Solution**: Create a junction first:
```bash
curl -X POST http://localhost:8000/api/v1/junctions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Main Junction",
    "location": "City Center",
    "ip_address": "192.168.1.100",
    "status": "active"
  }'
```

---

## 📚 Next Steps

1. **Read Full Documentation**: `backend/COMMAND_EXECUTOR_GUIDE.md`
2. **See Examples**: `backend/COMMAND_EXECUTOR_EXAMPLES.md`
3. **View Implementation**: `COMMAND_EXECUTOR_COMPLETE.md`

---

## ✅ Success Checklist

- [ ] Backend started successfully
- [ ] Executor started (check logs)
- [ ] Login successful (got token)
- [ ] Created first command
- [ ] Command status changed to SUCCESS
- [ ] Test script passed

If all checked, you're ready to use the Command Executor System! 🎉
