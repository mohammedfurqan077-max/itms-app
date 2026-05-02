# ITMS System Flow Diagrams

## 🔐 Authentication Flow

```
┌─────────────┐
│   Client    │
│ (Mobile/Web)│
└──────┬──────┘
       │
       │ 1. POST /api/v1/auth/login
       │    { email, password }
       ▼
┌─────────────────────────────────────┐
│         FastAPI Backend             │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Auth Endpoint               │  │
│  │  - Validate request schema   │  │
│  │  - Rate limit check          │  │
│  └────────────┬─────────────────┘  │
│               │                     │
│               ▼                     │
│  ┌──────────────────────────────┐  │
│  │  Auth Service                │  │
│  │  - Get user by email         │  │
│  │  - Verify password           │  │
│  │  - Check account status      │  │
│  │  - Check login attempts      │  │
│  │  - Generate JWT tokens       │  │
│  │  - Create session record     │  │
│  └────────────┬─────────────────┘  │
│               │                     │
│               ▼                     │
│  ┌──────────────────────────────┐  │
│  │  Database                    │  │
│  │  - users table               │  │
│  │  - sessions table            │  │
│  └──────────────────────────────┘  │
│                                     │
└──────────────┬──────────────────────┘
               │
               │ 2. Response
               │    { access_token, refresh_token, user }
               ▼
       ┌──────────────┐
       │   Client     │
       │ Stores tokens│
       └──────────────┘
```

---

## 🔒 Authorization Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ 1. Request with JWT
       │    Authorization: Bearer <token>
       ▼
┌─────────────────────────────────────┐
│         FastAPI Backend             │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Dependency: get_current_user│  │
│  │  - Extract token from header │  │
│  │  - Decode JWT                │  │
│  │  - Verify signature          │  │
│  │  - Check expiration          │  │
│  │  - Get user from database    │  │
│  │  - Check user status         │  │
│  └────────────┬─────────────────┘  │
│               │                     │
│               ▼                     │
│  ┌──────────────────────────────┐  │
│  │  Dependency: require_permission│
│  │  - Check user role           │  │
│  │  - Check specific permission │  │
│  │  - Allow or deny             │  │
│  └────────────┬─────────────────┘  │
│               │                     │
│               ▼                     │
│  ┌──────────────────────────────┐  │
│  │  Endpoint Handler            │  │
│  │  - Execute business logic    │  │
│  └──────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

---

## 🚦 Signal Control Flow (Manual Mode)

```
┌─────────────┐
│   Mobile    │
│     App     │
└──────┬──────┘
       │
       │ 1. Set Manual Mode
       │    POST /api/v1/signals/manual
       │    { junction_id: 1, lane1: 30, lane2: 45, ... }
       │    Authorization: Bearer <token>
       ▼
┌──────────────────────────────────────────────────────┐
│                  FastAPI Backend                     │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │  Signal Endpoint                               │ │
│  │  - Validate request schema                     │ │
│  │  - Check authentication (JWT)                  │ │
│  │  - Check permission (set_time)                 │ │
│  └─────────────────────┬──────────────────────────┘ │
│                        │                             │
│                        ▼                             │
│  ┌────────────────────────────────────────────────┐ │
│  │  Signal Service                                │ │
│  │  - Validate timings (total cycle, min/max)    │ │
│  │  - Check junction exists and online           │ │
│  │  - Check user has access to junction         │ │
│  │  - Get current junction state                 │ │
│  └─────────────────────┬──────────────────────────┘ │
│                        │                             │
│                        ▼                             │
│  ┌────────────────────────────────────────────────┐ │
│  │  Command Service                               │ │
│  │  - Create command record (status: pending)    │ │
│  │  - Add to command queue                       │ │
│  └─────────────────────┬──────────────────────────┘ │
│                        │                             │
│                        ▼                             │
│  ┌────────────────────────────────────────────────┐ │
│  │  Junction Client                               │ │
│  │  - Send HTTP/TCP request to junction IP      │ │
│  │  - Retry with exponential backoff            │ │
│  │  - Handle timeout                             │ │
│  └─────────────────────┬──────────────────────────┘ │
│                        │                             │
└────────────────────────┼─────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Junction Controller │
              │  (Hardware Device)   │
              │  - Receive command   │
              │  - Execute command   │
              │  - Send ACK/NACK     │
              └──────────┬───────────┘
                         │
                         │ Response
                         ▼
┌──────────────────────────────────────────────────────┐
│                  FastAPI Backend                     │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │  Command Service (continued)                   │ │
│  │  - Update command status (success/failed)     │ │
│  │  - Update junction state in database          │ │
│  └─────────────────────┬──────────────────────────┘ │
│                        │                             │
│                        ▼                             │
│  ┌────────────────────────────────────────────────┐ │
│  │  Log Service                                   │ │
│  │  - Create audit log entry                     │ │
│  │  - Record: user, junction, action, result     │ │
│  └─────────────────────┬──────────────────────────┘ │
│                        │                             │
│                        ▼                             │
│  ┌────────────────────────────────────────────────┐ │
│  │  WebSocket Service                             │ │
│  │  - Broadcast mode change to connected clients │ │
│  │  - Send to admin dashboard                    │ │
│  │  - Send to other mobile users                 │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
└──────────────────────┬───────────────────────────────┘
                       │
                       │ 2. Response
                       │    { success: true, state: {...} }
                       ▼
               ┌──────────────┐
               │  Mobile App  │
               │ Update UI    │
               └──────────────┘
```

