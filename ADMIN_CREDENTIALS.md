# Admin Account Credentials

## 🔐 Default Admin Account

### Credentials:
```
Email:    admin@itms.com
Password: admin123
```

---

## 📝 How Admin Account is Created

The admin account is created automatically when you run the seed data script or when the application starts for the first time.

### Location in Code:
- **File**: `backend/scripts/seed_data.py`
- **Email**: `admin@itms.com`
- **Password**: `admin123` (hashed with bcrypt)
- **Role**: ADMIN
- **Status**: ACTIVE

---

## 🚀 For Railway Deployment

When deploying to Railway, you should set these environment variables:

```bash
ADMIN_EMAIL=admin@itms.com
ADMIN_PASSWORD=admin123
```

**IMPORTANT**: Change the password to something secure for production!

### Recommended Production Password:
```bash
ADMIN_PASSWORD=YourSecurePassword123!
```

---

## 🧪 Testing Login

### Using cURL:
```bash
# Local
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@itms.com&password=admin123"

# Railway (replace with your URL)
curl -X POST https://your-app.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@itms.com&password=admin123"
```

### Using PowerShell:
```powershell
# Local
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method Post `
  -ContentType "application/x-www-form-urlencoded" `
  -Body "username=admin@itms.com&password=admin123"

$response.access_token

# Railway
$response = Invoke-RestMethod -Uri "https://your-app.up.railway.app/api/v1/auth/login" `
  -Method Post `
  -ContentType "application/x-www-form-urlencoded" `
  -Body "username=admin@itms.com&password=admin123"

$response.access_token
```

### Expected Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 🔄 Creating Admin Account Manually

If the admin account doesn't exist, you can create it:

### Option 1: Run Seed Script
```bash
cd backend
python scripts/seed_data.py
```

### Option 2: Use Reset Password Script
```bash
cd backend
python reset_admin_password.py
```

### Option 3: Via API (if you have another admin account)
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@itms.com",
    "password": "admin123",
    "full_name": "System Administrator"
  }'
```

---

## 🔒 Security Recommendations

### For Development:
- ✅ Use: `admin@itms.com` / `admin123`
- ✅ This is fine for local testing

### For Production (Railway):
- ❌ Don't use: `admin123`
- ✅ Use strong password: `YourSecurePassword123!`
- ✅ Minimum 8 characters
- ✅ Mix of uppercase, lowercase, numbers, symbols

### Generate Strong Password:
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(16))"

# PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 16 | % {[char]$_})
```

---

## 📊 Admin Account Details

### Database Table: `users`
```sql
SELECT * FROM users WHERE email = 'admin@itms.com';
```

### Fields:
- **id**: Auto-generated
- **email**: admin@itms.com
- **hashed_password**: bcrypt hash of password
- **full_name**: System Administrator
- **is_active**: true
- **is_superuser**: true
- **created_at**: Timestamp

---

## 🔑 Changing Admin Password

### Method 1: Via API (if logged in)
```bash
# Get token first
TOKEN="your-access-token"

# Change password
curl -X PUT http://localhost:8000/api/v1/auth/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "admin123",
    "new_password": "NewSecurePassword123!"
  }'
```

### Method 2: Via Database
```sql
-- Connect to database
psql -U postgres -d itms_db

-- Update password (use bcrypt hash)
UPDATE users 
SET hashed_password = '$2b$12$...' 
WHERE email = 'admin@itms.com';
```

### Method 3: Via Reset Script
```bash
cd backend
python reset_admin_password.py
```

---

## 🧪 Verify Admin Account Exists

### Check via API:
```bash
# Try to login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=admin@itms.com&password=admin123"

# If successful, account exists
# If 401 error, account doesn't exist or wrong password
```

### Check via Database:
```sql
SELECT email, full_name, is_active, is_superuser, created_at 
FROM users 
WHERE email = 'admin@itms.com';
```

---

## 📝 Summary

### Default Credentials:
```
Email:    admin@itms.com
Password: admin123
```

### For Railway:
Set these environment variables:
```
ADMIN_EMAIL=admin@itms.com
ADMIN_PASSWORD=YourSecurePassword123!
```

### Test Login:
```bash
curl -X POST https://your-app.up.railway.app/api/v1/auth/login \
  -d "username=admin@itms.com&password=admin123"
```

---

## ⚠️ Important Notes

1. **Change Password in Production**: Never use `admin123` in production
2. **Secure Storage**: Store credentials securely (password manager)
3. **Environment Variables**: Use Railway environment variables for credentials
4. **First Login**: Change password immediately after first login
5. **Backup**: Keep backup of admin credentials in secure location

---

**Default Admin Account**: `admin@itms.com` / `admin123`

**For Production**: Change password to something secure!
