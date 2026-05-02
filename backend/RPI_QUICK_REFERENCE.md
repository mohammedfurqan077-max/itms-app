# Raspberry Pi Integration - Quick Reference

## Quick Start

### 1. Start Test Server
```bash
python backend/test_rpi_server.py
```

### 2. Update Junction IP
```bash
curl -X PUT http://localhost:8000/api/v1/junctions/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "127.0.0.1"}'
```

### 3. Send Test Command
```bash
curl -X POST http://localhost:8000/api/v1/commands/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "set_mode",
    "payload": {"mode": "auto"},
    "execute_immediately": true
  }'
```

---

## RPi API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/mode/{mode}` | POST | Set traffic mode |
| `/api/set_manual_times` | POST | Set lane timings |
| `/api/vip_override` | POST | VIP mode control |
| `/status` | GET | Get junction status |

---

## Command Types

| Type | RPi Endpoint | Payload |
|------|--------------|---------|
| `set_mode` | `/mode/{mode}` | `{"mode": "auto"}` |
| `set_time` | `/api/set_manual_times` | `{"lane1": 30, "lane2": 30, ...}` |
| `vip_mode` | `/api/vip_override` | `{"active": true, "lanes_to_green": [1,3]}` |
| `emergency_stop` | `/mode/emergency` | `{}` |
| `get_status` | `/status` | `{}` |
| `heartbeat` | `/status` | `{}` |

---

## Configuration

### Environment Variables
```env
CONTROL_SYSTEM_API_KEY=dev-api-key
CONTROL_SYSTEM_TIMEOUT=10
```

### Junction IP Addresses
```sql
UPDATE junctions SET ip_address = '192.168.1.100' WHERE id = 1;
UPDATE junctions SET ip_address = '192.168.1.101' WHERE id = 2;
UPDATE junctions SET ip_address = '192.168.1.102' WHERE id = 3;
```

---

## Error Handling

| Error | Status | Cause |
|-------|--------|-------|
| Timeout | `timeout` | No response after 10s |
| Connection Refused | `failed` | RPi offline/unreachable |
| HTTP Error | `failed` | RPi returns 4xx/5xx |
| Invalid Response | `failed` | Malformed JSON |

---

## Testing Commands

### Set Mode
```bash
curl -X POST http://localhost:8000/api/v1/commands/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "set_mode",
    "payload": {"mode": "auto"},
    "execute_immediately": true
  }'
```

### Set Times
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
    "execute_immediately": true
  }'
```

### VIP Mode
```bash
curl -X POST http://localhost:8000/api/v1/commands/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "vip_mode",
    "payload": {
      "active": true,
      "lanes_to_green": [1, 3]
    },
    "execute_immediately": true
  }'
```

### Get Status
```bash
curl -X POST http://localhost:8000/api/v1/commands/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "get_status",
    "payload": {},
    "execute_immediately": true
  }'
```

---

## Monitoring

### Command Statistics
```bash
curl -X GET http://localhost:8000/api/v1/commands/stats/overview \
  -H "Authorization: Bearer $TOKEN"
```

### Failed Commands
```bash
curl -X GET "http://localhost:8000/api/v1/commands?status=failed" \
  -H "Authorization: Bearer $TOKEN"
```

### Recent Commands
```bash
curl -X GET "http://localhost:8000/api/v1/commands?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Troubleshooting

### Check RPi Connectivity
```bash
# Ping RPi
ping 192.168.1.100

# Test RPi API
curl -X GET http://192.168.1.100:5000/status \
  -H "X-API-KEY: dev-api-key"
```

### Check Backend Logs
```bash
# View logs
tail -f backend/logs/app.log

# Search for errors
grep "ERROR" backend/logs/app.log
```

### Retry Failed Command
```bash
curl -X POST http://localhost:8000/api/v1/commands/123/retry \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

---

## Production Checklist

- [ ] RPi Flask server installed and running
- [ ] RPi has static IP address
- [ ] API key configured on RPi
- [ ] Firewall allows port 5000
- [ ] Junction IP addresses updated in database
- [ ] Backend API key matches RPi
- [ ] Connectivity tested
- [ ] Test commands sent successfully
- [ ] Monitoring configured

---

## Documentation

- **RPI_INTEGRATION_GUIDE.md** - Complete guide
- **RPI_INTEGRATION_EXAMPLES.sh** - Example scripts
- **test_rpi_server.py** - Mock server for testing
- **RPI_INTEGRATION_COMPLETE.md** - Summary

---

**Quick Reference v1.0** - Raspberry Pi Integration
