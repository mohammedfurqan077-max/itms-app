# Command Execution System Guide

## Overview

The Command Execution System provides a robust mechanism for sending commands to junction devices (Raspberry Pi controllers) and tracking their execution status. This system acts as a communication layer between the backend API and physical traffic control devices.

## Architecture

### Components

1. **Command Model** (`app/models/command.py`)
   - Database model for command tracking
   - Stores command details, status, and execution history
   - Supports retry logic and error tracking

2. **Command Schemas** (`app/schemas/command.py`)
   - Pydantic models for request/response validation
   - Type-safe command creation and execution
   - JSON payload validation

3. **Command Service** (`app/services/command_service.py`)
   - Business logic for command execution
   - Integration with control service
   - Retry and error handling logic

4. **Command API** (`app/api/v1/endpoints/commands.py`)
   - RESTful endpoints for command management
   - Permission-based access control
   - Comprehensive API documentation

## Command Types

### 1. SET_MODE
Switch traffic control mode (auto/manual/vip)

**Payload:**
```json
{
  "mode": "auto"  // Options: "auto", "manual", "vip"
}
```

**Use Cases:**
- Switch to automatic mode for normal operation
- Switch to manual mode for operator control
- Switch to VIP mode for special events

### 2. SET_TIME
Set manual lane timings

**Payload:**
```json
{
  "lane1": 30,
  "lane2": 30,
  "lane3": 30,
  "lane4": 30
}
```

**Use Cases:**
- Adjust traffic flow during peak hours
- Optimize lane timings based on traffic patterns
- Manual override for special situations

### 3. VIP_MODE
Enable/disable VIP override for specific lanes

**Payload:**
```json
{
  "active": true,
  "lanes_to_green": [1, 3]
}
```

**Use Cases:**
- VIP vehicle passage (ambulance, police, etc.)
- Emergency vehicle priority
- Special event traffic management

### 4. EMERGENCY_STOP
Emergency stop all lanes (all red)

**Payload:**
```json
{}  // No payload required
```

**Use Cases:**
- Emergency situations
- System maintenance
- Safety incidents

### 5. HEARTBEAT
Check device connectivity and health

**Payload:**
```json
{}  // No payload required
```

**Use Cases:**
- Device health monitoring
- Connection verification
- System diagnostics

### 6. GET_STATUS
Get current device status and state

**Payload:**
```json
{}  // No payload required
```

**Use Cases:**
- Status monitoring
- System state verification
- Debugging and diagnostics

## Command Status Flow

```
PENDING → EXECUTING → SUCCESS
                   ↓
                 FAILED → (retry) → PENDING
                   ↓
                TIMEOUT
                   ↓
              CANCELLED
```

### Status Descriptions

- **PENDING**: Command created, waiting for execution
- **EXECUTING**: Command is currently being executed
- **SUCCESS**: Command executed successfully
- **FAILED**: Command execution failed (can be retried)
- **TIMEOUT**: Command execution timed out
- **CANCELLED**: Command was cancelled before execution

## API Endpoints

### 1. Send Command
**POST** `/api/v1/commands/send`

Send a command to a junction device.

**Request:**
```json
{
  "junction_id": 1,
  "command_type": "set_mode",
  "payload": {
    "mode": "auto"
  },
  "execute_immediately": true
}
```

**Response:**
```json
{
  "command_id": 123,
  "success": true,
  "message": "Command executed successfully",
  "status": "success",
  "response_data": {
    "mode": "auto",
    "timestamp": "2026-04-30T18:00:00Z"
  },
  "executed_at": "2026-04-30T18:00:00Z"
}
```

**Permissions:** `control:execute`

### 2. Get Command
**GET** `/api/v1/commands/{command_id}`

Get command details by ID.

**Response:**
```json
{
  "id": 123,
  "junction_id": 1,
  "command_type": "set_mode",
  "payload": "{\"mode\": \"auto\"}",
  "status": "success",
  "response": "{\"mode\": \"auto\"}",
  "error_message": null,
  "created_by": 1,
  "retry_count": 0,
  "max_retries": 3,
  "created_at": "2026-04-30T18:00:00Z",
  "executed_at": "2026-04-30T18:00:01Z",
  "completed_at": "2026-04-30T18:00:02Z"
}
```

