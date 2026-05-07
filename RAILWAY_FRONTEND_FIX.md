# Railway Frontend Fix - Application Failed to Respond

## 🔴 Issue
Frontend shows: "Application failed to respond"

## 🔍 Root Causes
1. Missing environment variables during build
2. Next.js trying to make API calls during build time
3. Port binding issues

## ✅ Fixes Applied

### 1. Updated `frontend/next.config.js`
Added environment variable handling and disabled image optimization:

```javascript
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || '/api',
    NEXT_PUBLIC_SOCKET_URL: process.env.NEXT_PUBLIC_SOCKET_URL || '',
  },
  images: {
    unoptimized: true,
  },
};
```

### 2. Updated `frontend/railway.toml`
Simplified start command:

```toml
[deploy]
startCommand = "npm run start"
```

---

## 🚀 Deployment Steps

### Step 1: Push Code Changes

```bash
git add frontend/next.config.js frontend/railway.toml

git commit -m "Fix Railway frontend deployment - add env handling"

git push origin main
```

### Step 2: Set Environment Variables in Railway

**CRITICAL**: You MUST set these BEFORE the build runs!

Go to Railway Dashboard → **Frontend Service** → **Variables** tab:

```env
NEXT_PUBLIC_API_BASE_URL=/api
NEXT_PUBLIC_SOCKET_URL=https://itms-app-production.up.railway.app
API_SERVER_URL=https://itms-app-production.up.railway.app/api
NODE_ENV=production
PORT=3000
```

### Step 3: Trigger Redeploy

After setting variables:
1. Go to Railway Dashboard → Frontend Service
2. Click "Deployments" tab
3. Click "Redeploy" on the latest deployment

OR just push the code changes and Railway will auto-deploy.

---

## 🔧 Alternative Fix: Manual Railway Configuration

If the above doesn't work, try this in Railway Dashboard:

### Build Settings:
- **Build Command**: `npm run build`
- **Start Command**: `npm run start`
- **Root Directory**: `frontend`

### Environment Variables:
```env
NEXT_PUBLIC_API_BASE_URL=/api
NEXT_PUBLIC_SOCKET_URL=https://itms-app-production.up.railway.app
NODE_ENV=production
```

---

## 🐛 Debugging Steps

### 1. Check Railway Logs

Go to Railway Dashboard → Frontend Service → Deployments → View Logs

Look for:
- ✅ `npm run build` completed successfully
- ✅ `npm run start` started
- ✅ `ready - started server on 0.0.0.0:3000`
- ❌ Any error messages

### 2. Common Error Messages

#### "ECONNREFUSED" or "fetch failed"
**Cause**: Frontend trying to call backend during build
**Fix**: Environment variables not set correctly

#### "Error: listen EADDRINUSE"
**Cause**: Port already in use
**Fix**: Railway should handle this automatically

#### "Module not found"
**Cause**: Dependencies not installed
**Fix**: Delete `node_modules` in Railway (redeploy)

### 3. Check Build Output

Successful build should show:
```
✓ Compiled successfully
✓ Linting and checking validity of types
✓ Collecting page data
✓ Generating static pages
✓ Finalizing page optimization
```

### 4. Check Start Output

Successful start should show:
```
> next start
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

---

## 🎯 Expected Timeline

1. **Push code**: ~5 seconds
2. **Railway detects**: ~10 seconds
3. **Install dependencies**: ~30-60 seconds
4. **Build**: ~2-3 minutes
5. **Start**: ~10 seconds
6. **Health check**: ~5 seconds

**Total**: ~3-5 minutes

---

## ✅ Success Indicators

When working correctly:

1. **Build logs show**:
   ```
   ✓ Compiled successfully
   ✓ Generating static pages
   ```

2. **Start logs show**:
   ```
   ready - started server on 0.0.0.0:3000
   ```

3. **Frontend URL loads**: https://lively-art-production-5c53.up.railway.app

4. **Login page appears** with no errors

5. **Browser console** shows no errors (F12 → Console)

---

## 🔄 If Still Not Working

### Option 1: Delete and Recreate Service

1. Delete the frontend service in Railway
2. Create new service from GitHub
3. Set Root Directory: `frontend`
4. Add environment variables BEFORE first deploy
5. Deploy

### Option 2: Use Different Build Configuration

Update `frontend/railway.toml`:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "npm run start"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

Remove `buildCommand` to let Nixpacks auto-detect.

### Option 3: Check for Build-Time API Calls

Some pages might be trying to fetch data during build. Check:
- `frontend/src/pages/*.js` - Look for `getStaticProps` or `getServerSideProps`
- Make sure they handle missing API gracefully

---

## 📊 Environment Variables Explained

| Variable | Purpose | Example |
|----------|---------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | Client-side API path | `/api` |
| `NEXT_PUBLIC_SOCKET_URL` | WebSocket connection | `https://itms-app-production.up.railway.app` |
| `API_SERVER_URL` | Server-side API URL | `https://itms-app-production.up.railway.app/api` |
| `NODE_ENV` | Environment mode | `production` |
| `PORT` | Server port (optional) | `3000` |

**Note**: Variables starting with `NEXT_PUBLIC_` are exposed to the browser.

---

## 🚀 Quick Commands

```bash
# Push frontend fixes
git add frontend/next.config.js frontend/railway.toml RAILWAY_FRONTEND_FIX.md

git commit -m "Fix Railway frontend deployment - add env handling"

git push origin main
```

Then set environment variables in Railway and wait 3-5 minutes for deployment!

---

## 📞 Need Help?

If still not working, check:
1. Railway logs for specific error messages
2. Browser console (F12) for client-side errors
3. Network tab (F12) to see failed requests

Share the error message and I'll help debug further!
