# ITMS API - Quick Reference Card

## 🔗 Base URL
```
http://localhost:8000/api/v1
```

---

## 🔐 Authentication Endpoints

### Register
```http
POST /auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@itms.com",
  "password": "password123",
  "role": "jawan"
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "jawan@itms.com",
  "password": "jawan123"
}

Response:
{
  "user": {...},
  "tokens": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### Get Current User
```http
GET /auth/me
Authorization: Bearer {access_token}
```

### Refresh Token
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}
```

### Change Password
```http
POST /auth/change-password
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "current_password": "old123",
  "new_password": "new456"
}
```

### Logout
```http
POST /auth/logout?refresh_token={refresh_token}
Authorization: Bearer {access_token}
```

### Verify Token
```http
POST /auth/verify-token
Authorization: Bearer {access_token}
```

---

## 🎛️ System State Endpoints

### Get System State
```http
GET /system/state
Authorization: Bearer {access_token}
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
  "updated_by_name": "Admin User",
  "junction_name": null
}
```

### Update Mode (Path)
```http
POST /system/mode/{mode}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "new_mode": "auto_circle",
  "junction_id": null,
  "mode_metadata": null
}
```

### Update Mode (Body)
```http
POST /system/mode
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "new_mode": "vip",
  "junction_id": 5,
  "mode_metadata": "{\"lane\": 2}"
}
```

### Reset to Default
```http
POST /system/reset
Authorization: Bearer {access_token}
```

### Get Current Mode
```http
GET /system/mode
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "current_mode": "manual"
}
```

---

## 🔑 Test Credentials

**Admin:**
- Email: `admin@itms.com`
- Password: `admin123`

**Jawan:**
- Email: `jawan@itms.com`
- Password: `jawan123`

---

## 🎫 Using Tokens

### In Headers
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Expiration
- **Access Token**: 30 minutes
- **Refresh Token**: 7 days

---

## 🎯 System Modes

| Mode | Description |
|------|-------------|
| `manual` | Manual control |
| `auto_circle` | Automatic circular rotation |
| `auto_jump` | Intelligent auto mode |
| `blinker` | Yellow blinker mode |
| `vip` | VIP/emergency vehicle mode |

---

## 📊 Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 423 | Account Locked |
| 429 | Rate Limit Exceeded |
| 500 | Server Error |

---

## 🚦 Rate Limits

| Endpoint | Limit |
|----------|-------|
| /auth/register | 5/minute |
| /auth/login | 10/minute |
| /auth/refresh | 20/minute |

---

## 🔒 Permissions

- `set_time` - Set manual signal timings
- `auto_jump` - Use auto jump mode
- `auto_circle` - Use auto circle mode
- `blinker` - Use yellow blinker mode
- `vip_mode` - Activate VIP mode

---

## 🛠️ Quick Commands

### Start Server
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f backend
```

### Run Migrations
```bash
alembic upgrade head
```

### Seed Data
```bash
python scripts/seed_data.py
```

### Database Shell
```bash
make db-shell
```

---

## 📚 Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/health

---

## 🧪 Testing with curl

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@itms.com","password":"admin123"}'
```

### Get System State
```bash
TOKEN="your_access_token_here"
curl -X GET "http://localhost:8000/api/v1/system/state" \
  -H "Authorization: Bearer $TOKEN"
```

### Update Mode
```bash
curl -X POST "http://localhost:8000/api/v1/system/mode/auto_circle" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_mode":"auto_circle"}'
```

---

## 🐛 Troubleshooting

### Database Connection Error
```bash
docker-compose up -d postgres
```

### Table Doesn't Exist
```bash
alembic upgrade head
```

### No Test Users
```bash
python scripts/seed_data.py
```

---

**Quick Reference v1.1.0** - Updated with System State endpoints