**Permissions:** Authenticated user

### 3. List Commands
**GET** `/api/v1/commands`

List commands with pagination and filtering.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10, max: 100)
- `junction_id`: Filter by junction ID
- `command_type`: Filter by command type
- `status`: Filter by status

**Response:**
```json
{
  "commands": [...],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10
}
```

**Permissions:** Authenticated user

### 4. Retry Command
**POST** `/api/v1/commands/{command_id}/retry`

Retry a failed command.

**Request:**
```json
{
  "force": false
}
```

**Response:**
```json
{
  "command_id": 123,
  "success": true,
  "message": "Command executed successfully",
  "status": "success"
}
```

**Permissions:** `control:execute`

### 5. Cancel Command
**POST** `/api/v1/commands/{command_id}/cancel`

Cancel a pending command.

**Response:**
```json
{
  "id": 123,
  "status": "cancelled",
  "completed_at": "2026-04-30T18:00:00Z"
}
```

**Permissions:** `control:execute`

### 6. Get Statistics
**GET** `/api/v1/commands/stats/overview`

Get command execution statistics.

**Response:**
```json
{
  "total_commands": 1000,
  "pending_commands": 5,
  "executing_commands": 2,
  "success_commands": 950,
  "failed_commands": 40,
  "timeout_commands": 2,
  "cancelled_commands": 1,
  "commands_by_type": {
    "set_mode": 400,
    "set_time": 300,
    "vip_mode": 100,
    "emergency_stop": 50,
    "heartbeat": 100,
    "get_status": 50
  },
  "commands_by_junction": {
    "1": 500,
    "2": 300,
    "3": 200
  },
  "average_execution_time": 1.5
}
```

**Permissions:** Authenticated user

### 7. Get Pending Commands
**GET** `/api/v1/commands/pending/list`

Get pending commands for execution (admin only).

**Query Parameters:**
- `limit`: Maximum number of commands (default: 100, max: 1000)

**Response:**
```json
[
  {
    "id": 123,
    "command_type": "set_mode",
    "status": "pending",
    "created_at": "2026-04-30T18:00:00Z"
  }
]
```

**Permissions:** Admin only

## Retry Logic

### Automatic Retry
- Commands can be configured with `max_retries` (default: 3)
- Failed commands can be retried automatically or manually
- Retry count is tracked for each command

### Manual Retry
- Use the retry endpoint to manually retry a failed command
- Set `force: true` to retry even if max retries reached
- Useful for transient failures or network issues

### Retry Strategy
1. Command fails with status `FAILED`
2. Check if `retry_count < max_retries`
3. If yes, increment retry count and set status to `PENDING`
4. Execute command again
5. If no, command remains `FAILED` (unless forced)

## Error Handling

### Error Types
1. **Validation Errors**: Invalid payload or parameters
2. **Execution Errors**: Control service failures
3. **Timeout Errors**: Command execution timeout
4. **Network Errors**: Device communication failures

### Error Response
```json
{
  "command_id": 123,
  "success": false,
  "message": "Command execution failed",
  "status": "failed",
  "error": "Connection timeout to junction device"
}
```

### Error Storage
- All errors are stored in `error_message` field
- Full error context available for debugging
- Error history preserved for audit trail

## Integration with Control Service

The Command Service integrates with the Control Service for actual command execution:

```python
# Command Service → Control Service
response = await self.control_service.switch_mode(mode)
```

### Control Service Methods Used
- `switch_mode(mode)`: Switch traffic mode
- `set_manual_times(lane1, lane2, lane3, lane4)`: Set lane timings
- `vip_override(active, lanes_to_green)`: VIP mode control
- `emergency_stop()`: Emergency stop
- `get_status()`: Get system status
- `health_check()`: Health check

## Future: Raspberry Pi Integration

The Command Execution System is designed to support future Raspberry Pi integration:

### Current State
- Commands are executed through the mock control service
- All commands are tracked in the database
- Full audit trail is maintained

### Future State
- Commands will be sent to actual Raspberry Pi devices
- Device communication via HTTP/MQTT/WebSocket
- Real-time status updates from devices
- Device heartbeat monitoring

