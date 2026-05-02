# Command Executor System - Complete Guide

## Overview

The Command Executor System is a **background processor** that automatically executes pending commands from the database. It runs continuously as a FastAPI background task and processes commands using the existing control service.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Application                      │
│                                                                   │
│  ┌────────────────┐         ┌──────────────────┐                │
│  │  API Endpoint  │────────▶│ Command Service  │                │
│  │ POST /commands │         │  (Create Command)│                │
│  └────────────────┘         └──────────────────┘                │
│                                      │                            │
│                                      ▼                            │
│                             ┌─────────────────┐                  │
│                             │    Database     │                  │
│                             │  (Commands)     │                  │
│                             └─────────────────┘                  │
│                                      ▲                            │
│                                      │                            │
│  ┌────────────────────────────────────────────────────┐          │
│  │         Command Executor (Background Task)         │          │
│  │                                                     │          │
│  │  1. Poll database every 2 seconds                  │          │
│  │  2. Fetch commands with status = PENDING           │          │
│  │  3. Update status → EXECUTING                      │          │
│  │  4. Execute using Control Service                  │          │
│  │  5. Update status → SUCCESS or FAILED              │          │
│  │  6. Store response/error_message                   │          │
│  └────────────────────────────────────────────────────┘          │
│                                      │                            │
│                                      ▼                            │
│                             ┌─────────────────┐                  │
│                             │ Control Service │                  │
│                             │ (Execute Logic) │                  │
│                             └─────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Command Executor (`app/services/command_executor.py`)

**Purpose**: Background processor that polls database and executes pending commands.

**Key Features**:
- Runs as async background task
- Polls database every 2 seconds
- Processes up to 100 commands per iteration
- Uses Control Service for execution
- Comprehensive error handling
- Detailed logging at every step

**Main Methods**:
- `start()` - Start the background executor
- `stop()` - Stop the background executor
- `_run_loop()` - Main execution loop
- `_process_pending_commands()` - Fetch and process pending commands
- `_execute_command()` - Execute a single command

### 2. Control Service (`app/services/control_service.py`)

**Purpose**: Communication layer with traffic control hardware/simulation.

**Supported Operations**:
- `switch_mode(mode_name)` - Switch traffic control mode
- `set_manual_times(lane1, lane2, lane3, lane4)` - Set manual lane timings
- `vip_override(active, lanes_to_green)` - VIP mode control
- `get_status()` - Get current system status
- `emergency_stop()` - Emergency stop all signals

### 3. Command Model (`app/models/command.py`)

**Status Flow**:
```
PENDING → EXECUTING → SUCCESS
                   └→ FAILED
                   └→ TIMEOUT
```

**Key Fields**:
- `status` - Current command status
- `response` - JSON response from control system
- `error_message` - Error message if failed
- `created_at` - When command was created
- `executed_at` - When execution started
- `completed_at` - When execution finished

## Command Types

### 1. SET_MODE
Switch traffic control mode.

**Payload**:
```json
{
  "mode": "manual"  // Options: manual, auto_circle, auto_jump, blinker, vip
}
```

**Example**:
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

### 2. SET_TIME
Set manual timing for all lanes.

**Payload**:
```json
{
  "lane1": 30,  // Green time in seconds
  "lane2": 45,
  "lane3": 30,
  "lane4": 45
}
```

**Example**:
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

### 3. VIP_MODE
Activate or deactivate VIP override mode.

**Payload**:
```json
{
  "active": true,
  "lanes_to_green": [1, 2]  // Optional: lanes to turn green
}
```

**Example (Activate)**:
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

**Example (Deactivate)**:
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

### 4. GET_STATUS
Get current status from control system.

**Payload**: Empty or null

**Example**:
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

### 5. EMERGENCY_STOP
Emergency stop - set all signals to red/blinker.

**Payload**: Empty or null

**Example**:
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

### 6. HEARTBEAT
Heartbeat check (same as GET_STATUS).

**Payload**: Empty or null

## Usage

### Immediate Execution vs Background Processing

**Immediate Execution** (`execute_immediately: true`):
- Command is executed synchronously
- API waits for completion
- Returns result immediately
- Use for interactive operations

**Background Processing** (`execute_immediately: false`):
- Command is queued with status PENDING
- API returns immediately
- Background executor picks it up within 2 seconds
- Use for batch operations or scheduled tasks

### Creating Commands

```python
import httpx

async def create_command():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/commands/send",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "junction_id": 1,
                "command_type": "set_mode",
                "payload": {"mode": "auto_circle"},
                "execute_immediately": False  # Background processing
            }
        )
        
        data = response.json()
        command_id = data["command_id"]
        print(f"Command created: {command_id}")
        return command_id
```

### Monitoring Command Status

```python
async def check_command_status(command_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8000/api/v1/commands/{command_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        command = response.json()
        print(f"Status: {command['status']}")
        print(f"Response: {command['response']}")
        print(f"Error: {command['error_message']}")
```

### Waiting for Completion

```python
import asyncio

async def wait_for_completion(command_id: int, timeout: int = 30):
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        command = await check_command_status(command_id)
        
        if command['status'] in ['success', 'failed', 'timeout']:
            return command
        
        await asyncio.sleep(1)
    
    raise TimeoutError(f"Command {command_id} did not complete")
```

