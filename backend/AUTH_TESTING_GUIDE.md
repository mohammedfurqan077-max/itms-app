# Authentication Module - Testing Guide

## 🎯 Overview

The authentication module is now complete and ready for testing. This guide will help you test all authentication endpoints.

---

## 🚀 Quick Setup

### 1. Start the Backend

#### Option A: Docker (Recommended)
```bash
cd backend
docker-compose up -d
```

#### Option B: Local
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run migrations
alembic upgrade head

# Seed test data
python scripts/seed_data.py

# Start server
uvicorn app.main:app --reload
```

### 2. Access API Documentation
Open: http://localhost:8000/api/docs

---

## 👥 Test Credentials

After running the seed script, you'll have:

**Admin User:**
- Email: `admin@itms.com`
- Password: `admin123`
- Role: `admin`

**Jawan User:**
- Email: `jawan@itms.com`
- Password: `jawan123`
- Role: `jawan`

---

## 📝 Testing Endpoints

### 1. Register New User

**Endpoint:** `POST /api/v1/auth/register`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@itms.com",
    "password": "testpass123",
    "role": "jawan"
  }'
```

**Expected Response:**
```json
{
  "user": {
    "id": 3,
    "name": "Test User",
    "email": "test@itms.com",
    "role": "jawan",
    "status": "active",
    "last_login": null,
    "created_at": "2024-01-15T10:30:00"
  },
  "message": "User registered successfully"
}
```

**Test Cases:**
- ✅ Valid registration
- ❌ Duplicate email (should fail)
- ❌ Invalid email format (should fail)
- ❌ Password too short (should fail)
- ❌ Try to register as admin (should fail)

---

### 2. Login

**Endpoint:** `POST /api/v1/auth/login`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jawan@itms.com",
    "password": "jawan123"
  }'
```

**Expected Response:**
```json
{
  "user": {
    "id": 2,
    "name": "Test Jawan",
    "email": "jawan@itms.com",
    "role": "jawan",
    "status": "active",
    "last_login": "2024-01-15T10:30:00",
    "created_at": "2024-01-01T00:00:00"
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

**Save the tokens for next requests!**

**Test Cases:**
- ✅ Valid credentials
- ❌ Wrong password (should fail)
- ❌ Non-existent email (should fail)
- ❌ Multiple failed attempts (should lock account after 5 attempts)

---

### 3. Get Current User

**Endpoint:** `GET /api/v1/auth/me`

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "id": 2,
  "name": "Test Jawan",
  "email": "jawan@itms.com",
  "role": "jawan",
  "status": "active",
  "last_login": "2024-01-15T10:30:00",
  "created_at": "2024-01-01T00:00:00"
}
```

**Test Cases:**
- ✅ Valid token
- ❌ No token (should fail with 401)
- ❌ Invalid token (should fail with 401)
- ❌ Expired token (should fail with 401)

---

### 4. Refresh Token

**Endpoint:** `POST /api/v1/auth/refresh`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Test Cases:**
- ✅ Valid refresh token
- ❌ Invalid refresh token (should fail)
- ❌ Expired refresh token (should fail)
- ❌ Using access token instead of refresh token (should fail)

---

### 5. Change Password

**Endpoint:** `POST /api/v1/auth/change-password`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/change-password" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "jawan123",
    "new_password": "newpass456"
  }'
```

**Expected Response:**
```json
{
  "message": "Password changed successfully. Please login again.",
  "success": true
}
```

**Note:** All sessions are invalidated after password change.

**Test Cases:**
- ✅ Valid current password
- ❌ Wrong current password (should fail)
- ❌ New password too short (should fail)

---

### 6. Logout

**Endpoint:** `POST /api/v1/auth/logout`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout?refresh_token=YOUR_REFRESH_TOKEN" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "message": "Logged out successfully"
}
```

**Test Cases:**
- ✅ Valid refresh token
- ✅ Already logged out token (should still succeed)

---

### 7. Verify Token

**Endpoint:** `POST /api/v1/auth/verify-token`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/verify-token" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "valid": true,
  "user": {
    "id": 2,
    "name": "Test Jawan",
    "email": "jawan@itms.com",
    "role": "jawan",
    "status": "active",
    "last_login": "2024-01-15T10:30:00",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

---

## 🧪 Testing with Swagger UI

1. Open http://localhost:8000/api/docs
2. Click on any endpoint to expand
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"
6. View the response

### Using Authentication in Swagger:
1. Login using `/api/v1/auth/login`
2. Copy the `access_token` from response
3. Click "Authorize" button at top
4. Enter: `Bearer YOUR_ACCESS_TOKEN`
5. Click "Authorize"
6. Now all requests will include the token

---

## 🔐 Security Features to Test

### 1. Account Lockout
Try logging in with wrong password 5 times:
```bash
for i in {1..5}; do
  curl -X POST "http://localhost:8000/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"jawan@itms.com","password":"wrongpass"}'
  echo "\nAttempt $i"
