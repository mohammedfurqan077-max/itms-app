# ITMS Backend - Complete API Endpoints Reference

## Base URL
```
http://localhost:8000/api/v1
```

---

## 1. Authentication APIs (`/auth`)

### 1.1 Login
**POST** `/auth/login`

**Request:**
```json
{
  "email": "admin@itms.com",
  "password": "admin123"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "name": "Admin User",
    "email": "admin@itms.com",
    "role": "admin",
    "status": "active"
  },
  "tokens": {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### 1.2 Register
**POST** `/auth/register`

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@itms.com",
  "password": "password123",
  "role": "jawan"
}
```

### 1.3 Get Current User
**GET** `/auth/me`

**Headers:** `Authorization: Bearer {token}`

### 1.4 Refresh Token
**POST** `/auth/refresh`

**Request:**
```json
{
  "refresh_token": "eyJhbGc..."
}
```

### 1.5 Change Password
**POST** `/auth/change-password`

**Request:**
```json
{
  "current_password": "old123",
  "new_password": "new456"
}
```

### 1.6 Logout
**POST** `/auth/logout?refresh_token={token}`

### 1.7 Verify Token
**POST** `/auth/verify-token`

---

## 2. System State APIs (`/system`)

### 2.1 Get System State
**GET** `/system/state`

**Response:**
```json
{
  "id": 1,
  "current_mode": "manual",
  "last_updated_by": 1,
  "junction_id": null,
  "mode_metadata": null,
  "updated_at": "2024-01-15T10:30:00",
  "created_at": "2024-01-01T00:00:00",
  "updated_by_name": "Admin User",
  "junction_name": null
}
```

### 2.2 Update Mode
**POST** `/system/mode/{mode}`

**Request:**
```json
{
  "new_mode": "auto_circle",
  "junction_id": null,
  "mode_metadata": null
}
```

### 2.3 Reset to Default
**POST** `/system/reset`

### 2.4 Get Current Mode
**GET** `/system/mode`

**Response:**
```json
{
  "current_mode": "manual"
}
```

---

## 3. Control System APIs (`/control`)

### 3.1 Switch Mode
**POST** `/control/mode`

**Request:**
```json
{
  "mode": "auto"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Mode switched to auto",
  "data": {
    "mode": "auto",
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

### 3.2 Set Manual Times
**POST** `/control/manual-times`

**Request:**
```json
{
  "lane1": 30,
  "lane2": 45,
  "lane3": 30,
  "lane4": 45
}
```

### 3.3 VIP Override
**POST** `/control/vip-override`

**Request:**
```json
{
  "active": true,
  "lanes_to_green": [1, 3]
}
```

### 3.4 Emergency Stop
**POST** `/control/emergency-stop`

### 3.5 Get Status
**GET** `/control/status`

**Response:**
```json
{
  "success": true,
  "data": {
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
    "emergency_stop": false
  }
}
```

### 3.6 Health Check
**GET** `/control/health`

---

## 4. Junction Management APIs (`/junctions`)

### 4.1 List Junctions
**GET** `/junctions?page=1&page_size=10&status=online&zone=Zone A`

**Response:**
```json
{
  "junctions": [
    {
      "id": 1,
      "name": "Main Square Junction",
      "location": "Main Square, Downtown",
      "ip_address": "192.168.1.100",
      "device_id": "RPI-001",
      "status": "online",
      "last_seen": "2024-01-15T10:30:00",
      "description": "Primary junction",
      "zone": "Zone A",
      "config_metadata": null,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 3,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

### 4.2 Get Junction by ID
**GET** `/junctions/{id}`

### 4.3 Create Junction
**POST** `/junctions`

**Request:**
```json
{
  "name": "New Junction",
  "location": "North Gate",
  "ip_address": "192.168.1.105",
  "device_id": "RPI-005",
  "description": "New junction",
  "zone": "Zone B"
}
```

### 4.4 Update Junction
**PUT** `/junctions/{id}`

### 4.5 Delete Junction
**DELETE** `/junctions/{id}`

### 4.6 Update Junction Status
**PATCH** `/junctions/{id}/status`

**Request:**
```json
{
  "status": "maintenance"
}
```

### 4.7 Heartbeat
**POST** `/junctions/{id}/heartbeat`

### 4.8 Get Junction Statistics
**GET** `/junctions/stats/overview`

**Response:**
```json
{
  "total_junctions": 3,
  "online_junctions": 2,
  "offline_junctions": 1,
  "maintenance_junctions": 0,
  "error_junctions": 0,
  "junctions_by_zone": {
    "Zone A": 2,
    "Zone B": 1
  },
  "junctions_by_status": {
    "online": 2,
    "offline": 1
  }
}
```

### 4.9 Check Offline Junctions
**GET** `/junctions/offline/check?threshold_minutes=5`

---

## 5. Command Execution APIs (`/commands`)

### 5.1 Send Command
**POST** `/commands/send`

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
    "timestamp": "2024-01-15T10:30:00"
  },
  "executed_at": "2024-01-15T10:30:00"
}
```

### 5.2 Get Command by ID
**GET** `/commands/{id}`

### 5.3 List Commands
**GET** `/commands?page=1&page_size=10&junction_id=1&command_type=set_mode&status=success`

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

### 5.4 Retry Command
**POST** `/commands/{id}/retry`

**Request:**
```json
{
  "force": false
}
```

### 5.5 Cancel Command
**POST** `/commands/{id}/cancel`

### 5.6 Get Command Statistics
**GET** `/commands/stats/overview`

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
    "vip_mode": 100
  },
  "commands_by_junction": {
    "1": 500,
    "2": 300
  },
  "average_execution_time": 1.5
}
```

### 5.7 Get Pending Commands (Admin Only)
**GET** `/commands/pending/list?limit=100`

---

## Command Types

| Type | Description | Payload Example |
|------|-------------|-----------------|
| `set_mode` | Switch traffic mode | `{"mode": "auto"}` |
| `set_time` | Set lane timings | `{"lane1": 30, "lane2": 45, "lane3": 30, "lane4": 45}` |
| `vip_mode` | VIP override | `{"active": true, "lanes_to_green": [1, 3]}` |
| `emergency_stop` | Emergency stop | `{}` |
| `heartbeat` | Health check | `{}` |
| `get_status` | Get status | `{}` |

---

## System Modes

| Mode | Description |
|------|-------------|
| `manual` | Manual control |
| `auto_circle` | Automatic circular rotation |
| `auto_jump` | Intelligent auto mode |
| `blinker` | Yellow blinker mode |
| `vip` | VIP/emergency vehicle mode |

---

## Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Server Error |

---

## Authentication

All endpoints (except `/auth/login` and `/auth/register`) require JWT authentication:

```
Authorization: Bearer {access_token}
```

**Token Expiration:**
- Access Token: 30 minutes
- Refresh Token: 7 days
