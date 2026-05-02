# Command Executor - Examples and Logs

## Example 1: Successful Command Execution

### Create Command
```bash
curl -X POST http://localhost:8000/api/v1/commands/send \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "set_mode",
    "payload": {"mode": "auto_circle"},
    "execute_immediately": false
  }'
```

### Response
```json
{
  "success": true,
  "command_id": 123,
  "status": "pending",
  "message": "Command queued for execution"
}
```

### Executor Logs
```
[2024-01-15 10:30:00] INFO: Found 1 pending command(s) to process

[2024-01-15 10:30:00] INFO: Picked command for execution: set_mode
  command_id: 123
  command_type: set_mode
  junction_id: 1
  created_at: 2024-01-15T10:29:58

[2024-01-15 10:30:00] INFO: Started executing command: set_mode
  command_id: 123
  command_type: set_mode

[2024-01-15 10:30:00] INFO: Switching mode to: auto_circle

[2024-01-15 10:30:00] INFO: Control request: POST http://localhost:5000/switch_mode
  data: {"mode": "auto_circle"}

[2024-01-15 10:30:00] INFO: Control request successful: POST /switch_mode
  status_code: 200

[2024-01-15 10:30:00] INFO: Command completed successfully: set_mode
  command_id: 123
  command_type: set_mode
  response: {
    "success": true,
    "message": "Request successful",
    "data": {"mode": "auto_circle", "status": "active"},
    "status_code": 200
  }
```

### Check Command Status
```bash
curl -X GET http://localhost:8000/api/v1/commands/123 \
  -H "Authorization: Bearer eyJhbGc..."
```

### Response
```json
{
  "id": 123,
  "junction_id": 1,
  "command_type": "set_mode",
  "payload": "{\"mode\": \"auto_circle\"}",
  "status": "success",
  "response": "{\"success\": true, \"message\": \"Request successful\", ...}",
  "error_message": null,
  "created_by": 1,
  "retry_count": 0,
  "max_retries": 3,
  "created_at": "2024-01-15T10:29:58",
  "executed_at": "2024-01-15T10:30:00",
  "completed_at": "2024-01-15T10:30:00"
}
```

---

## Example 2: Failed Command (Control System Unreachable)

### Create Command
```bash
curl -X POST http://localhost:8000/api/v1/commands/send \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "get_status",
    "payload": {},
    "execute_immediately": false
  }'
```

### Response
```json
{
  "success": true,
  "command_id": 124,
  "status": "pending",
  "message": "Command queued for execution"
}
```

### Executor Logs
```
[2024-01-15 10:31:00] INFO: Found 1 pending command(s) to process

[2024-01-15 10:31:00] INFO: Picked command for execution: get_status
  command_id: 124
  command_type: get_status
  junction_id: 1
  created_at: 2024-01-15T10:30:58

[2024-01-15 10:31:00] INFO: Started executing command: get_status
  command_id: 124
  command_type: get_status

[2024-01-15 10:31:00] DEBUG: Getting control system status

[2024-01-15 10:31:00] DEBUG: Control request: GET http://localhost:5000/status

[2024-01-15 10:31:10] ERROR: Control connection error: /status
  error: Failed to connect to control system at http://localhost:5000

[2024-01-15 10:31:10] ERROR: Command execution failed: get_status
  command_id: 124
  command_type: get_status
  error: Failed to connect to control system at http://localhost:5000
```

### Check Command Status
```json
{
  "id": 124,
  "junction_id": 1,
  "command_type": "get_status",
  "payload": "{}",
  "status": "failed",
  "response": null,
  "error_message": "Failed to connect to control system at http://localhost:5000",
  "created_by": 1,
  "retry_count": 0,
  "max_retries": 3,
  "created_at": "2024-01-15T10:30:58",
  "executed_at": "2024-01-15T10:31:00",
  "completed_at": "2024-01-15T10:31:10"
}
```

---

## Example 3: Validation Error (Missing Required Field)

### Create Command
```bash
curl -X POST http://localhost:8000/api/v1/commands/send \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "set_mode",
    "payload": {},
    "execute_immediately": false
  }'
```

### Executor Logs
```
[2024-01-15 10:32:00] INFO: Found 1 pending command(s) to process

[2024-01-15 10:32:00] INFO: Picked command for execution: set_mode
  command_id: 125
  command_type: set_mode
  junction_id: 1
  created_at: 2024-01-15T10:31:58

[2024-01-15 10:32:00] INFO: Started executing command: set_mode
  command_id: 125
  command_type: set_mode

[2024-01-15 10:32:00] ERROR: Command validation failed: set_mode
  command_id: 125
  command_type: set_mode
  error: 'mode' is required in payload for SET_MODE command
```

### Check Command Status
```json
{
  "id": 125,
  "junction_id": 1,
  "command_type": "set_mode",
  "payload": "{}",
  "status": "failed",
  "response": null,
  "error_message": "'mode' is required in payload for SET_MODE command",
  "created_by": 1,
  "retry_count": 0,
  "max_retries": 3,
  "created_at": "2024-01-15T10:31:58",
  "executed_at": "2024-01-15T10:32:00",
  "completed_at": "2024-01-15T10:32:00"
}
```

---

## Example 4: Batch Command Processing

