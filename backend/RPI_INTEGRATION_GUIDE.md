# Raspberry Pi Integration Guide

## Overview

The command execution system now communicates directly with Raspberry Pi devices running Flask servers at each traffic junction. This replaces the previous mock control service simulation.

---

## Architecture

```
Backend API
    ↓
Command Service
    ↓
HTTP Request (httpx)
    ↓
Raspberry Pi Flask Server (Port 5000)
    ↓
Traffic Signal Hardware
```

---

## Raspberry Pi API Endpoints

### Base URL
```
http://{junction_ip_address}:5000
```

### 1. Set Mode
**POST** `/mode/{mode_name}`

**Headers:**
```
X-API-KEY: {api_key}
Content-Type: application/json
```

**Example:**
```bash
curl -X POST http://192.168.1.100:5000/mode/auto \
  -H "X-API-KEY: dev-api-key"
```

**Response:**
```json
{
  "success": true,
  "mode": "auto",
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### 2. Set Manual Times
**POST** `/api/set_manual_times`

**Headers:**
```
X-API-KEY: {api_key}
Content-Type: application/json
```

**Request Body:**
```json
{
  "lane1_time": 30,
  "lane2_time": 45,
  "lane3_time": 30,
  "lane4_time": 45
}
```

**Example:**
```bash
curl -X POST http://192.168.1.100:5000/api/set_manual_times \
  -H "X-API-KEY: dev-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "lane1_time": 30,
    "lane2_time": 45,
    "lane3_time": 30,
    "lane4_time": 45
  }'