## Logging

The executor provides comprehensive logging at every step:

### Command Picked
```
INFO: Picked command for execution: set_mode
  command_id: 123
  command_type: set_mode
  junction_id: 1
  created_at: 2024-01-15T10:30:00
```

### Execution Started
```
INFO: Started executing command: set_mode
  command_id: 123
  command_type: set_mode
```

### Execution Completed (Success)
```
INFO: Command completed successfully: set_mode
  command_id: 123
  command_type: set_mode
  response: {"success": true, "message": "Mode switched"}
```

### Execution Failed
```
ERROR: Command failed: set_mode
  command_id: 123
  command_type: set_mode
  error: Connection refused by control system
```

## Testing

### Run Test Script

```bash
cd backend
python test_command_executor.py
```

The test script will:
1. Login as admin
2. Create 5 test commands with `execute_immediately=False`
3. Monitor their execution by the background executor
4. Display detailed results and timing

### Expected Output

```
================================================================================
COMMAND EXECUTOR SYSTEM TEST
================================================================================

STEP 1: Login as admin
✓ Login successful

STEP 2: Test Background Command Execution
Creating commands with execute_immediately=False

1. Creating command: GET_STATUS
   ✓ Command created: ID=1, Status=pending

2. Creating command: SET_MODE (manual)
   ✓ Command created: ID=2, Status=pending

...

STEP 3: Monitor Command Execution
Waiting for background executor to process commands...

Monitoring: GET_STATUS (ID: 1)
  ✓ Status: success
  ✓ Execution time: 0.15s

Monitoring: SET_MODE (ID: 2)
  ✓ Status: success
  ✓ Execution time: 0.12s

...

STEP 4: Test Summary
Total Commands: 5
Successful: 5
Failed: 0
Success Rate: 100.0%
```

## Integration with FastAPI

The executor is automatically started when FastAPI starts:

```python
# app/main.py

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from app.services.command_executor import get_command_executor
    executor = get_command_executor()
    await executor.start()
    
    yield
    
    # Shutdown
    await executor.stop()
```

## Configuration

### Poll Interval

Default: 2 seconds

To change:
```python
executor = CommandExecutor(poll_interval=5)  # Poll every 5 seconds
```

### Batch Size

Default: 100 commands per iteration

To change, modify `_process_pending_commands()`:
```python
.limit(100)  # Change to desired batch size
```

## Error Handling

### Validation Errors
- Invalid payload format
- Missing required fields
- Invalid command type

**Result**: Status set to FAILED, error_message stored

### Communication Errors
- Control system not reachable
- Connection timeout
- HTTP errors

**Result**: Status set to FAILED or TIMEOUT, error_message stored

### Unexpected Errors
- Database errors
- JSON parsing errors
- Unknown exceptions

**Result**: Status set to FAILED, error logged with stack trace

## Best Practices

### 1. Use Background Processing for Batch Operations
```python
# Good: Queue multiple commands
for junction_id in [1, 2, 3, 4, 5]:
    await create_command(
        junction_id=junction_id,
        command_type="get_status",
        execute_immediately=False  # Background processing
    )
```

### 2. Use Immediate Execution for Interactive Operations
```python
# Good: Immediate execution for user-triggered actions
result = await create_command(
    junction_id=1,
    command_type="emergency_stop",
    execute_immediately=True  # Wait for result
)
```

### 3. Monitor Command Status
```python
# Good: Check status after creating command
command_id = await create_command(...)
await asyncio.sleep(5)  # Wait for processing
status = await check_command_status(command_id)
```

### 4. Handle Failures Gracefully
```python
# Good: Check for failures and retry if needed
command = await check_command_status(command_id)
if command['status'] == 'failed':
    # Retry or alert user
    await retry_command(command_id)
```

## Troubleshooting

### Commands Stay in PENDING Status

**Possible Causes**:
- Executor not started
- Executor crashed
- Database connection issues

**Solution**:
1. Check logs for executor startup message
2. Restart FastAPI application
3. Check database connectivity

### Commands Fail Immediately

**Possible Causes**:
- Control system not running
- Invalid payload
- Network issues

**Solution**:
1. Check control system is running at configured URL
2. Verify payload format matches command type
3. Check network connectivity

### High Execution Time

**Possible Causes**:
- Control system slow to respond
- Network latency
- Too many commands in queue

**Solution**:
1. Optimize control system performance
2. Reduce poll interval
3. Increase batch size

## Production Considerations

### 1. Monitoring
- Monitor executor health
- Track command success rate
- Alert on high failure rate

### 2. Scaling
- Single executor instance per application
- Use database locking for multiple instances
- Consider message queue for high volume

### 3. Reliability
- Implement retry logic for transient failures
- Set appropriate timeouts
- Log all errors for debugging

### 4. Performance
- Tune poll interval based on load
- Adjust batch size for throughput
- Monitor database query performance

## Summary

The Command Executor System provides:
- ✅ Automatic background processing
- ✅ Reliable command execution
- ✅ Comprehensive error handling
- ✅ Detailed logging
- ✅ Easy integration with FastAPI
- ✅ Support for all command types
- ✅ Production-ready architecture

The system is now ready for production use!