### Create Multiple Commands
```python
import httpx
import asyncio

async def create_batch_commands():
    commands = [
        {"command_type": "get_status", "payload": {}},
        {"command_type": "set_mode", "payload": {"mode": "manual"}},
        {"command_type": "set_time", "payload": {
            "lane1": 30, "lane2": 45, "lane3": 30, "lane4": 45
        }},
        {"command_type": "vip_mode", "payload": {
            "active": True, "lanes_to_green": [1, 2]
        }},
        {"command_type": "vip_mode", "payload": {"active": False}}
    ]
    
    async with httpx.AsyncClient() as client:
        for cmd in commands:
            response = await client.post(
                "http://localhost:8000/api/v1/commands/send",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "junction_id": 1,
                    "command_type": cmd["command_type"],
                    "payload": cmd["payload"],
                    "execute_immediately": False
                }
            )
            print(f"Created: {response.json()['command_id']}")

asyncio.run(create_batch_commands())
```

### Executor Logs
```
[2024-01-15 10:33:00] INFO: Found 5 pending command(s) to process

[2024-01-15 10:33:00] INFO: Picked command for execution: get_status
  command_id: 126
  ...

[2024-01-15 10:33:00] INFO: Command completed successfully: get_status
  command_id: 126
  ...

[2024-01-15 10:33:00] INFO: Picked command for execution: set_mode
  command_id: 127
  ...

[2024-01-15 10:33:01] INFO: Command completed successfully: set_mode
  command_id: 127
  ...

[2024-01-15 10:33:01] INFO: Picked command for execution: set_time
  command_id: 128
  ...

[2024-01-15 10:33:01] INFO: Command completed successfully: set_time
  command_id: 128
  ...

[2024-01-15 10:33:01] INFO: Picked command for execution: vip_mode
  command_id: 129
  ...

[2024-01-15 10:33:02] INFO: Command completed successfully: vip_mode
  command_id: 129
  ...

[2024-01-15 10:33:02] INFO: Picked command for execution: vip_mode
  command_id: 130
  ...

[2024-01-15 10:33:02] INFO: Command completed successfully: vip_mode
  command_id: 130
  ...
```

---

## Example 5: Application Startup/Shutdown Logs

### Startup
```
[2024-01-15 10:00:00] INFO: Starting ITMS Backend...
[2024-01-15 10:00:00] INFO: Environment: Development
[2024-01-15 10:00:00] INFO: CommandExecutor initialized
  poll_interval: 2
[2024-01-15 10:00:00] INFO: CommandExecutor started
[2024-01-15 10:00:00] INFO: CommandExecutor loop started
[2024-01-15 10:00:00] INFO: Command executor started successfully
[2024-01-15 10:00:00] INFO: Application startup complete
```

### Shutdown
```
[2024-01-15 18:00:00] INFO: Shutting down ITMS Backend...
[2024-01-15 18:00:00] INFO: CommandExecutor loop stopped
[2024-01-15 18:00:00] INFO: CommandExecutor stopped
[2024-01-15 18:00:00] INFO: Command executor stopped
[2024-01-15 18:00:00] INFO: Application shutdown complete
```

---

## Example 6: Monitoring Command Execution

### Python Script
```python
import httpx
import asyncio
import time

async def monitor_command(command_id: int):
    """Monitor command execution in real-time"""
    async with httpx.AsyncClient() as client:
        start_time = time.time()
        
        while True:
            response = await client.get(
                f"http://localhost:8000/api/v1/commands/{command_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            command = response.json()
            status = command["status"]
            elapsed = time.time() - start_time
            
            print(f"[{elapsed:.1f}s] Status: {status}")
            
            if status in ["success", "failed", "timeout"]:
                print(f"\nFinal Status: {status}")
                if command["error_message"]:
                    print(f"Error: {command['error_message']}")
                break
            
            await asyncio.sleep(0.5)

# Usage
command_id = 123
asyncio.run(monitor_command(command_id))
```

### Output
```
[0.0s] Status: pending
[0.5s] Status: pending
[1.0s] Status: pending
[1.5s] Status: pending
[2.0s] Status: executing
[2.5s] Status: executing
[3.0s] Status: success

Final Status: success
```

---

## Example 7: Command Statistics

### Get Statistics
```bash
curl -X GET http://localhost:8000/api/v1/commands/stats \
  -H "Authorization: Bearer eyJhbGc..."
```

### Response
```json
{
  "total_commands": 150,
  "pending_commands": 5,
  "executing_commands": 2,
  "success_commands": 120,
  "failed_commands": 20,
  "timeout_commands": 2,
  "cancelled_commands": 1,
  "commands_by_type": {
    "get_status": 50,
    "set_mode": 40,
    "set_time": 30,
    "vip_mode": 25,
    "emergency_stop": 5
  },
  "commands_by_junction": {
    "1": 75,
    "2": 50,
    "3": 25
  },
  "average_execution_time": 0.25
}
```

---

## Example 8: Error Recovery

### Retry Failed Command
```bash
curl -X POST http://localhost:8000/api/v1/commands/124/retry \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

### Response
```json
{
  "success": true,
  "command_id": 124,
  "status": "pending",
  "message": "Command queued for retry"
}
```

### Executor Logs
```
[2024-01-15 10:35:00] INFO: Retrying command: get_status (attempt 1/3)
  command_id: 124
  command_type: get_status
  retry_count: 1

[2024-01-15 10:35:02] INFO: Found 1 pending command(s) to process

[2024-01-15 10:35:02] INFO: Picked command for execution: get_status
  command_id: 124
  ...

[2024-01-15 10:35:02] INFO: Command completed successfully: get_status
  command_id: 124
  ...
```

---

## Summary

These examples demonstrate:
- ✅ Successful command execution
- ✅ Error handling (connection failures, validation errors)
- ✅ Batch processing
- ✅ Real-time monitoring
- ✅ Statistics tracking
- ✅ Retry mechanism
- ✅ Comprehensive logging

All examples are production-ready and can be used as templates for your implementation!
