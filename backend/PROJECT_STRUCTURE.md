# ITMS Backend - Complete Project Structure

## 📁 Directory Tree

```
backend/
│
├── 📄 README.md                    # Project overview and setup guide
├── 📄 ARCHITECTURE.md              # Detailed architecture documentation
├── 📄 PROJECT_STRUCTURE.md         # This file
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # Environment variables template
├── 📄 .gitignore                   # Git ignore rules
├── 📄 .dockerignore                # Docker ignore rules
├── 📄 Dockerfile                   # Docker image definition
├── 📄 docker-compose.yml           # Multi-container Docker setup
├── 📄 alembic.ini                  # Alembic configuration
├── 📄 setup.sh                     # Setup script
├── 📄 Makefile                     # Development commands
│
├── 📁 alembic/                     # Database migrations
│   ├── 📄 env.py                   # Alembic environment (async support)
│   ├── 📄 script.py.mako           # Migration template
│   └── 📁 versions/                # Migration files (auto-generated)
│
├── 📁 app/                         # Main application package
│   ├── 📄 __init__.py
│   ├── 📄 main.py                  # FastAPI app entry point
│   │
│   ├── 📁 core/                    # Core application components
│   │   ├── 📄 __init__.py
│   │   ├── 📄 config.py            # Configuration management (Pydantic Settings)
│   │   ├── 📄 security.py          # JWT, password hashing, token management
│   │   ├── 📄 dependencies.py      # FastAPI dependencies (auth, permissions)
│   │   ├── 📄 exceptions.py        # Custom exception classes
│   │   ├── 📄 logging.py           # Structured logging configuration
│   │   └── 📄 rate_limit.py        # Rate limiting setup
│   │
│   ├── 📁 db/                      # Database layer
│   │   ├── 📄 __init__.py
│   │   ├── 📄 base.py              # SQLAlchemy declarative base
│   │   └── 📄 session.py           # Async session management
│   │
│   ├── 📁 models/                  # SQLAlchemy ORM models
│   │   ├── 📄 __init__.py          # Import all models
│   │   ├── 📄 user.py              # User, Permission, UserPermission, Session
│   │   ├── 📄 junction.py          # Junction, JunctionState
│   │   ├── 📄 command.py           # Command queue
│   │   └── 📄 log.py               # AuditLog
│   │
│   ├── 📁 schemas/                 # Pydantic schemas (request/response)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 user.py              # User schemas
│   │   ├── 📄 auth.py              # Auth schemas (login, token)
│   │   ├── 📄 junction.py          # Junction schemas
│   │   ├── 📄 signal.py            # Signal control schemas
│   │   └── 📄 log.py               # Log schemas
│   │
│   ├── 📁 api/                     # API endpoints
│   │   ├── 📄 __init__.py
│   │   └── 📁 v1/                  # API version 1
│   │       ├── 📄 __init__.py
│   │       ├── 📄 router.py        # Main API router
│   │       └── 📁 endpoints/       # Endpoint modules
│   │           ├── 📄 __init__.py
│   │           ├── 📄 auth.py      # Login, register, refresh token
│   │           ├── 📄 users.py     # User CRUD, permissions
│   │           ├── 📄 junctions.py # Junction CRUD, status
│   │           ├── 📄 signals.py   # Signal control (manual, auto, VIP)
│   │           ├── 📄 logs.py      # Audit logs, export
│   │           └── 📄 websocket.py # WebSocket connections
│   │
│   ├── 📁 services/                # Business logic layer
│   │   ├── 📄 __init__.py
│   │   ├── 📄 user_service.py      # User management logic
│   │   ├── 📄 auth_service.py      # Authentication logic
│   │   ├── 📄 junction_service.py  # Junction management logic
│   │   ├── 📄 signal_service.py    # Signal control logic
│   │   ├── 📄 command_service.py   # Command queue processing
│   │   └── 📄 log_service.py       # Audit logging logic
│   │
│   └── 📁 utils/                   # Utility functions
│       ├── 📄 __init__.py
│       ├── 📄 junction_client.py   # HTTP/TCP client for junction communication
│       ├── 📄 validators.py        # Custom validators
│       └── 📄 helpers.py           # Helper functions
│
└── 📁 tests/                       # Test suite (to be created)
    ├── 📄 conftest.py              # Pytest configuration
    ├── 📁 unit/                    # Unit tests
    └── 📁 integration/             # Integration tests
```

## 📦 Key Files Explained

### Configuration & Setup
| File | Purpose |
|------|---------|
| `requirements.txt` | All Python dependencies |
| `.env.example` | Template for environment variables |
| `alembic.ini` | Database migration configuration |
| `Dockerfile` | Container image definition |
| `docker-compose.yml` | Multi-service orchestration |
| `setup.sh` | Automated setup script |
| `Makefile` | Development shortcuts |

### Core Application
| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app initialization, middleware, exception handlers |
| `app/core/config.py` | Environment-based configuration |
| `app/core/security.py` | JWT tokens, password hashing |
| `app/core/dependencies.py` | Auth dependencies, permission checks |
| `app/core/exceptions.py` | Custom exception classes |
| `app/core/logging.py` | Structured logging setup |

