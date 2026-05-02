# ITMS Backend - Intelligent Traffic Management System

Production-grade FastAPI backend for traffic signal control and management.

## 🏗️ Architecture Overview

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── __init__.py
│   │
│   ├── core/                   # Core application components
│   │   ├── config.py           # Configuration management
│   │   ├── security.py         # JWT, password hashing
│   │   ├── dependencies.py     # FastAPI dependencies (auth, permissions)
│   │   ├── exceptions.py       # Custom exception classes
│   │   ├── logging.py          # Structured logging
│   │   └── rate_limit.py       # Rate limiting configuration
│   │
│   ├── db/                     # Database layer
│   │   ├── base.py             # SQLAlchemy declarative base
│   │   └── session.py          # Database session management
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── user.py             # User, Permission, Session models
│   │   ├── junction.py         # Junction, JunctionState models
│   │   ├── command.py          # Command queue model
│   │   └── log.py              # Audit log model
│   │
│   ├── schemas/                # Pydantic schemas (request/response)
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── junction.py
│   │   ├── signal.py
│   │   └── log.py
│   │
│   ├── api/                    # API endpoints
│   │   └── v1/
│   │       ├── router.py       # Main API router
│   │       └── endpoints/
│   │           ├── auth.py     # Login, register, refresh token
│   │           ├── users.py    # User management
│   │           ├── junctions.py # Junction management
│   │           ├── signals.py  # Signal control
│   │           ├── logs.py     # Audit logs
│   │           └── websocket.py # WebSocket connections
│   │
│   ├── services/               # Business logic layer
│   │   ├── user_service.py
│   │   ├── auth_service.py
│   │   ├── junction_service.py
│   │   ├── signal_service.py
│   │   ├── command_service.py
│   │   └── log_service.py
│   │
│   └── utils/                  # Utility functions
│       ├── junction_client.py  # HTTP/TCP client for junction communication
│       ├── validators.py       # Custom validators
│       └── helpers.py          # Helper functions
│
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
│
├── tests/                      # Test suite
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── alembic.ini                 # Alembic configuration
└── README.md                   # This file
```

## 🚀 Key Features

### Security
- **JWT Authentication**: Access + Refresh tokens
- **Password Hashing**: bcrypt with configurable rounds
- **Role-Based Access Control (RBAC)**: Admin vs Traffic Operator
- **Permission-Based Features**: Granular permission checks
- **Rate Limiting**: Protect against abuse
- **Session Tracking**: IP, device, last_seen

### Architecture Patterns
- **Clean Architecture**: Separation of concerns
- **Dependency Injection**: FastAPI's DI system
- **Async/Await**: Full async support for I/O operations
- **Repository Pattern**: Service layer abstracts database operations
- **Exception Handling**: Centralized error handling
- **Structured Logging**: JSON logs for production

### Database
- **PostgreSQL**: Production-grade relational database
- **SQLAlchemy 2.0**: Modern async ORM
- **Alembic**: Database migrations
- **Connection Pooling**: Optimized for performance
- **Proper Indexing**: Fast queries

### API Design
- **RESTful**: Standard HTTP methods and status codes
- **Versioned**: `/api/v1/` prefix for future compatibility
- **OpenAPI/Swagger**: Auto-generated documentation
- **Request Validation**: Pydantic schemas
- **Response Models**: Consistent response structure

## 📦 Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis (optional, for caching)

### Setup

1. **Clone and navigate to backend**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Setup database**
```bash
# Create database
createdb itms_db

# Run migrations
alembic upgrade head
```

6. **Run application**
```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🔧 Configuration

Key environment variables (see `.env.example`):

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/itms_db

# JWT
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Security
BCRYPT_ROUNDS=12
MAX_LOGIN_ATTEMPTS=5

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_auth.py
```

## 📚 API Documentation

Once running, access:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## 🔐 Security Considerations

1. **Never commit `.env` file**
2. **Use strong SECRET_KEY in production**
3. **Enable HTTPS in production**
4. **Configure CORS properly**
5. **Use environment-specific settings**
6. **Regular security audits**
7. **Keep dependencies updated**

## 🚀 Deployment

### Docker (Recommended)

```dockerfile
# Dockerfile will be provided
docker build -t itms-backend .
docker run -p 8000:8000 itms-backend
```

### Systemd Service

```ini
# /etc/systemd/system/itms-backend.service
[Unit]
Description=ITMS Backend
After=network.target

[Service]
User=itms
WorkingDirectory=/opt/itms/backend
Environment="PATH=/opt/itms/backend/venv/bin"
ExecStart=/opt/itms/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

[Install]
WantedBy=multi-user.target
```

## 📊 Monitoring

- **Health Check**: `GET /health`
- **Logs**: Structured JSON logs
- **Metrics**: Process time headers
- **Database**: Connection pool monitoring

## 🔄 Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🛠️ Development

### Code Style
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

```bash
# Format code
black app/
isort app/

# Lint
flake8 app/
mypy app/
```

## 📝 Next Steps

1. ✅ Backend architecture (DONE)
2. 🔄 Database schema and models
3. 🔄 Authentication module
4. 🔄 User management
5. 🔄 Junction management
6. 🔄 Signal control
7. 🔄 WebSocket real-time updates
8. 🔄 Audit logging
9. 🔄 Testing suite

## 📞 Support

For issues or questions, contact the development team.

---

**ITMS Backend v1.0.0** - Production-ready traffic management system
