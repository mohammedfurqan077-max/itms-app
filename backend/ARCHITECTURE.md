# ITMS Backend Architecture

## 📐 Architecture Overview

The ITMS backend follows **Clean Architecture** principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   Auth     │  │   Users    │  │  Junctions │  ...       │
│  │ Endpoints  │  │ Endpoints  │  │ Endpoints  │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   Auth     │  │   User     │  │  Junction  │  ...       │
│  │  Service   │  │  Service   │  │  Service   │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│         (Business Logic & Validation)                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  Data Access Layer                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │    User    │  │  Junction  │  │  Command   │  ...       │
│  │   Model    │  │   Model    │  │   Model    │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│              (SQLAlchemy ORM Models)                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                       │
└─────────────────────────────────────────────────────────────┘
```

## 🏛️ Layer Responsibilities

### 1. API Layer (`app/api/`)
**Responsibility**: HTTP request/response handling

- Receive HTTP requests
- Validate request data (Pydantic schemas)
- Call appropriate service methods
- Format responses
- Handle HTTP-specific concerns (status codes, headers)
- **NO business logic here**

**Example**:
```python
@router.post("/login")
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    result = await auth_service.authenticate(credentials)
    return result
```

### 2. Service Layer (`app/services/`)
**Responsibility**: Business logic and orchestration

- Implement business rules
- Coordinate between multiple models
- Validate business constraints
- Handle transactions
- Call external services (junction controllers)
- **Core application logic lives here**

**Example**:
```python
class SignalService:
    async def set_manual_mode(self, junction_id, timings, user):
        # 1. Check permissions
        # 2. Validate timings
        # 3. Send command to junction
        # 4. Update database
        # 5. Log action
        # 6. Broadcast via WebSocket
```

### 3. Data Access Layer (`app/models/`)
**Responsibility**: Database schema and ORM

- Define database tables (SQLAlchemy models)
- Relationships between tables
- Database constraints
- **NO business logic here**

### 4. Schema Layer (`app/schemas/`)
**Responsibility**: Data validation and serialization

- Request validation (Pydantic)
- Response serialization
- Type safety
- API documentation

## 🔐 Security Architecture

### Authentication Flow
```
1. User sends credentials → POST /api/v1/auth/login
2. Backend validates credentials
3. Generate JWT tokens (access + refresh)
4. Return tokens to client
5. Client stores tokens securely
6. Client includes access token in Authorization header
7. Backend validates token on each request
8. If expired, client uses refresh token to get new access token
```

### Authorization Flow
```
1. Extract user from JWT token
2. Check user role (Admin vs Jawan)
3. Check specific permissions (if required)
4. Allow or deny request
```

### Permission Enforcement
```python
# In endpoint
@router.post("/signals/manual")
async def set_manual_mode(
    current_user: User = Depends(require_permission("set_time"))
):
    # Only users with "set_time" permission can access
    pass
```

## 🔄 Request Flow Example

### Setting Manual Signal Mode

```
1. Mobile App → POST /api/v1/signals/manual
   Headers: Authorization: Bearer <token>
   Body: { junction_id: 1, lane1: 30, lane2: 45, ... }

2. API Layer (signals.py)
   ↓ Validate request schema
   ↓ Extract current user from token
   ↓ Check permissions

3. Service Layer (signal_service.py)
   ↓ Validate business rules (total cycle time, etc.)
   ↓ Check junction status (online/offline)
   ↓ Create command in database
   ↓ Send command to junction controller

4. Junction Client (junction_client.py)
   ↓ HTTP/TCP request to junction IP
   ↓ Handle retries and timeouts
   ↓ Return success/failure

5. Service Layer (continued)
   ↓ Update junction state in database
   ↓ Create audit log
   ↓ Broadcast update via WebSocket

6. API Layer (continued)
   ↓ Return success response to client