### Migration Path
1. Replace control service calls with device communication
2. Implement device-specific protocols (HTTP/MQTT)
3. Add device authentication and security
4. Implement real-time status updates
5. Add device health monitoring

## Security

### Authentication
- All endpoints require JWT authentication
- Token must be valid and not expired

### Authorization
- **Send Command**: Requires `control:execute` permission
- **Retry Command**: Requires `control:execute` permission
- **Cancel Command**: Requires `control:execute` permission
- **Get Pending**: Requires Admin role
- **Other Endpoints**: Authenticated user

### Audit Trail
- All commands are logged with user ID
- Full execution history is preserved
- Timestamps for all state changes

## Best Practices

### 1. Command Creation
- Always validate payload before sending
- Use appropriate command type for the operation
- Set reasonable `max_retries` value

### 2. Error Handling
- Check command status after execution
- Implement retry logic for transient failures
- Log all errors for debugging

### 3. Monitoring
- Monitor command statistics regularly
- Track failed commands and investigate
- Set up alerts for high failure rates

### 4. Performance
- Use pagination for large command lists
- Filter commands by junction/type/status
- Archive old commands periodically

### 5. Testing
- Test all command types thoroughly
- Verify retry logic works correctly
- Test error handling scenarios

## Example Workflows

### Workflow 1: Switch to Manual Mode
```bash
# 1. Send command
curl -X POST http://localhost:8000/api/v1/commands/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "set_mode",
    "payload": {"mode": "manual"},
    "execute_immediately": true
  }'

# 2. Check command status
curl -X GET http://localhost:8000/api/v1/commands/123 \
  -H "Authorization: Bearer $TOKEN"
```

### Workflow 2: Set Lane Timings
```bash
# 1. Send command
curl -X POST http://localhost:8000/api/v1/commands/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "set_time",
    "payload": {
      "lane1": 45,
      "lane2": 30,
      "lane3": 45,
      "lane4": 30
    },
    "execute_immediately": true
  }'
```

### Workflow 3: Handle Failed Command
```bash
# 1. Check failed commands
curl -X GET "http://localhost:8000/api/v1/commands?status=failed" \
  -H "Authorization: Bearer $TOKEN"

# 2. Retry failed command
curl -X POST http://localhost:8000/api/v1/commands/123/retry \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

### Workflow 4: Monitor System Health
```bash
# 1. Get command statistics
curl -X GET http://localhost:8000/api/v1/commands/stats/overview \
  -H "Authorization: Bearer $TOKEN"

# 2. Check pending commands
curl -X GET http://localhost:8000/api/v1/commands/pending/list \
  -H "Authorization: Bearer $TOKEN"
```

## Troubleshooting

### Issue: Command Stuck in PENDING
**Cause**: Command not executed
**Solution**: Check pending commands and execute manually or investigate system issues

### Issue: High Failure Rate
**Cause**: Control service issues or device connectivity
**Solution**: Check control service logs, verify device connectivity

### Issue: Commands Not Retrying
**Cause**: Max retries reached or retry logic disabled
**Solution**: Use force retry or increase max_retries

### Issue: Slow Command Execution
**Cause**: Network latency or device performance
**Solution**: Monitor execution times, optimize device communication

## Database Schema

### Commands Table
```sql
CREATE TABLE commands (
    id SERIAL PRIMARY KEY,
    junction_id INTEGER REFERENCES junctions(id) ON DELETE SET NULL,
    command_type commandtype NOT NULL,
    payload TEXT,
    status commandstatus NOT NULL DEFAULT 'pending',
    response TEXT,
    error_message TEXT,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    executed_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

### Indexes
- `ix_commands_id`: Primary key index
- `ix_commands_junction_id`: Junction lookup
- `ix_commands_command_type`: Type filtering
- `ix_commands_status`: Status filtering
- `ix_commands_created_by`: User lookup
- `ix_commands_created_at`: Time-based queries
- `idx_command_junction_status`: Composite index for junction + status
- `idx_command_type_status`: Composite index for type + status

## Conclusion

The Command Execution System provides a robust, scalable, and secure mechanism for managing traffic control commands. It supports current mock operations and is designed for future Raspberry Pi integration with minimal changes.