```

**Response:**
```json
{
  "success": true,
  "timings": {
    "lane1": 30,
    "lane2": 45,
    "lane3": 30,
    "lane4": 45
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### 3. VIP Override
**POST** `/api/vip_override`

**Headers:**
```
X-API-KEY: {api_key}
Content-Type: application/json
```

**Request Body:**
```json
{
  "active": true,
  "lanes_to_green": ["81", "82"]
}
```

**Example:**
```bash
curl -X POST http://192.168.1.100:5000/api/vip_override \
  -H "X-API-KEY: dev-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "active": true,
    "lanes_to_green": ["81", "82"]
  }'
```

**Response:**
```json
{
  "success": true,
  "vip_active": true,
  "lanes_to_green": ["81", "82"],
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### 4. Get Status
**GET** `/status`

**Headers:**
```
X-API-KEY: {api_key}
```

**Example:**
```bash
curl -X GET http://192.168.1.100:5000/status \
  -H "X-API-KEY: dev-api-key"
```

**Response:**
```json
{
  "success": true,
  "mode": "manual",
  "lane_states": {
    "lane1": "green",
    "lane2": "red",
    "lane3": "red",
    "lane4": "red"
  },
  "timings": {
    "lane1": 30,
    "lane2": 30,
    "lane3": 30,
    "lane4": 30
  },
  "vip_active": false,
  "emergency_stop": false,
  "timestamp": "2024-01-15T10:30:00"
}
```

---

## Backend Configuration

### Environment Variables

Add to `backend/.env`:

```env
# Raspberry Pi Communication
CONTROL_SYSTEM_API_KEY=your-secure-api-key-here
CONTROL_SYSTEM_TIMEOUT=10

# Junction Communication
JUNCTION_TIMEOUT_SECONDS=10
JUNCTION_RETRY_ATTEMPTS=3
JUNCTION_RETRY_BACKOFF=2
```

### Configuration in `config.py`

```python
# Junction Communication
JUNCTION_TIMEOUT_SECONDS: int = 10
JUNCTION_RETRY_ATTEMPTS: int = 3
JUNCTION_RETRY_BACKOFF: int = 2

# Control System (External Hardware/Simulation)
CONTROL_SYSTEM_URL: str = "http://localhost:5000"
CONTROL_SYSTEM_API_KEY: str = "dev-api-key"
CONTROL_SYSTEM_TIMEOUT: int = 10
```

---

## Command Execution Flow

### 1. Send Command via API

```bash
curl -X POST http://localhost:8000/api/v1/commands/send \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "set_mode",
    "payload": {
      "mode": "auto"
    },
    "execute_immediately": true
  }'
```

### 2. Backend Processing

```python
# 1. Create command in database
command = Command(
    junction_id=1,
    command_type="set_mode",
    payload='{"mode": "auto"}',
    status="pending"
)

# 2. Get junction from database
junction = await db.get(Junction, 1)
# junction.ip_address = "192.168.1.100"

# 3. Build RPi URL
base_url = f"http://{junction.ip_address}:5000"
endpoint = "/mode/auto"
url = f"{base_url}{endpoint}"

# 4. Send HTTP request
async with httpx.AsyncClient(timeout=10) as client:
    response = await client.post(
        url,
        headers={"X-API-KEY": api_key}
    )

# 5. Update command status
command.status = "success"
command.response = response.json()
command.completed_at = datetime.utcnow()
```

### 3. Response to Client

```json
{
  "command_id": 123,
  "success": true,
  "message": "Command executed successfully",
  "status": "success",
  "response_data": {
    "success": true,
    "mode": "auto",
    "timestamp": "2024-01-15T10:30:00"
  },
  "executed_at": "2024-01-15T10:30:00"
}
```

---

## Command Type Mapping

| Backend Command | RPi Endpoint | Method | Payload |
|----------------|--------------|--------|---------|
| `SET_MODE` | `/mode/{mode}` | POST | None |
| `SET_TIME` | `/api/set_manual_times` | POST | `{lane1_time, lane2_time, lane3_time, lane4_time}` |
| `VIP_MODE` | `/api/vip_override` | POST | `{active, lanes_to_green}` |
| `EMERGENCY_STOP` | `/mode/emergency` | POST | None |
| `GET_STATUS` | `/status` | GET | None |
| `HEARTBEAT` | `/status` | GET | None |

---

## Error Handling

### Timeout Error
```python
# After 10 seconds with no response
command.status = "timeout"
command.error_message = "Request timeout to junction Main Square (192.168.1.100)"
```

### Connection Refused
```python
# RPi device is offline or unreachable
command.status = "failed"
command.error_message = "Connection refused by junction Main Square (192.168.1.100)"
```

### HTTP Error
```python
# RPi returns 4xx or 5xx status code
command.status = "failed"
command.error_message = "HTTP error 500 from junction Main Square"
```

### Invalid Response
```python
# RPi returns non-JSON or malformed response
command.status = "failed"
command.error_message = "Invalid response from junction Main Square"
```

---

## Testing

### 1. Test with Mock RPi Server

Create a simple Flask server for testing:

```python
# test_rpi_server.py
from flask import Flask, request, jsonify

app = Flask(__name__)
API_KEY = "dev-api-key"

def check_api_key():
    if request.headers.get('X-API-KEY') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    return None

@app.route('/mode/<mode_name>', methods=['POST'])
def set_mode(mode_name):
    error = check_api_key()
    if error:
        return error
    
    return jsonify({
        "success": True,
        "mode": mode_name,
        "timestamp": "2024-01-15T10:30:00"
    })

@app.route('/api/set_manual_times', methods=['POST'])
def set_manual_times():
    error = check_api_key()
    if error:
        return error
    
    data = request.json
    return jsonify({
        "success": True,
        "timings": {
            "lane1": data.get('lane1_time'),
            "lane2": data.get('lane2_time'),
            "lane3": data.get('lane3_time'),
            "lane4": data.get('lane4_time')
        },
        "timestamp": "2024-01-15T10:30:00"
    })

@app.route('/api/vip_override', methods=['POST'])
def vip_override():
    error = check_api_key()
    if error:
        return error
    
    data = request.json
    return jsonify({
        "success": True,
        "vip_active": data.get('active'),
        "lanes_to_green": data.get('lanes_to_green'),
        "timestamp": "2024-01-15T10:30:00"
    })

@app.route('/status', methods=['GET'])
def get_status():
    error = check_api_key()
    if error:
        return error
    
    return jsonify({
        "success": True,
        "mode": "manual",
        "lane_states": {
            "lane1": "green",
            "lane2": "red",
            "lane3": "red",
            "lane4": "red"
        },
        "timings": {
            "lane1": 30,
            "lane2": 30,
            "lane3": 30,
            "lane4": 30
        },
        "vip_active": False,
        "emergency_stop": False,
        "timestamp": "2024-01-15T10:30:00"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

Run the test server:
```bash
python test_rpi_server.py
```

### 2. Update Junction IP Address

```bash
# Update junction to point to test server
curl -X PUT http://localhost:8000/api/v1/junctions/1 \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "127.0.0.1"
  }'
```

### 3. Send Test Command

```bash
curl -X POST http://localhost:8000/api/v1/commands/send \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "set_mode",
    "payload": {
      "mode": "auto"
    },
    "execute_immediately": true
  }'
```

---

## Production Deployment

### 1. Setup Raspberry Pi

Each RPi should:
- Run Flask server on port 5000
- Have static IP address
- Be accessible from backend server
- Have API key configured

### 2. Configure Junctions

Update each junction with correct IP address:

```sql
UPDATE junctions 
SET ip_address = '192.168.1.100' 
WHERE id = 1;

UPDATE junctions 
SET ip_address = '192.168.1.101' 
WHERE id = 2;
```

### 3. Set API Key

Update `.env` with production API key:

```env
CONTROL_SYSTEM_API_KEY=your-production-api-key-here
```

Ensure RPi devices use the same API key.

### 4. Test Connectivity

```bash
# Test each junction
curl -X GET http://192.168.1.100:5000/status \
  -H "X-API-KEY: your-production-api-key-here"
```

---

## Monitoring

### Check Command Status

```bash
# Get command statistics
curl -X GET http://localhost:8000/api/v1/commands/stats/overview \
  -H "Authorization: Bearer {token}"
```

### Check Failed Commands

```bash
# List failed commands
curl -X GET "http://localhost:8000/api/v1/commands?status=failed" \
  -H "Authorization: Bearer {token}"
```

### Check Junction Status

```bash
# Send heartbeat to all junctions
for junction_id in 1 2 3; do
  curl -X POST http://localhost:8000/api/v1/commands/send \
    -H "Authorization: Bearer {token}" \
    -H "Content-Type: application/json" \
    -d "{
      \"junction_id\": $junction_id,
      \"command_type\": \"heartbeat\",
      \"payload\": {},
      \"execute_immediately\": true
    }"
done
```

---

## Troubleshooting

### Issue: Connection Timeout

**Symptoms:** Commands fail with "Request timeout"

**Solutions:**
1. Check RPi is powered on
2. Verify network connectivity: `ping {junction_ip}`
3. Check Flask server is running on RPi
4. Increase timeout in config: `CONTROL_SYSTEM_TIMEOUT=20`

### Issue: Connection Refused

**Symptoms:** Commands fail with "Connection refused"

**Solutions:**
1. Check Flask server is running: `curl http://{junction_ip}:5000/status`
2. Check firewall allows port 5000
3. Verify IP address is correct in database

### Issue: Unauthorized

**Symptoms:** Commands fail with HTTP 401

**Solutions:**
1. Check API key matches between backend and RPi
2. Verify `X-API-KEY` header is being sent
3. Check RPi API key configuration

### Issue: Invalid Response

**Symptoms:** Commands fail with "Invalid response"

**Solutions:**
1. Check RPi returns valid JSON
2. Verify response format matches expected structure
3. Check RPi logs for errors

---

## Security Considerations

### 1. API Key
- Use strong, random API key in production
- Rotate API key periodically
- Never commit API key to git

### 2. Network Security
- Use VPN or private network for RPi communication
- Consider HTTPS for production (requires SSL certificates on RPi)
- Implement IP whitelisting on RPi

### 3. Authentication
- RPi should validate API key on every request
- Log all unauthorized access attempts
- Implement rate limiting on RPi

---

## Future Enhancements

### 1. HTTPS Support
```python
# Use HTTPS for secure communication
base_url = f"https://{junction.ip_address}:5000"
```

### 2. Retry Logic
```python
# Automatic retry with exponential backoff
for attempt in range(3):
    try:
        response = await send_to_rpi(...)
        break
    except Exception:
        await asyncio.sleep(2 ** attempt)
```

### 3. WebSocket Updates
```python
# Real-time status updates from RPi
ws = await websocket.connect(f"ws://{junction.ip_address}:5000/ws")
```

### 4. Command Queue
```python
# Background worker to process pending commands
async def process_pending_commands():
    commands = await get_pending_commands()
    for command in commands:
        await execute_command(command.id)
```

---

## Conclusion

The command execution system now communicates directly with Raspberry Pi devices, providing:

- ✅ Real junction device control
- ✅ Proper error handling
- ✅ Timeout management
- ✅ Complete audit trail
- ✅ Support for multiple junctions
- ✅ Production-ready architecture

**Status:** Ready for deployment with real Raspberry Pi devices! 🚀
