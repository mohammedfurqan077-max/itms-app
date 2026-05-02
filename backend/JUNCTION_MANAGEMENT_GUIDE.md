## 🚦 Junction Management System - Complete Guide

**Module:** Junction Management  
**Status:** ✅ Implemented  
**Version:** 1.0.0

---

## 📋 Overview

The Junction Management System provides complete CRUD operations for managing traffic junctions. Each junction represents a physical traffic control point managed by a device (e.g., Raspberry Pi).

### Key Features
- ✅ Create, Read, Update, Delete junctions
- ✅ Pagination and filtering
- ✅ Status tracking (online, offline, maintenance, error)
- ✅ Heartbeat system for device monitoring
- ✅ Zone-based organization
- ✅ IP address validation
- ✅ Duplicate prevention
- ✅ Statistics and health monitoring

---

## 📦 Components

### 1. Model (`app/models/junction.py`)
**Junction Model Fields:**
- `id` - Primary key
- `name` - Junction name (unique)
- `location` - Physical location (optional)
- `ip_address` - Device IP address (unique, validated)
- `device_id` - Unique device identifier (optional, unique)
- `status` - Current status (online/offline/maintenance/error)
- `last_seen` - Last heartbeat timestamp
- `description` - Additional notes (optional)
- `zone` - Zone classification (optional)
- `config_metadata` - JSON configuration (optional)
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

**Status Enum:**
- `online` - Junction is operational
- `offline` - Junction is not responding
- `maintenance` - Junction is under maintenance
- `error` - Junction has errors

### 2. Schemas (`app/schemas/junction.py`)
- `JunctionCreate` - Create junction request
- `JunctionUpdate` - Update junction request
- `JunctionResponse` - Junction response
- `JunctionListResponse` - Paginated list response
- `JunctionStatusUpdate` - Status update request
- `JunctionHeartbeat` - Device heartbeat request
- `JunctionStats` - Statistics response

### 3. Service (`app/services/junction_service.py`)
**Methods:**
- `create_junction()` - Create new junction
- `get_junction_by_id()` - Get junction by ID
- `get_junctions()` - Get paginated list with filters
- `update_junction()` - Update junction
- `delete_junction()` - Delete junction
- `update_junction_status()` - Update status
- `process_heartbeat()` - Process device heartbeat
- `get_junction_stats()` - Get statistics
- `check_offline_junctions()` - Check for offline junctions

### 4. API Endpoints (`app/api/v1/endpoints/junctions.py`)
**Routes:**
- `POST /api/v1/junctions` - Create junction (admin)
- `GET /api/v1/junctions` - List junctions (paginated)
- `GET /api/v1/junctions/{id}` - Get junction by ID
- `PUT /api/v1/junctions/{id}` - Update junction (admin)
- `DELETE /api/v1/junctions/{id}` - Delete junction (admin)
- `PATCH /api/v1/junctions/{id}/status` - Update status (admin)
- `POST /api/v1/junctions/heartbeat` - Process heartbeat (device)
- `GET /api/v1/junctions/stats/overview` - Get statistics
- `GET /api/v1/junctions/health/check-offline` - Check offline junctions (admin)

---

## 🔐 Authorization

| Endpoint | Role Required | Permission Required |
|----------|---------------|---------------------|
| Create junction | Admin | - |
| List junctions | Any authenticated | - |
| Get junction | Any authenticated | - |
| Update junction | Admin | - |
| Delete junction | Admin | - |
| Update status | Admin | - |
| Process heartbeat | None (device) | - |
| Get statistics | Any authenticated | - |
| Check offline | Admin | - |

---

## 📝 API Examples

### 1. Create Junction (Admin Only)

**Request:**
```bash
POST /api/v1/junctions
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "name": "Main Square Junction",
  "location": "Main Square, Downtown",
  "ip_address": "192.168.1.100",
  "device_id": "RPI-001",
  "description": "Primary junction at main square",
  "zone": "Zone A",
  "config_metadata": "{\"lanes\": 4, \"has_camera\": true}"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Main Square Junction",
  "location": "Main Square, Downtown",
  "ip_address": "192.168.1.100",
  "device_id": "RPI-001",
  "status": "offline",
  "last_seen": null,
  "description": "Primary junction at main square",
  "zone": "Zone A",
  "config_metadata": "{\"lanes\": 4, \"has_camera\": true}",
  "created_at": "2026-04-30T10:00:00Z",
  "updated_at": "2026-04-30T10:00:00Z"
}
```

### 2. List Junctions (Paginated)

