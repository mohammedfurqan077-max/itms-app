# SystemState Module - Implementation Guide

## 🎯 Overview

The SystemState module implements a **singleton pattern** to track the current global traffic system mode. This ensures a single source of truth for the system's operational state.

---

## 📦 What Was Implemented

### 1. Database Model ✅
**File:** `app/models/system_state.py`

**SystemState Model (Singleton):**
- `id` - Always 1 (singleton)
- `current_mode` - Current system mode (manual, auto_circle, auto_jump, blinker, vip)
- `last_updated_by` - User ID who last updated the state
- `junction_id` - Optional junction ID for junction-specific modes
- `mode_metadata` - JSON metadata for mode configuration
- `updated_at` - Last update timestamp
- `created_at` - Creation timestamp

**Relationships:**
- `updated_by_user` - User who last updated (eager loaded)
- `junction` - Junction if mode is junction-specific (eager loaded)

### 2. Pydantic Schemas ✅
**File:** `app/schemas/system_state.py`

**Schemas:**
- `SystemStateResponse` - System state with nested user/junction info
- `UpdateSystemStateRequest` - Request to update mode
- `UpdateSystemStateResponse` - Response with previous and current mode
- `SystemModeEnum` - Valid system modes enumeration

**Valid Modes:**
- `manual` - Manual control
- `auto_circle` - Automatic circular rotation
- `auto_jump` - Intelligent auto mode
- `blinker` - Yellow blinker mode
- `vip` - VIP/emergency vehicle mode

### 3. Business Logic ✅
**File:** `app/services/system_state_service.py`

**Methods:**
- `get_system_state()` - Get current state (creates default if not exists)
- `update_system_state()` - Update state with transaction safety
- `get_current_mode()` - Get just the mode string
- `is_mode_active()` - Check if specific mode is active
- `reset_to_default()` - Reset to manual mode
- `get_state_with_details()` - Get state with user/junction details

**Features:**
- Singleton pattern enforcement
- Automatic default state creation
- Transaction safety
- Previous mode tracking
- Comprehensive logging

### 4. API Endpoints ✅
**File:** `app/api/v1/endpoints/system.py`

**Endpoints:**
- `GET /api/v1/system/state` - Get current system state
- `POST /api/v1/system/mode/{mode}` - Update mode (path param)
- `POST /api/v1/system/mode` - Update mode (body)
- `POST /api/v1/system/reset` - Reset to default mode
- `GET /api/v1/system/mode` - Get current mode only

### 5. Database Migration ✅
**File:** `alembic/versions/002_add_system_state.py`

**Creates:**
- `junctions` table (minimal placeholder)
- `system_state` table (singleton)
- Check constraint to enforce singleton (id = 1)
- Default system state row

---

## 🔐 Security & Access Control

### Authentication Required
All endpoints require valid JWT token.

### Authorization
- **GET endpoints**: Any authenticated user
- **POST endpoints**: Admin role only (`require_role(UserRole.ADMIN)`)

---

## 🚀 Quick Start

### 1. Run Migration
```bash
cd backend
alembic upgrade head
```

**Output:**
```
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, Add system_state table
```

### 2. Verify Default State
```bash
# Using Docker
docker-compose exec postgres psql -U itms_user -d itms_db -c "SELECT * FROM system_state;"

# Expected output:
 id | current_mode | last_updated_by | junction_id | mode_metadata | updated_at | created_at
----+--------------+-----------------+-------------+---------------+------------+------------
  1 | manual       |                 |             |               | ...        | ...
```

### 3. Test Endpoints
```bash
# Login as admin
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@itms.com","password":"admin123"}' \
  | jq -r '.tokens.access_token')

# Get current state
curl -X GET "http://localhost:8000/api/v1/system/state" \
  -H "Authorization: Bearer $TOKEN"

# Update mode
curl -X POST "http://localhost:8000/api/v1/system/mode/auto_circle" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_mode":"auto_circle","junction_id":null,"mode_metadata":null}'
```

---

## 📊 API Endpoints Details

### 1. Get System State
```http
GET /api/v1/system/state
Authorization: Bearer {token}
```

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
  "updated_by_name": "System Administrator",
  "junction_name": null
}
```

### 2. Update Mode (Path Parameter)
```http
POST /api/v1/system/mode/{mode}
Authorization: Bearer {token}
Content-Type: application/json

