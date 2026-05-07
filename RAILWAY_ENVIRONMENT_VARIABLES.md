# Railway Environment Variables Configuration

## 🎯 Your Railway URLs

- **Backend**: https://itms-app-production.up.railway.app
- **Frontend**: https://lively-art-production-5c53.up.railway.app

---

## 🔧 Backend Environment Variables

Go to Railway Dashboard → **Backend Service** → **Variables** tab

### Required Variables:

```env
DATABASE_URL=postgresql://neondb_owner:npg_Van5Q4GATHJc@ep-orange-block-amqofpv1-pooler.c-5.us-east-1.aws.neon.tech/ITMS

SECRET_KEY=your-secret-key-here-generate-a-random-string

ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,https://lively-art-production-5c53.up.railway.app

DEBUG=false

LOG_LEVEL=INFO
```

**Note**: The `ALLOWED_ORIGINS` has been updated in the code to include your frontend URL.

---

## 🌐 Frontend Environment Variables

Go to Railway Dashboard → **Frontend Service** → **Variables** tab

### Required Variables:

```env
API_SERVER_URL=https://itms-app-production.up.railway.app/api

NEXT_PUBLIC_SOCKET_URL=https://itms-app-production.up.railway.app

NEXT_PUBLIC_API_BASE_URL=/api

NODE_ENV=production
```

---

## 📝 Git Commands to Deploy Backend Changes

Run these commands to push the CORS update:

```bash
git add backend/app/core/config.py backend/app/main.py

git commit -m "Update CORS to allow Railway frontend domain"

git push origin main
```

---

## ✅ Verification Steps

### 1. Check Backend API
Open these URLs in your browser:

- Health Check: https://itms-app-production.up.railway.app/health
- API Docs: https://itms-app-production.up.railway.app/docs
- API V1: https://itms-app-production.up.railway.app/api/v1/health

### 2. Check Frontend
- Open: https://lively-art-production-5c53.up.railway.app
- Should load without 502 errors
- Login page should appear

### 3. Test Login
- Email: `admin@itms.com`
- Password: `admin123`

---

## 🔄 Deployment Timeline

1. **Push backend changes** (CORS update)
   - Railway detects push: ~10 seconds
   - Backend rebuilds: ~2-3 minutes
   - Backend redeploys: ~30 seconds

2. **Add frontend environment variables**
   - Railway detects change: ~10 seconds
   - Frontend rebuilds: ~2-3 minutes
   - Frontend redeploys: ~30 seconds

**Total time**: ~5-7 minutes

---

## 🐛 Troubleshooting

### Still Getting 502 Error?

1. **Check Backend Logs**:
   - Railway Dashboard → Backend Service → Deployments → View Logs
   - Look for startup errors

2. **Check Frontend Logs**:
   - Railway Dashboard → Frontend Service → Deployments → View Logs
   - Look for connection errors

3. **Verify Environment Variables**:
   - Make sure all variables are set correctly
   - No extra spaces or quotes

4. **Check CORS**:
   - Open browser console (F12)
   - Look for CORS errors
   - Should see: "Access-Control-Allow-Origin: https://lively-art-production-5c53.up.railway.app"

### Backend Not Starting?

- Check DATABASE_URL is correct
- Check SECRET_KEY is set
- Check logs for migration errors

### Frontend Not Connecting?

- Verify API_SERVER_URL has `/api` at the end
- Verify NEXT_PUBLIC_SOCKET_URL does NOT have `/api`
- Check browser console for fetch errors

---

## 🎉 Success Indicators

When everything works:

✅ Backend health check returns: `{"status":"healthy","app":"ITMS","version":"1.0.0"}`

✅ Frontend loads without errors

✅ Login page appears

✅ Can login with admin credentials

✅ Dashboard loads with map view

✅ No CORS errors in browser console

---

## 📊 What Changed?

### Backend (`backend/app/core/config.py`):
```python
# Before:
ALLOWED_ORIGINS = "http://localhost:3000,http://localhost:8080"

# After:
ALLOWED_ORIGINS = "http://localhost:3000,http://localhost:8080,https://lively-art-production-5c53.up.railway.app"
```

### Backend (`backend/app/main.py`):
```python
# Before:
docs_url="/api/docs" if settings.DEBUG else None

# After:
docs_url="/docs"  # Always available
```

This allows you to access API documentation at: https://itms-app-production.up.railway.app/docs

---

## 🚀 Ready to Deploy!

**Run these commands now:**

```bash
# 1. Add backend changes
git add backend/app/core/config.py backend/app/main.py

# 2. Commit
git commit -m "Update CORS to allow Railway frontend domain"

# 3. Push
git push origin main
```

**Then add the frontend environment variables in Railway dashboard!**

---

**Your System Will Be Live in ~5-7 Minutes!** 🎉
