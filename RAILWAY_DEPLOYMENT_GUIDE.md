# Railway Deployment Guide - ITMS Backend

## Overview

This guide will help you deploy the ITMS backend to Railway with PostgreSQL database.

---

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Account**: For connecting your repository
3. **Git**: Installed on your local machine

---

## Step 1: Prepare Your Repository

### 1.1 Initialize Git (if not already done)
```bash
cd D:\ITMS_APP
git init
git add .
git commit -m "Initial commit - ITMS Backend"
```

### 1.2 Create GitHub Repository
1. Go to [github.com](https://github.com)
2. Click "New Repository"
3. Name it: `itms-backend`
4. Don't initialize with README (we already have code)
5. Click "Create Repository"

### 1.3 Push to GitHub
```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/itms-backend.git

# Push code
git branch -M main
git push -u origin main
```

---

## Step 2: Create Railway Project

### 2.1 Login to Railway
1. Go to [railway.app](https://railway.app)
2. Click "Login" and sign in with GitHub
3. Authorize Railway to access your repositories

### 2.2 Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `itms-backend` repository
4. Railway will detect it's a Python project

### 2.3 Add PostgreSQL Database
1. In your project, click "New"
2. Select "Database"
3. Choose "PostgreSQL"
4. Railway will provision a PostgreSQL database

---

## Step 3: Configure Environment Variables

### 3.1 Get Database URL
1. Click on the PostgreSQL service
2. Go to "Variables" tab
3. Copy the `DATABASE_URL` value
4. It will look like: `postgresql://user:pass@host:port/db`

### 3.2 Convert Database URL for AsyncPG
Railway provides a sync URL, but we need async:
```
# Railway gives:
postgresql://user:pass@host:port/db

# Change to:
postgresql+asyncpg://user:pass@host:port/db
```

### 3.3 Add Environment Variables
Click on your backend service → "Variables" tab → Add these:

```bash
# Application
APP_NAME=ITMS Backend
APP_VERSION=1.0.0
DEBUG=False
LOG_LEVEL=INFO

# Database (IMPORTANT: Use postgresql+asyncpg://)
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db

# Security (CHANGE THESE!)
SECRET_KEY=your-super-secret-key-min-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (Add your frontend URL when ready)
ALLOWED_ORIGINS=*
ALLOWED_HOSTS=*

# Control System (Optional)
CONTROL_SYSTEM_URL=http://localhost:5000
CONTROL_SYSTEM_API_KEY=production-api-key
CONTROL_SYSTEM_TIMEOUT=10

# Admin User
ADMIN_EMAIL=admin@itms.com
ADMIN_PASSWORD=YourSecurePassword123!
```

**IMPORTANT**: 
- Replace `DATABASE_URL` with your actual Railway PostgreSQL URL
- Change `SECRET_KEY` to a random 32+ character string
- Change `ADMIN_PASSWORD` to a secure password

### 3.4 Generate Secret Key
```bash
# On your local machine
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Step 4: Configure Deployment

### 4.1 Verify Configuration Files
Railway should detect these files in your `backend/` directory:
- ✅ `railway.toml` - Railway configuration
- ✅ `Procfile` - Start command
- ✅ `nixpacks.toml` - Build configuration
- ✅ `requirements.txt` - Python dependencies

### 4.2 Set Root Directory
1. Go to your backend service
2. Click "Settings"
3. Find "Root Directory"
4. Set it to: `backend`
5. Click "Save"

### 4.3 Set Start Command (if needed)
If Railway doesn't pick up the Procfile:
1. Go to "Settings"
2. Find "Start Command"
3. Set it to:
```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## Step 5: Deploy

### 5.1 Trigger Deployment
1. Railway will automatically deploy when you push to GitHub
2. Or click "Deploy" in the Railway dashboard

### 5.2 Monitor Deployment
1. Click on your service
2. Go to "Deployments" tab
3. Click on the latest deployment
4. Watch the build logs

**Expected logs**:
```
[nixpacks] Installing Python dependencies...
[nixpacks] Running: pip install -r requirements.txt
[nixpacks] Build complete
[railway] Starting deployment...
[app] Running: alembic upgrade head
[app] INFO  [alembic.runtime.migration] Running upgrade -> 001
[app] INFO  [alembic.runtime.migration] Running upgrade 001 -> 002
[app] INFO  [alembic.runtime.migration] Running upgrade 002 -> 003
[app] INFO  [alembic.runtime.migration] Running upgrade 003 -> 004
[app] INFO: Starting ITMS Backend...
[app] INFO: CommandExecutor started
[app] INFO: Application startup complete
[app] INFO: Uvicorn running on http://0.0.0.0:PORT
```

### 5.3 Check Deployment Status
- ✅ Green checkmark = Deployed successfully
- ❌ Red X = Deployment failed (check logs)

---

## Step 6: Get Your API URL

### 6.1 Generate Public URL
1. Click on your backend service
2. Go to "Settings"
3. Find "Networking" section
4. Click "Generate Domain"
5. Railway will give you a URL like: `https://your-app.railway.app`

### 6.2 Test Your API
```bash
# Health check
curl https://your-app.railway.app/health

# Expected response:
{
  "status": "healthy",
  "app": "ITMS Backend",
  "version": "1.0.0"
}
```

---

## Step 7: Create Admin User

### 7.1 Option A: Via Environment Variables
The admin user should be created automatically on first startup if you set:
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`

### 7.2 Option B: Via Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run command
railway run python -c "
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash
import asyncio

async def create_admin():
    async with AsyncSessionLocal() as db:
        admin = User(
            email='admin@itms.com',
            hashed_password=get_password_hash('YourPassword123!'),
            full_name='Admin User',
            is_active=True,
            is_superuser=True
        )
        db.add(admin)
        await db.commit()
        print('Admin created!')

asyncio.run(create_admin())
"
```

---

## Step 8: Test Your Deployment

### 8.1 Test Authentication
```bash
export API_URL="https://your-app.railway.app"

# Login
curl -X POST $API_URL/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@itms.com&password=YourPassword123!"

# Save the token
export TOKEN="your_token_here"
```

### 8.2 Test API Endpoints
```bash
# Get current user
curl -X GET $API_URL/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Get system stats
curl -X GET $API_URL/api/v1/system/stats \
  -H "Authorization: Bearer $TOKEN"

# Create a junction
curl -X POST $API_URL/api/v1/junctions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Main Junction",
    "location": "City Center",
    "ip_address": "192.168.1.100",
    "status": "active"
  }'
```

### 8.3 Test Command Creation
```bash
# Create command
curl -X POST $API_URL/api/v1/commands/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "get_status",
    "payload": {},
    "execute_immediately": false
  }'
```

---

## Step 9: Monitor Your Application

### 9.1 View Logs
1. Go to your service in Railway
2. Click "Logs" tab
3. Watch real-time logs

### 9.2 Check Metrics
1. Click "Metrics" tab
2. View CPU, Memory, Network usage

### 9.3 Set Up Alerts (Optional)
1. Go to project settings
2. Configure notifications for:
   - Deployment failures
   - High resource usage
   - Downtime

---

## Step 10: Connect Frontend

### 10.1 Update Frontend API URL
In your frontend `.env`:
```bash
VITE_API_URL=https://your-app.railway.app/api/v1
# or
REACT_APP_API_URL=https://your-app.railway.app/api/v1
# or
NEXT_PUBLIC_API_URL=https://your-app.railway.app/api/v1
```

### 10.2 Update CORS Settings
Update your backend environment variables:
```bash
ALLOWED_ORIGINS=https://your-frontend.railway.app,https://your-custom-domain.com
```

Then redeploy:
```bash
git add .
git commit -m "Update CORS settings"
git push origin main
```

---

## Troubleshooting

### Issue: Build Fails

**Check**:
1. Logs in Railway dashboard
2. Verify `requirements.txt` is correct
3. Ensure `backend/` is set as root directory

**Solution**:
```bash
# Test locally first
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app
```

### Issue: Database Connection Error

**Check**:
1. `DATABASE_URL` is set correctly
2. URL uses `postgresql+asyncpg://` (not just `postgresql://`)
3. Database service is running

**Solution**:
```bash
# In Railway, go to PostgreSQL service
# Copy the connection string
# Update DATABASE_URL with +asyncpg
```

### Issue: Migration Fails

**Check**:
1. Alembic is running before app starts
2. Database is accessible
3. Migration files exist

**Solution**:
```bash
# Check start command includes:
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Issue: App Crashes on Startup

**Check**:
1. All environment variables are set
2. SECRET_KEY is at least 32 characters
3. No syntax errors in code

**Solution**:
```bash
# View logs in Railway
# Look for error messages
# Fix and redeploy
```

### Issue: 502 Bad Gateway

**Check**:
1. App is listening on `0.0.0.0` and `$PORT`
2. Health endpoint responds
3. No startup errors

**Solution**:
```bash
# Verify start command:
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## Production Checklist

Before going live, ensure:

### Security
- [ ] `DEBUG=False`
- [ ] Strong `SECRET_KEY` (32+ characters)
- [ ] Secure `ADMIN_PASSWORD`
- [ ] CORS configured with specific origins
- [ ] HTTPS enabled (Railway does this automatically)

### Database
- [ ] Migrations run successfully
- [ ] Database backups enabled (Railway Pro)
- [ ] Connection pooling configured

### Monitoring
- [ ] Logs are accessible
- [ ] Metrics are being collected
- [ ] Alerts configured

### Performance
- [ ] Rate limiting enabled
- [ ] Proper indexes on database
- [ ] Command executor running

### Documentation
- [ ] API documentation accessible
- [ ] Environment variables documented
- [ ] Deployment process documented

---

## Updating Your Deployment

### Method 1: Git Push (Automatic)
```bash
# Make changes
git add .
git commit -m "Your changes"
git push origin main

# Railway will automatically deploy
```

### Method 2: Manual Deploy
1. Go to Railway dashboard
2. Click "Deploy"
3. Select commit to deploy

### Method 3: Rollback
1. Go to "Deployments"
2. Find previous working deployment
3. Click "Redeploy"

---

## Cost Estimation

### Railway Pricing (as of 2024)

**Free Tier**:
- $5 credit per month
- Suitable for development/testing
- May sleep after inactivity

**Hobby Plan** ($5/month):
- $5 credit included
- No sleeping
- Better for production

**Pro Plan** ($20/month):
- $20 credit included
- Priority support
- Database backups
- Better for production

**Estimated Monthly Cost**:
- Backend service: ~$3-5
- PostgreSQL database: ~$2-3
- **Total**: ~$5-8/month

---

## Custom Domain (Optional)

### 1. Add Custom Domain
1. Go to your service settings
2. Find "Networking"
3. Click "Add Custom Domain"
4. Enter your domain: `api.yourdomain.com`

### 2. Configure DNS
Add CNAME record in your DNS provider:
```
Type: CNAME
Name: api
Value: your-app.railway.app
```

### 3. Wait for SSL
Railway will automatically provision SSL certificate (5-10 minutes)

---

## Support

### Railway Documentation
- [Railway Docs](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)

### ITMS Support
- Check logs in Railway dashboard
- Review `TESTING_GUIDE.md` for validation
- Run `test_full_system_validation.py` locally

---

## Summary

✅ **Deployment Steps**:
1. Push code to GitHub
2. Create Railway project
3. Add PostgreSQL database
4. Configure environment variables
5. Deploy and test

✅ **Your URLs**:
- Backend: `https://your-app.railway.app`
- API Docs: `https://your-app.railway.app/api/docs`
- Health: `https://your-app.railway.app/health`

✅ **Next Steps**:
1. Test all endpoints
2. Create junctions
3. Test command execution
4. Connect frontend
5. Go live!

---

**Deployment Time**: ~15-20 minutes  
**Difficulty**: Easy  
**Cost**: ~$5-8/month  
**Status**: Production-ready ✅