done
```

After 5 attempts, account should be locked for 15 minutes.

### 2. Token Expiration
- Access token expires in 30 minutes
- Refresh token expires in 7 days
- Try using expired token (should fail)

### 3. Session Tracking
- Each login creates a session record
- Sessions track IP address and user agent
- Logout invalidates the session

### 4. Password Security
- Passwords are hashed with bcrypt
- Minimum 8 characters required
- Password hash is never returned in responses

---

## 📊 Database Verification

### Check Users
```bash
docker-compose exec postgres psql -U itms_user -d itms_db -c "SELECT id, name, email, role, status FROM users;"
```

### Check Sessions
```bash
docker-compose exec postgres psql -U itms_user -d itms_db -c "SELECT id, user_id, is_active, created_at FROM sessions;"
```

### Check Permissions
```bash
docker-compose exec postgres psql -U itms_user -d itms_db -c "SELECT * FROM permissions;"
```

---

## 🐛 Common Issues

### Issue: "Database connection error"
**Solution:** Make sure PostgreSQL is running
```bash
docker-compose up -d postgres
```

### Issue: "Table doesn't exist"
**Solution:** Run migrations
```bash
alembic upgrade head
```

### Issue: "No test users"
**Solution:** Run seed script
```bash
python scripts/seed_data.py
```

### Issue: "Token expired"
**Solution:** Use refresh token to get new access token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"YOUR_REFRESH_TOKEN"}'
```

---

## ✅ Testing Checklist

### Registration
- [ ] Register new user successfully
- [ ] Duplicate email rejected
- [ ] Invalid email rejected
- [ ] Short password rejected
- [ ] Admin role registration rejected

### Login
- [ ] Login with valid credentials
- [ ] Wrong password rejected
- [ ] Non-existent email rejected
- [ ] Account locked after 5 failed attempts
- [ ] Tokens returned correctly

### Token Management
- [ ] Access token works for authenticated endpoints
- [ ] Refresh token generates new access token
- [ ] Invalid token rejected
- [ ] Expired token rejected

### User Info
- [ ] Get current user info works
- [ ] Requires valid token
- [ ] Returns correct user data

### Password Change
- [ ] Change password successfully
- [ ] Wrong current password rejected
- [ ] All sessions invalidated after change

### Logout
- [ ] Logout invalidates refresh token
- [ ] Access token still works until expiration

---

## 📈 Performance Testing

### Load Test Login Endpoint
```bash
# Install Apache Bench
# Ubuntu: apt-get install apache2-utils
# Mac: brew install ab

# Test 100 requests with 10 concurrent
ab -n 100 -c 10 -p login.json -T application/json http://localhost:8000/api/v1/auth/login
```

Create `login.json`:
```json
{"email":"jawan@itms.com","password":"jawan123"}
```

---

## 🎯 Next Steps

After testing authentication:
1. ✅ Authentication module working
2. 🔄 Implement user management endpoints
3. 🔄 Implement junction management
4. 🔄 Implement signal control
5. 🔄 Add WebSocket support

---

## 📞 Support

If you encounter issues:
1. Check logs: `docker-compose logs -f backend`
2. Check database: `make db-shell`
3. Review code in `app/api/v1/endpoints/auth.py`
4. Review service in `app/services/auth_service.py`

---

**Happy Testing! 🚀**