**Request:**
```bash
GET /api/v1/junctions?page=1&page_size=10&status=online&zone=Zone%20A
Authorization: Bearer {token}
```

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
      "last_seen": "2026-04-30T10:05:00Z",
      "description": "Primary junction at main square",
      "zone": "Zone A",
      "config_metadata": "{\"lanes\": 4, \"has_camera\": true}",
      "created_at": "2026-04-30T10:00:00Z",
      "updated_at": "2026-04-30T10:05:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

### 3. Get Junction by ID

**Request:**
```bash
GET /api/v1/junctions/1
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": 1,
  "name": "Main Square Junction",
  "location": "Main Square, Downtown",
  "ip_address": "192.168.1.100",
  "device_id": "RPI-001",
  "status": "online",
  "last_seen": "2026-04-30T10:05:00Z",
  "description": "Primary junction at main square",
  "zone": "Zone A",
  "config_metadata": "{\"lanes\": 4, \"has_camera\": true}",
  "created_at": "2026-04-30T10:00:00Z",
  "updated_at": "2026-04-30T10:05:00Z"
}
```

### 4. Update Junction (Admin Only)

**Request:**
```bash
PUT /api/v1/junctions/1
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "location": "Main Square, Downtown (Updated)",
  "description": "Primary junction at main square - Updated",
  "zone": "Zone B"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Main Square Junction",
  "location": "Main Square, Downtown (Updated)",
  "ip_address": "192.168.1.100",
  "device_id": "RPI-001",
  "status": "online",
  "last_seen": "2026-04-30T10:05:00Z",
  "description": "Primary junction at main square - Updated",
  "zone": "Zone B",
  "config_metadata": "{\"lanes\": 4, \"has_camera\": true}",
  "created_at": "2026-04-30T10:00:00Z",
  "updated_at": "2026-04-30T10:10:00Z"
}
```

### 5. Update Junction Status (Admin Only)

**Request:**
```bash
PATCH /api/v1/junctions/1/status
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "status": "maintenance"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Main Square Junction",
  "location": "Main Square, Downtown",
  "ip_address": "192.168.1.100",
  "device_id": "RPI-001",
  "status": "maintenance",
  "last_seen": "2026-04-30T10:10:00Z",
  "description": "Primary junction at main square",
  "zone": "Zone A",
  "config_metadata": "{\"lanes\": 4, \"has_camera\": true}",
  "created_at": "2026-04-30T10:00:00Z",
  "updated_at": "2026-04-30T10:10:00Z"
}
```

### 6. Delete Junction (Admin Only)

**Request:**
```bash
DELETE /api/v1/junctions/1
Authorization: Bearer {admin_token}
```

**Response:**
```
204 No Content
```

### 7. Process Heartbeat (Device)

**Request:**
```bash
POST /api/v1/junctions/heartbeat
Content-Type: application/json

{
  "device_id": "RPI-001",
  "status": "online",
  "metadata": {
    "cpu_temp": 45.2,
    "uptime": 86400
  }
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Main Square Junction",
  "location": "Main Square, Downtown",
  "ip_address": "192.168.1.100",
  "device_id": "RPI-001",
  "status": "online",
  "last_seen": "2026-04-30T10:15:00Z",
  "description": "Primary junction at main square",
  "zone": "Zone A",
  "config_metadata": "{\"lanes\": 4, \"has_camera\": true}",
  "created_at": "2026-04-30T10:00:00Z",
  "updated_at": "2026-04-30T10:15:00Z"
}
```

### 8. Get Junction Statistics

**Request:**
```bash
GET /api/v1/junctions/stats/overview
Authorization: Bearer {token}
```

**Response:**
```json
{
  "total_junctions": 10,
  "online_junctions": 7,
  "offline_junctions": 2,
  "maintenance_junctions": 1,
  "error_junctions": 0,
  "junctions_by_zone": {
    "Zone A": 5,
    "Zone B": 3,
    "Zone C": 2
  }
}
```

### 9. Check Offline Junctions (Admin Only)

**Request:**
```bash
GET /api/v1/junctions/health/check-offline?timeout_minutes=5
Authorization: Bearer {admin_token}
```

**Response:**
```json
[
  {
    "id": 2,
    "name": "North Gate Junction",
    "location": "North Gate Entrance",
    "ip_address": "192.168.1.101",
    "device_id": "RPI-002",
    "status": "online",
    "last_seen": "2026-04-30T09:50:00Z",
    "description": "Junction at north gate",
    "zone": "Zone B",
    "config_metadata": null,
    "created_at": "2026-04-30T09:00:00Z",
    "updated_at": "2026-04-30T09:50:00Z"
  }
]
```

---

## 🔍 Query Parameters