```

## 🗄️ Database Design Principles

### Tables
- **users**: User accounts and roles
- **permissions**: Available permissions
- **user_permissions**: Many-to-many relationship
- **sessions**: Active user sessions
- **junctions**: Traffic junction information
- **junction_states**: Current state of each junction
- **commands**: Command queue and execution status
- **audit_logs**: Immutable audit trail

### Indexing Strategy
- Primary keys (automatic)
- Foreign keys
- Frequently queried fields (email, junction_id)
- Timestamp fields (for log queries)

### Relationships
```
User ←→ UserPermission ←→ Permission
User ←→ Session
User ←→ AuditLog
Junction ←→ JunctionState
Junction ←→ Command
Junction ←→ AuditLog
```

## 🚀 Async Architecture

### Why Async?
- **Non-blocking I/O**: Handle multiple requests concurrently
- **Database operations**: Async SQLAlchemy
- **HTTP requests**: Async junction communication
- **WebSockets**: Real-time updates

### Async Patterns
```python
# Async database query
async def get_user(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

# Async HTTP request to junction
async def send_command(junction_ip: str, command: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://{junction_ip}/command",
            json=command,
            timeout=10.0
        )
        return response.json()
```

## 📡 Junction Communication

### Command Execution Flow
```
1. User action → API endpoint
2. Create Command record (status: pending)
3. Background task picks up command
4. Send to junction controller (HTTP/TCP)
5. Retry with exponential backoff if failed
6. Update Command status (success/failed)
7. Update JunctionState
8. Create AuditLog
9. Broadcast via WebSocket
```

### Retry Strategy
```python
max_retries = 3
backoff = 2  # seconds

for attempt in range(max_retries):
    try:
        response = await send_to_junction(command)
        return response
    except Exception as e:
        if attempt < max_retries - 1:
            await asyncio.sleep(backoff ** attempt)
        else:
            raise JunctionException("Failed after retries")
```

## 🔌 WebSocket Architecture

### Real-time Updates
```
Client connects → WebSocket endpoint
Backend authenticates connection
Client subscribes to channels (junction updates, alerts)
Backend broadcasts events to subscribed clients
```

### Event Types
- `junction_status`: Online/offline status
- `mode_change`: Signal mode changed
- `vip_mode_active`: VIP mode activated
- `alert`: System alerts

## 🧪 Testing Strategy

### Unit Tests
- Test individual functions
- Mock external dependencies
- Fast execution

### Integration Tests
- Test API endpoints
- Use test database
- Test service layer with real database

### E2E Tests
- Test complete user flows
- Test junction communication
- Test WebSocket updates

## 📊 Monitoring & Observability

### Logging
- Structured JSON logs
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Context: user_id, junction_id, action

### Metrics
- Request count
- Response time
- Error rate
- Active connections

### Health Checks
- Database connectivity
- Redis connectivity (if used)
- Junction controller status

## 🔧 Configuration Management

### Environment-based Config
- Development: `.env` file
- Production: Environment variables
- Secrets: Never commit to git

### Config Hierarchy
```
1. Environment variables (highest priority)
2. .env file
3. Default values in code
```

## 🚀 Deployment Architecture

### Production Setup
```
┌─────────────┐
│   Nginx     │  (Reverse proxy, SSL termination)
│   (Port 80) │
└──────┬──────┘
       │
┌──────▼──────┐
│   Uvicorn   │  (ASGI server, multiple workers)
│  (Port 8000)│
└──────┬──────┘
       │
┌──────▼──────┐
│  FastAPI    │  (Application)
│     App     │
└──────┬──────┘
       │
┌──────▼──────┐
│ PostgreSQL  │  (Database)
│  (Port 5432)│
└─────────────┘
```

### Scaling Strategy
- **Horizontal**: Multiple Uvicorn workers
- **Load Balancing**: Nginx upstream
- **Database**: Connection pooling
- **Caching**: Redis for frequently accessed data

## 🔒 Security Best Practices

1. **Never trust client input**: Validate everything
2. **Enforce permissions server-side**: Never rely on frontend
3. **Use HTTPS in production**: Encrypt all traffic
4. **Secure JWT tokens**: Strong secret key, short expiration
5. **Rate limiting**: Prevent abuse
6. **SQL injection prevention**: Use ORM, parameterized queries
7. **CORS configuration**: Whitelist allowed origins
8. **Audit logging**: Track all critical actions

## 📝 Code Organization Principles

### Single Responsibility
Each module has one clear purpose

### Dependency Injection
Use FastAPI's DI system for testability

### Don't Repeat Yourself (DRY)
Extract common logic to utilities

### Separation of Concerns
API ≠ Business Logic ≠ Data Access

### Type Safety
Use type hints everywhere

---

This architecture is designed for **production use** with:
- ✅ Scalability
- ✅ Maintainability
- ✅ Security
- ✅ Performance
- ✅ Testability