---

## 🚨 VIP Mode Flow

```
┌─────────────┐
│   Mobile    │
│     App     │
└──────┬──────┘
       │
       │ 1. Activate VIP Mode
       │    POST /api/v1/signals/vip
       │    { junction_id: 1, lane: 2, duration: 300 }
       ▼
┌──────────────────────────────────────┐
│         FastAPI Backend              │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  Signal Service                │ │
│  │  - Check vip_mode permission   │ │
│  │  - Validate lane number        │ │
│  │  - Set VIP mode on junction    │ │
│  │  - Schedule auto-revert        │ │
│  └────────────┬───────────────────┘ │
│               │                      │
│               ▼                      │
│  ┌────────────────────────────────┐ │
│  │  Background Task               │ │
│  │  - Wait for duration           │ │
│  │  - Auto-revert to previous mode│ │
│  └────────────────────────────────┘ │
│                                      │
└──────────────────────────────────────┘
```

---

## 📊 Real-time Updates (WebSocket)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Mobile 1   │     │  Mobile 2   │     │   Admin     │
│             │     │             │     │  Dashboard  │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │ 1. Connect        │                   │
       │ WS /api/v1/ws     │                   │
       ▼                   ▼                   ▼
┌────────────────────────────────────────────────────┐
│              WebSocket Manager                     │
│  - Authenticate connection (JWT)                   │
│  - Store connection in active connections          │
│  - Subscribe to channels (junction updates, etc.)  │
└────────────────────┬───────────────────────────────┘
                     │
                     │ 2. Event occurs
                     │    (mode change, junction offline, etc.)
                     │
                     ▼
┌────────────────────────────────────────────────────┐
│              WebSocket Manager                     │
│  - Broadcast to all connected clients              │
│  - Filter by subscription                          │
│  - Send event data                                 │
└────────────────────┬───────────────────────────────┘
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Mobile 1 │  │ Mobile 2 │  │  Admin   │
│ Update UI│  │ Update UI│  │ Update UI│
└──────────┘  └──────────┘  └──────────┘
```

---

## 🗄️ Database Relationships

```
┌──────────────┐
│    users     │
│──────────────│
│ id (PK)      │
│ email        │
│ password_hash│
│ role         │
│ status       │
└──────┬───────┘
       │
       │ 1:N
       │
       ▼
┌──────────────────┐
│ user_permissions │
│──────────────────│
│ user_id (FK)     │
│ permission_id(FK)│
└──────┬───────────┘
       │
       │ N:1
       │
       ▼
┌──────────────┐
│ permissions  │
│──────────────│
│ id (PK)      │
│ name         │
│ description  │
└──────────────┘

┌──────────────┐
│    users     │
└──────┬───────┘
       │
       │ 1:N
       │
       ▼