{
  "new_mode": "auto_circle",
  "junction_id": null,
  "mode_metadata": null
}
```

**Response:**
```json
{
  "success": true,
  "message": "System mode updated from 'manual' to 'auto_circle'",
  "previous_mode": "manual",
  "current_mode": "auto_circle",
  "system_state": {
    "id": 1,
    "current_mode": "auto_circle",
    "last_updated_by": 1,
    "junction_id": null,
    "mode_metadata": null,
    "updated_at": "2024-01-15T10:35:00",
    "created_at": "2024-01-01T00:00:00",
    "updated_by_name": "System Administrator",
    "junction_name": null
  }
}
```

### 3. Update Mode (Body)
```http
POST /api/v1/system/mode
Authorization: Bearer {token}
Content-Type: application/json

{
  "new_mode": "vip",
  "junction_id": 5,
  "mode_metadata": "{\"lane\": 2, \"duration\": 300}"
}
```

### 4. Reset to Default
```http
POST /api/v1/system/reset
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "message": "System reset to default mode from 'auto_circle'",
  "previous_mode": "auto_circle",
  "current_mode": "manual",
  "system_state": {...}
}
```

### 5. Get Current Mode Only
```http
GET /api/v1/system/mode
Authorization: Bearer {token}
```

**Response:**
```json
{
  "current_mode": "manual"
}
```

---

## 🔄 Usage Flow Example

### Typical Control Action Flow

```python
from app.services.system_state_service import SystemStateService
from app.core.logging import logger

async def switch_to_auto_mode(
    db: AsyncSession,
    user: User
):
    """Example: Switch to auto circle mode"""
    
    system_state_service = SystemStateService(db)
    
    # 1. Get current state
    current_state = await system_state_service.get_system_state()
    logger.info(f"Current mode: {current_state.current_mode}")
    
    # 2. Store previous mode
    previous_mode = current_state.current_mode
    
    # 3. Perform control action (e.g., send command to junctions)
    try:
        # await control_service.switch_mode("auto_circle")
        pass
    except Exception as e:
        logger.error(f"Failed to switch mode: {e}")
        raise
    
    # 4. If success, update system state
    updated_state, prev_mode = await system_state_service.update_system_state(
        new_mode="auto_circle",
        user_id=user.id
    )
    
    # 5. Log the change
    logger.info(
        f"Mode changed: {prev_mode} → {updated_state.current_mode}",
        extra={
            "user_id": user.id,
            "previous_mode": prev_mode,
            "new_mode": updated_state.current_mode
        }
    )
    
    return updated_state
```

---

## 🧪 Testing

### Manual Testing

#### 1. Test Default State Creation
```bash
# Check if default state exists
curl -X GET "http://localhost:8000/api/v1/system/state" \
  -H "Authorization: Bearer $TOKEN"

# Should return manual mode
```

#### 2. Test Mode Update (Admin)
```bash
# Login as admin
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@itms.com","password":"admin123"}' \
  | jq -r '.tokens.access_token')

# Update to auto_circle
curl -X POST "http://localhost:8000/api/v1/system/mode/auto_circle" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_mode":"auto_circle"}'

# Verify change
curl -X GET "http://localhost:8000/api/v1/system/state" \
  -H "Authorization: Bearer $TOKEN"
```

#### 3. Test Authorization (Jawan - Should Fail)
```bash
# Login as jawan
JAWAN_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"jawan@itms.com","password":"jawan123"}' \
  | jq -r '.tokens.access_token')

# Try to update mode (should fail with 403)
curl -X POST "http://localhost:8000/api/v1/system/mode/manual" \
  -H "Authorization: Bearer $JAWAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_mode":"manual"}'

# Expected: 403 Forbidden
```

#### 4. Test Invalid Mode
```bash
# Try invalid mode
curl -X POST "http://localhost:8000/api/v1/system/mode/invalid_mode" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_mode":"invalid_mode"}'

# Expected: 422 Validation Error
```

#### 5. Test Reset
```bash
# Reset to default
curl -X POST "http://localhost:8000/api/v1/system/reset" \
  -H "Authorization: Bearer $TOKEN"

# Verify reset
curl -X GET "http://localhost:8000/api/v1/system/mode" \
  -H "Authorization: Bearer $TOKEN"