### List Junctions
- `page` (int, default: 1) - Page number
- `page_size` (int, default: 10, max: 100) - Items per page
- `status` (string, optional) - Filter by status (online/offline/maintenance/error)
- `zone` (string, optional) - Filter by zone
- `search` (string, optional) - Search in name, location, or IP address

### Check Offline Junctions
- `timeout_minutes` (int, default: 5, range: 1-60) - Minutes without heartbeat

---

## ✅ Validation Rules

### IP Address
- Must be valid IPv4 or IPv6 address
- Examples: `192.168.1.100`, `2001:0db8:85a3::8a2e:0370:7334`

### Name
- Length: 2-100 characters
- Must be unique

### Device ID
- Length: max 100 characters
- Must be unique (if provided)

### Status
- Must be one of: `online`, `offline`, `maintenance`, `error`

### Zone
- Length: max 50 characters

---

## 🚨 Error Responses

### Duplicate Junction Name
```json
{
  "success": false,
  "error": "Junction with name 'Main Square Junction' already exists",
  "error_code": "DUPLICATE"
}
```

### Duplicate IP Address
```json
{
  "success": false,
  "error": "Junction with IP address '192.168.1.100' already exists",
  "error_code": "DUPLICATE"
}
```

### Junction Not Found
```json
{
  "success": false,
  "error": "Junction with ID 999 not found",
  "error_code": "NOT_FOUND"
}
```

### Invalid IP Address
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "ip_address"],
      "msg": "Invalid IP address: 999.999.999.999"
    }
  ]
}
```

### Invalid Status
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "status"],
      "msg": "Invalid status: invalid_status. Must be one of: online, offline, maintenance, error"
    }
  ]
}
```

---

## 🔄 Heartbeat System

### Purpose
Devices (Raspberry Pi) send periodic heartbeats to report their status.

### Flow
1. Device sends POST request to `/api/v1/junctions/heartbeat`
2. Backend updates junction status and `last_seen` timestamp
3. Backend returns updated junction information

### Monitoring
- Admin can check for offline junctions using `/api/v1/junctions/health/check-offline`
- Junctions without heartbeat for specified duration are flagged

### Example Device Code (Python)
```python
import requests
import time

BACKEND_URL = "http://localhost:8000/api/v1/junctions/heartbeat"
DEVICE_ID = "RPI-001"

while True:
    try:
        response = requests.post(
            BACKEND_URL,
            json={
                "device_id": DEVICE_ID,
                "status": "online",
                "metadata": {
                    "cpu_temp": get_cpu_temp(),
                    "uptime": get_uptime()
                }
            },
            timeout=10
        )
        print(f"Heartbeat sent: {response.status_code}")
    except Exception as e:
        print(f"Heartbeat failed: {e}")
    
    time.sleep(60)  # Send heartbeat every minute
```

---

## 📊 Database Schema

```sql
CREATE TABLE junctions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(255),
    ip_address VARCHAR(45) NOT NULL UNIQUE,
    device_id VARCHAR(100) UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'offline',
    last_seen TIMESTAMP,
    description TEXT,
    zone VARCHAR(50),
    config_metadata TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_junction_status_zone ON junctions(status, zone);
CREATE INDEX idx_junction_last_seen ON junctions(last_seen);
```

---

## 🧪 Testing

### Test Scenarios
1. ✅ Create junction with valid data
2. ✅ Create junction with duplicate name (should fail)
3. ✅ Create junction with duplicate IP (should fail)
4. ✅ Create junction with invalid IP (should fail)
5. ✅ List junctions with pagination
6. ✅ Filter junctions by status
7. ✅ Filter junctions by zone
8. ✅ Search junctions by name/location/IP
9. ✅ Get junction by ID
10. ✅ Update junction
11. ✅ Update junction status
12. ✅ Delete junction
13. ✅ Process heartbeat
14. ✅ Get statistics
15. ✅ Check offline junctions

---

## 🚀 Future Enhancements

### Planned Features
- [ ] User-to-junction assignments
- [ ] Junction groups
- [ ] Real-time WebSocket updates
- [ ] Junction health metrics
- [ ] Automated offline detection
- [ ] Junction configuration templates
- [ ] Bulk operations
- [ ] Export/import junctions
- [ ] Junction activity logs
- [ ] Device firmware management

---

## 📚 Related Documentation

- [Backend Architecture](ARCHITECTURE.md)
- [API Quick Reference](API_QUICK_REFERENCE.md)
- [System State Guide](SYSTEM_STATE_GUIDE.md)
- [Control Service Guide](CONTROL_SERVICE_GUIDE.md)

---

**Junction Management v1.0.0**  
**Status**: ✅ Complete  
**Quality**: Production-Grade 💎
