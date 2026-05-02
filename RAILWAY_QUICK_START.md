# Railway Deployment - Quick Start

## 🚀 Deploy in 5 Minutes

### Option 1: Railway Dashboard (Easiest)

1. **Go to Railway**
   ```
   https://railway.app/dashboard
   ```

2. **New Project → Deploy from GitHub**
   - Select your repository
   - Set root directory: `backend`

3. **Add PostgreSQL**
   - Click "New" → "Database" → "PostgreSQL"

4. **Set Environment Variables**
   ```
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   SECRET_KEY=<generate-secure-key>
   DEBUG=False
   ALLOWED_ORIGINS=https://your-frontend.com
   ```

5. **Deploy!**
   - Railway deploys automatically
   - Get your URL: `https://your-app.up.railway.app`

---

### Option 2: Railway CLI (Fastest)

```bash
# Install CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
cd backend
./deploy_railway.sh  # Linux/Mac
# or
.\deploy_railway.ps1  # Windows
```

---

## 📝 Required Environment Variables

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in Railway Dashboard
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=<your-generated-key>
DEBUG=False
ALLOWED_ORIGINS=https://your-frontend.com,http://localhost:3000
APP_NAME=ITMS
LOG_LEVEL=INFO
```

---

## ✅ Verify Deployment

```bash
# Test health endpoint
curl https://your-app.up.railway.app/health

# Expected response
{"status":"healthy","app":"ITMS","version":"1.0.0"}
```

---

## 🔧 Post-Deployment

### 1. Run Migrations
```bash
railway run alembic upgrade head
```

### 2. Create Admin User
```bash
railway run python
```

```python
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash
import asyncio

async def create_admin():
    async with AsyncSessionLocal() as db:
        admin = User(
            email="admin@itms.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True
        )
        db.add(admin)
        await db.commit()
        print("Admin created!")

asyncio.run(create_admin())
```

### 3. Test Login
```bash
curl -X POST https://your-app.up.railway.app/api/v1/auth/login \
  -d "username=admin@itms.com&password=admin123"
```

---

## 📊 Monitor

```bash
# View logs
railway logs

# Check status
railway status

# Open dashboard
railway open
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | Check `requirements.txt` exists |
| Database error | Verify `DATABASE_URL` is set |
| Port error | Ensure using `$PORT` variable |
| CORS error | Add frontend URL to `ALLOWED_ORIGINS` |

---

## 💰 Cost

- **Hobby**: $5/month (500 hours)
- **Pro**: $20/month (unlimited)

**Estimated**: ~$10-20/month for ITMS

---

## 📚 Full Guide

See `RAILWAY_DEPLOYMENT_GUIDE.md` for complete instructions.

---

## ✅ Checklist

- [ ] Railway account created
- [ ] Code pushed to GitHub
- [ ] PostgreSQL database added
- [ ] Environment variables set
- [ ] Deployment successful
- [ ] Migrations run
- [ ] Admin user created
- [ ] Endpoints tested
- [ ] Frontend URL in CORS

---

**Your Backend URL**: `https://your-app.up.railway.app`

**API Docs**: `https://your-app.up.railway.app/api/docs` (if DEBUG=True)

**Ready to deploy? Run**: `./deploy_railway.sh` 🚀