┌──────────────┐
│   sessions   │
│──────────────│
│ id (PK)      │
│ user_id (FK) │
│ token        │
│ ip_address   │
│ user_agent   │
│ last_seen    │
└──────────────┘

┌──────────────┐
│  junctions   │
│──────────────│
│ id (PK)      │
│ name         │
│ ip_address   │
│ zone         │
│ status       │
└──────┬───────┘
       │
       │ 1:1
       │
       ▼
┌──────────────────┐
│ junction_states  │
│──────────────────│
│ id (PK)          │
│ junction_id (FK) │
│ current_mode     │
│ lane1_time       │
│ lane2_time       │
│ lane3_time       │
│ lane4_time       │
│ updated_at       │
└──────────────────┘

┌──────────────┐     ┌──────────────┐
│    users     │     │  junctions   │
└──────┬───────┘     └──────┬───────┘
       │                    │
       │                    │
       └────────┬───────────┘
                │
                │ N:N
                │
                ▼
┌──────────────────────────┐
│      audit_logs          │
│──────────────────────────│
│ id (PK)                  │
│ user_id (FK)             │
│ junction_id (FK)         │
│ action                   │
│ previous_state           │
│ new_state                │
│ result                   │
│ ip_address               │
│ timestamp                │
└──────────────────────────┘
```

---

## 🔄 Command Queue Processing

```
┌─────────────────────────────────────────────────┐
│              Command Queue                      │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Command 1│  │ Command 2│  │ Command 3│ ... │
│  │ pending  │  │ pending  │  │ pending  │     │
│  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────┬───────────────────────────┘
                      │
                      │ Background Worker
                      │ (Celery/RQ or async task)
                      ▼
        ┌─────────────────────────────┐
        │  Command Processor          │
        │  1. Pick pending command    │
        │  2. Update status: processing│
        │  3. Send to junction        │
        │  4. Retry if failed         │
        │  5. Update status: success  │
        │     or failed               │
        └─────────────────────────────┘
```

---

## 📈 Request Lifecycle

```
1. HTTP Request arrives
   ↓
2. CORS Middleware
   ↓
3. Trusted Host Middleware
   ↓
4. Rate Limiting
   ↓
5. Request Timing (start)
   ↓
6. Route Matching
   ↓
7. Dependency Injection
   - Database session
   - Current user (JWT validation)
   - Permissions check
   ↓
8. Request Validation (Pydantic)
   ↓
9. Endpoint Handler
   ↓
10. Service Layer
    - Business logic
    - Database operations
    - External calls
    ↓
11. Response Serialization (Pydantic)
    ↓
12. Request Timing (end)
    ↓
13. Logging
    ↓
14. HTTP Response
```

---

## 🔍 Error Handling Flow

```
┌─────────────┐
│   Request   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Try: Execute       │
│  - Validate         │
│  - Process          │
│  - Respond          │
└──────┬──────────────┘
       │
       │ Exception?
       │
       ├─ ITMSException ──────────┐
       │                          │
       ├─ ValidationError ─────────┤
       │                          │
       ├─ JunctionException ───────┤
       │                          │
       └─ General Exception ───────┤
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │  Exception Handler       │
                    │  - Log error             │
                    │  - Format response       │
                    │  - Set status code       │
                    │  - Return JSON           │
                    └──────────┬───────────────┘
                               │
                               ▼
                    ┌──────────────────────────┐
                    │  Error Response          │
                    │  {                       │
                    │    success: false,       │
                    │    error: "message",     │
                    │    error_code: "CODE"    │
                    │  }                       │
                    └──────────────────────────┘
```

---

## 🎯 Summary

These diagrams show:
1. **Authentication**: How users log in and get tokens
2. **Authorization**: How requests are validated
3. **Signal Control**: Complete flow from user to junction
4. **VIP Mode**: Emergency vehicle handling
5. **WebSocket**: Real-time updates
6. **Database**: Table relationships
7. **Command Queue**: Async command processing
8. **Request Lifecycle**: Complete request flow
9. **Error Handling**: Exception management

All flows are designed for **production use** with proper error handling, retry logic, and audit trails.
