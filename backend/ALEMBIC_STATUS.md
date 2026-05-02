# Alembic Database Migrations - Status

## ✅ Alembic is Fully Configured

### Configuration Files
- ✅ `alembic.ini` - Alembic configuration
- ✅ `alembic/env.py` - Environment configuration
- ✅ `alembic/script.py.mako` - Migration template

---

## Migration Files

### Current Migrations (4 files)

#### 1. **001_initial_schema.py**
**Purpose:** Initial database schema

**Creates:**
- `users` table
- `permissions` table
- `user_permissions` table (junction)
- `sessions` table

**Features:**
- User authentication system
- Role-based access control (Admin, Jawan)
- Permission system
- Session tracking

---

#### 2. **002_add_system_state.py**
**Purpose:** Add system state management

**Creates:**
- `system_states` table

**Features:**
- Track current system mode (manual, auto_circle, auto_jump, blinker, vip)
- Track last updated by user
- Track junction-specific modes
- Mode metadata storage

---

#### 3. **003_update_junction_model.py**
**Purpose:** Complete junction management system

**Creates:**
- `junctions` table (full schema)
- 8 indexes for performance

**Features:**
- Junction information (name, location, IP address)
- Device tracking (device_id, status)
- Status management (online, offline, maintenance, error)
- Zone classification
- Configuration metadata
- Last seen tracking

**Sample Data:**
- Main Square Junction (192.168.1.100)
- North Gate Junction (192.168.1.101)
- South Plaza Junction (192.168.1.102)

---

#### 4. **004_add_command_model.py**
**Purpose:** Command execution system for RPi communication

**Creates:**
- `commands` table
- `commandtype` enum (6 types)
- `commandstatus` enum (6 statuses)
- 8 indexes for performance

**Features:**
- Command tracking (type, payload, status)
- Junction association
- User tracking (created_by)
- Retry logic (retry_count, max_retries)
- Timestamps (created_at, executed_at, completed_at)
- Response storage
- Error message storage

**Command Types:**
- SET_MODE - Switch traffic mode
- SET_TIME - Set lane timings
- VIP_MODE - VIP override
- EMERGENCY_STOP - Emergency stop
- HEARTBEAT - Health check
- GET_STATUS - Get status

**Command Statuses:**
- PENDING - Waiting for execution
- EXECUTING - Currently executing
- SUCCESS - Executed successfully
- FAILED - Execution failed
- TIMEOUT - Execution timed out
- CANCELLED - Cancelled before execution

---

## Migration Chain

```
001_initial_schema
    ↓
002_add_system_state
    ↓
003_update_junction_model
    ↓
004_add_command_model (LATEST)
```

---

## How to Use Alembic

### Check Current Version
```bash
cd backend
alembic current
```

### View Migration History
```bash
alembic history
```

### Upgrade to Latest
```bash
alembic upgrade head
```

### Upgrade One Step
```bash
alembic upgrade +1
```

### Downgrade One Step
```bash
alembic downgrade -1
```

### Downgrade to Specific Version
```bash
alembic downgrade 003
```

### Create New Migration
```bash
alembic revision --autogenerate -m "description"
```

---

## Database Schema Overview

### Tables Created (7 tables)

1. **users** - User accounts
   - id, name, email, password_hash, role, status
   - created_at, updated_at, last_login

2. **permissions** - Available permissions
   - id, name, description

3. **user_permissions** - User-permission mapping
   - user_id, permission_id

4. **sessions** - Active user sessions
   - id, user_id, refresh_token, ip_address, user_agent
   - created_at, expires_at, last_seen

5. **system_states** - System state tracking
   - id, current_mode, last_updated_by, junction_id
   - mode_metadata, updated_at, created_at

6. **junctions** - Traffic junctions
   - id, name, location, ip_address, device_id
   - status, last_seen, description, zone
   - config_metadata, created_at, updated_at

7. **commands** - Command execution tracking
   - id, junction_id, command_type, payload
   - status, response, error_message, created_by
   - retry_count, max_retries
   - created_at, executed_at, completed_at

---

## Enums Created (4 enums)

1. **UserRole** - admin, jawan
2. **JunctionStatus** - online, offline, maintenance, error
3. **CommandType** - set_mode, set_time, vip_mode, emergency_stop, heartbeat, get_status
4. **CommandStatus** - pending, executing, success, failed, timeout, cancelled

---

## Indexes Created (20+ indexes)

### Users Table
- Primary key (id)
- Unique email
- Role index
- Status index

### Junctions Table
- Primary key (id)
- Unique name
- Unique ip_address
- Unique device_id
- Status index
- Zone index
- Composite (status, zone)
- Last seen index

### Commands Table
- Primary key (id)
- Junction ID index
- Command type index
- Status index
- Created by index
- Created at index
- Composite (junction_id, status)
- Composite (command_type, status)

---

## Foreign Keys

### Commands Table
- `junction_id` → `junctions.id` (ON DELETE SET NULL)
- `created_by` → `users.id` (ON DELETE SET NULL)

### System States Table
- `last_updated_by` → `users.id` (ON DELETE SET NULL)
- `junction_id` → `junctions.id` (ON DELETE SET NULL)

### User Permissions Table
- `user_id` → `users.id` (ON DELETE CASCADE)
- `permission_id` → `permissions.id` (ON DELETE CASCADE)

### Sessions Table
- `user_id` → `users.id` (ON DELETE CASCADE)

---

## Running Migrations

### First Time Setup

1. **Ensure PostgreSQL is running**
```bash
# Check if database exists
psql -U postgres -c "\l"

# Create database if needed
createdb itms_db
```

2. **Update .env file**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/itms_db
```

3. **Run migrations**
```bash
cd backend
alembic upgrade head
```

4. **Verify**
```bash
alembic current
# Should show: 004 (head)
```

---

## Migration Status

### ✅ All Migrations Created
- [x] 001_initial_schema.py
- [x] 002_add_system_state.py
- [x] 003_update_junction_model.py
- [x] 004_add_command_model.py

### 🔲 Database Status
- [ ] Check if database exists
- [ ] Run migrations: `alembic upgrade head`
- [ ] Verify current version: `alembic current`
- [ ] Seed initial data (optional)

---

## Troubleshooting

### Issue: "alembic: command not found"
**Solution:**
```bash
pip install alembic
```

### Issue: "Can't locate revision identified by '004'"
**Solution:**
```bash
# Start fresh
alembic upgrade head
```

### Issue: "Database connection error"
**Solution:**
1. Check PostgreSQL is running
2. Verify DATABASE_URL in .env
3. Check database exists: `psql -U postgres -l`

### Issue: "Table already exists"
**Solution:**
```bash
# Mark current version without running migrations
alembic stamp head
```

---

## Next Steps

### To Apply Migrations

1. **Start PostgreSQL**
```bash
# Using Docker
docker-compose up -d postgres

# Or start local PostgreSQL service
```

2. **Run Migrations**
```bash
cd backend
alembic upgrade head
```

3. **Verify**
```bash
alembic current
# Expected output: 004 (head)
```

4. **Seed Data (Optional)**
```bash
python scripts/seed_data.py
```

---

## Summary

✅ **Alembic is fully configured**
- 4 migration files created
- All tables defined
- All relationships configured
- All indexes created
- Ready to run

🔲 **Next Action Required**
- Run `alembic upgrade head` to apply migrations to database

---

**Status:** Migrations ready, waiting for database setup
