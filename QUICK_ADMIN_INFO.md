# Quick Admin Info

## 🔐 Admin Credentials

```
Email:    admin@itms.com
Password: admin123
```

---

## 🚀 Login Test

### Local:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=admin@itms.com&password=admin123"
```

### Railway:
```bash
curl -X POST https://your-app.up.railway.app/api/v1/auth/login \
  -d "username=admin@itms.com&password=admin123"
```

---

## 📝 For Railway Deployment

Add these environment variables:

```
ADMIN_EMAIL=admin@itms.com
ADMIN_PASSWORD=admin123
```

**⚠️ Change password for production!**

---

## ✅ Success Response

```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

---

**Full details**: See `ADMIN_CREDENTIALS.md`
