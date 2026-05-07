# Frontend Railway Deployment Guide

## ✅ Issue Fixed

**Problem**: Railway was running `npm ci` twice, causing cache conflict error:
```
EBUSY: resource busy or locked, rmdir '/app/node_modules/.cache'
```

**Root Cause**: Railway's default build command was `npm ci && npm run build`, but nixpacks already runs `npm ci` in the install phase.

**Solution**: Updated `frontend/nixpacks.toml` to only run `npm ci` once in the install phase.

---

## 🚀 Deployment Steps

### Step 1: Push Changes to GitHub

```bash
cd frontend
git add .
git commit -m "Fix Railway deployment configuration"
git push origin main
```

### Step 2: Configure Railway Project

1. **Go to Railway Dashboard**: https://railway.app/dashboard
2. **Create New Project** (or use existing)
3. **Add Service** → **GitHub Repo** → Select `itms_api`
4. **Configure Service Settings**:

#### Root Directory
```
frontend
```

#### Environment Variables
Add these in Railway dashboard:

```env
# Backend API URL (replace with your Railway backend URL)
API_SERVER_URL=https://your-backend.railway.app/api

# Socket URL (replace with your Railway backend URL)
NEXT_PUBLIC_SOCKET_URL=https://your-backend.railway.app

# Public API URL (for client-side requests)
NEXT_PUBLIC_API_BASE_URL=/api

# Node Environment
NODE_ENV=production
```

**Important**: Replace `your-backend.railway.app` with your actual Railway backend URL.

### Step 3: Deploy

1. Railway will automatically detect the configuration from `nixpacks.toml`
2. Build should complete successfully now
3. Frontend will be available at: `https://your-frontend.railway.app`

---

## 📋 Build Configuration

### nixpacks.toml
```toml
[phases.setup]
nixPkgs = ["nodejs_20"]

[phases.install]
cmds = ["npm ci --prefer-offline --no-audit"]

[phases.build]
cmds = ["npm run build"]

[start]
cmd = "npm run start -- -p ${PORT:-3000}"
```

### .dockerignore
```
node_modules
.next
.env.local
.env*.local
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.DS_Store
*.pem
.vscode
.idea
```

---

## 🔧 Post-Deployment Configuration

### Update Frontend Environment Variables

After backend is deployed, update `frontend/.env.local` for local development:

```env
NEXT_PUBLIC_API_BASE_URL=/api
API_SERVER_URL=https://your-backend.railway.app/api
NEXT_PUBLIC_SOCKET_URL=https://your-backend.railway.app
```

### Update Backend CORS Settings

Make sure your backend allows requests from the frontend domain:

In `backend/app/main.py`, update CORS origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend.railway.app"  # Add this
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ✅ Verification Checklist

After deployment:

- [ ] Frontend loads without errors
- [ ] Can access login page
- [ ] Can login with admin credentials (admin@itms.com / admin123)
- [ ] Dashboard loads correctly
- [ ] Map view displays
- [ ] Junction controls work
- [ ] Real-time updates work (WebSocket connection)
- [ ] Mobile responsive design works

---

## 🐛 Troubleshooting

### Build Still Fails with EBUSY Error

1. Delete the Railway service
2. Create a new service
3. Make sure Root Directory is set to `frontend`
4. Redeploy

### API Requests Fail

1. Check environment variables in Railway dashboard
2. Verify backend URL is correct
3. Check backend CORS settings
4. Check browser console for errors

### WebSocket Connection Fails

1. Verify `NEXT_PUBLIC_SOCKET_URL` is set correctly
2. Check backend WebSocket endpoint is accessible
3. Check browser console for connection errors

### Build Succeeds but App Doesn't Start

1. Check Railway logs for startup errors
2. Verify Node.js version (should be 20+)
3. Check `package.json` scripts are correct

---

## 📊 Expected Build Output

```
╔═══════════════ Nixpacks v1.41.0 ═══════════════╗
║ setup      │ nodejs_20                         ║
║────────────────────────────────────────────────║
║ install    │ npm ci --prefer-offline --no-audit║
║────────────────────────────────────────────────║
║ build      │ npm run build                     ║
║────────────────────────────────────────────────║
║ start      │ npm run start -- -p ${PORT:-3000} ║
╚════════════════════════════════════════════════╝
```

Build should complete in 2-5 minutes.

---

## 🎉 Success!

Once deployed, your ITMS frontend will be live at:
- **Frontend**: https://your-frontend.railway.app
- **Backend**: https://your-backend.railway.app

Users can access the system from any device with a web browser!

---

## 📱 Mobile Access

The web app is mobile-responsive and can be added to home screen:

### Android
1. Open the app in Chrome
2. Tap the menu (⋮)
3. Select "Add to Home screen"
4. App will open like a native app

### iOS
1. Open the app in Safari
2. Tap the Share button
3. Select "Add to Home Screen"
4. App will open like a native app

---

## 🔗 Quick Links

- **GitHub Repo**: https://github.com/Furqan-k77/itms_api
- **Railway Dashboard**: https://railway.app/dashboard
- **Backend API Docs**: https://your-backend.railway.app/docs
- **Admin Login**: admin@itms.com / admin123

---

**Status**: ✅ Configuration Fixed - Ready to Deploy!