# Should return: {"current_mode": "manual"}
```

### Using Swagger UI

1. Open http://localhost:8000/api/docs
2. Authorize with admin token
3. Try `/api/v1/system/state` - GET current state
4. Try `/api/v1/system/mode/{mode}` - Update mode
5. Try `/api/v1/system/reset` - Reset to default

---

## 🗄️ Database Schema

### system_state Table
```sql
CREATE TABLE system_state (
    id INTEGER PRIMARY KEY DEFAULT 1,
    current_mode VARCHAR(50) NOT NULL DEFAULT 'manual',
    last_updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    junction_id INTEGER REFERENCES junctions(id) ON DELETE SET NULL,
    mode_metadata TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT singleton_check CHECK (id = 1)
);
```

**Singleton Enforcement:**
- Check constraint: `id = 1`
- Only one row can exist
- Default row inserted during migration

---

## 🔒 Singleton Pattern Implementation

### Why Singleton?
- **Single source of truth** for system state
- **Prevents conflicts** from multiple state records
- **Simplifies queries** (always id = 1)
- **Ensures consistency** across the system

### How It Works

#### 1. Database Level
```sql
-- Check constraint ensures only id = 1
CONSTRAINT singleton_check CHECK (id = 1)

-- Default row inserted
INSERT INTO system_state (id, current_mode) VALUES (1, 'manual');
```

#### 2. Model Level
```python
class SystemState(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    
    @classmethod
    def get_singleton_id(cls) -> int:
        return 1
```

#### 3. Service Level
```python
async def get_system_state(self) -> SystemState:
    # Always query id = 1
    result = await self.db.execute(
        select(SystemState).where(SystemState.id == SystemState.get_singleton_id())
    )
    state = result.scalar_one_or_none()
    
    # Create default if not exists
    if not state:
        state = await self._create_default_state()
    
    return state
```

---

## 📝 Integration with Other Modules

### Example: Signal Control Integration

```python
from app.services.system_state_service import SystemStateService

@router.post("/signals/manual")
async def set_manual_mode(
    request: ManualModeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("set_time"))
):
    """Set manual signal mode"""
    
    system_state_service = SystemStateService(db)
    
    # 1. Get current state
    current_state = await system_state_service.get_system_state()
    previous_mode = current_state.current_mode
    
    # 2. Perform control action
    signal_service = SignalService(db)
    result = await signal_service.set_manual_timings(request)
    
    # 3. Update system state
    if result.success:
        await system_state_service.update_system_state(
            new_mode="manual",
            user_id=current_user.id,
            junction_id=request.junction_id
        )
    
    # 4. Log action
    await log_service.create_log(
        user_id=current_user.id,
        action="set_manual_mode",
        previous_state=previous_mode,
        new_state="manual",
        result="success" if result.success else "failed"
    )
    
    return result
```

---

## ✅ Testing Checklist

### Functionality
- [ ] Default state created on first access
- [ ] Get current state works
- [ ] Update mode works (admin)
- [ ] Update mode fails (non-admin)
- [ ] Invalid mode rejected
- [ ] Reset to default works
- [ ] Previous mode tracked correctly
- [ ] User tracking works
- [ ] Junction ID stored correctly
- [ ] Metadata stored correctly

### Security
- [ ] Authentication required for all endpoints
- [ ] Admin role required for updates
- [ ] Jawan cannot update mode
- [ ] Token validation works

### Database
- [ ] Only one row exists (singleton)
- [ ] Cannot insert second row
- [ ] Foreign keys work (user, junction)
- [ ] Timestamps update correctly

---

## 🎯 Summary

### Implemented ✅
- ✅ SystemState model (singleton pattern)
- ✅ Database migration with singleton enforcement
- ✅ SystemStateService with transaction safety
- ✅ 5 API endpoints (GET state, POST mode, POST reset, GET mode)
- ✅ Admin-only authorization
- ✅ Previous mode tracking
- ✅ User and junction tracking
- ✅ Comprehensive logging
- ✅ Error handling
- ✅ Pydantic schemas with validation

### Features ✅
- ✅ Singleton pattern (only one row)
- ✅ Automatic default state creation
- ✅ Transaction safety
- ✅ Mode validation
- ✅ Previous mode tracking
- ✅ User tracking (who updated)
- ✅ Junction tracking (for VIP mode)
- ✅ Metadata support (JSON config)
- ✅ Comprehensive logging

### Ready For ✅
- ✅ Integration with signal control
- ✅ Integration with junction management
- ✅ Integration with audit logging
- ✅ Production deployment

---

**SystemState Module v1.0.0**  
**Status**: Complete ✅  
**Ready**: For Integration 🚀