### Database
| File | Purpose |
|------|---------|
| `app/db/base.py` | SQLAlchemy declarative base |
| `app/db/session.py` | Async database session factory |
| `app/models/*.py` | ORM models (tables) |
| `alembic/env.py` | Migration environment (async) |

### API Layer
| File | Purpose |
|------|---------|
| `app/api/v1/router.py` | Aggregates all endpoint routers |
| `app/api/v1/endpoints/auth.py` | Authentication endpoints |
| `app/api/v1/endpoints/users.py` | User management endpoints |
| `app/api/v1/endpoints/junctions.py` | Junction management endpoints |
| `app/api/v1/endpoints/signals.py` | Signal control endpoints |
| `app/api/v1/endpoints/logs.py` | Audit log endpoints |
| `app/api/v1/endpoints/websocket.py` | WebSocket endpoint |

### Business Logic
| File | Purpose |
|------|---------|
| `app/services/auth_service.py` | Login, token generation, validation |
| `app/services/user_service.py` | User CRUD, permission management |
| `app/services/junction_service.py` | Junction CRUD, health checks |
| `app/services/signal_service.py` | Signal mode control, validation |
| `app/services/command_service.py` | Command queue, retry logic |
| `app/services/log_service.py` | Audit logging, export |

### Data Validation
| File | Purpose |
|------|---------|
| `app/schemas/auth.py` | Login request, token response |
| `app/schemas/user.py` | User create/update/response |
| `app/schemas/junction.py` | Junction create/update/response |
| `app/schemas/signal.py` | Signal control requests |
| `app/schemas/log.py` | Log query, response |

## 🔄 Data Flow

### Request → Response Flow
```
1. HTTP Request
   ↓
2. FastAPI Router (app/api/v1/endpoints/*.py)
   ↓
3. Dependency Injection (auth, permissions)
   ↓
4. Schema Validation (app/schemas/*.py)
   ↓
5. Service Layer (app/services/*.py)
   ↓
6. Database Access (app/models/*.py)
   ↓
7. Response Schema
   ↓
8. HTTP Response
```

### Signal Control Flow
```
1. User Action (Mobile/Web)
   ↓
2. API Endpoint (signals.py)
   ↓
3. Permission Check
   ↓
4. Signal Service (signal_service.py)
   ↓
5. Validation (timings, mode)
   ↓
6. Command Service (command_service.py)
   ↓
7. Junction Client (junction_client.py)
   ↓
8. Junction Controller (HTTP/TCP)
   ↓
9. Update Database State
   ↓
10. Audit Log
   ↓
11. WebSocket Broadcast
   ↓
12. Response to User
```

## 🎯 Module Responsibilities

### `app/core/`
**Purpose**: Core application infrastructure
- Configuration management
- Security utilities (JWT, hashing)
- Authentication/authorization dependencies
- Exception definitions
- Logging setup

### `app/db/`
**Purpose**: Database connection management
- Async engine creation
- Session factory
- Connection pooling

### `app/models/`
**Purpose**: Database schema definition
- SQLAlchemy ORM models
- Table relationships
- Database constraints

### `app/schemas/`
**Purpose**: Data validation and serialization
- Request validation
- Response formatting
- Type safety
- API documentation

### `app/api/`
**Purpose**: HTTP interface
- Route definitions
- Request handling
- Response formatting
- HTTP-specific logic

### `app/services/`
**Purpose**: Business logic
- Application rules
- Workflow orchestration
- External service calls
- Transaction management

### `app/utils/`
**Purpose**: Shared utilities
- Junction communication client
- Custom validators
- Helper functions

## 🚀 Getting Started

### Quick Start
```bash
# 1. Run setup script
bash setup.sh

# 2. Update .env file
nano .env

# 3. Create database
createdb itms_db

# 4. Run migrations
alembic upgrade head

# 5. Start server
uvicorn app.main:app --reload
```

### Using Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Using Makefile
```bash
make install    # Install dependencies
make run        # Run dev server
make test       # Run tests
make migrate    # Apply migrations
make format     # Format code
```

## 📝 Next Steps

### Phase 1: Database & Auth ✅
- [x] Project structure
- [x] Core configuration
- [x] Security utilities
- [ ] Database models
- [ ] Authentication endpoints

### Phase 2: User Management
- [ ] User CRUD
- [ ] Permission management
- [ ] Session tracking

### Phase 3: Junction Management
- [ ] Junction CRUD
- [ ] Health monitoring
- [ ] User-junction assignments

### Phase 4: Signal Control
- [ ] Manual mode
- [ ] Auto modes (circle, jump)
- [ ] VIP mode
- [ ] Blinker mode

### Phase 5: Real-time & Logging
- [ ] WebSocket implementation
- [ ] Audit logging
- [ ] Log export

### Phase 6: Testing & Deployment
- [ ] Unit tests
- [ ] Integration tests
- [ ] Production deployment

---

**Status**: Backend architecture complete ✅  
**Next**: Database schema and models
