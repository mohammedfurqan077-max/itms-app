# Railway Deployment - Quick Visual Guide

## ✅ STEP 1: CODE PUSHED - COMPLETE!

Your code is live at: **https://github.com/Furqan-k77/itms_api**

---

## 🚀 STEP 2: DEPLOY ON RAILWAY

### A. Login to Railway
```
1. Go to: https://railway.app
2. Click "Login"
3. Choose "Login with GitHub"
4. Authorize Railway
```

### B. Create Project
```
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose "Furqan-k77/itms_api"
```

### C. Add Database
```
1. Click "New"
2. Select "Database"
3. Choose "PostgreSQL"
4. Wait 30 seconds
```

### D. Configure Backend
```
1. Click backend service
2. Go to "Settings"
3. Set Root Directory: backend
4. Save
```

### E. Add Environment Variables
```
Click "Variables" tab, add these 8 variables:

1. DATABASE_URL
   Get from PostgreSQL service
   Change postgresql:// to postgresql+asyncpg://
   
2. SECRET_KEY
   Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
   
3. ADMIN_EMAIL
   Value: admin@itms.com
   
4. ADMIN_PASSWORD
   Value: YourSecurePassword123!
   
5. DEBUG
   Value: False
   
6. LOG_LEVEL
   Value: INFO
   
7. ALLOWED_ORIGINS
   Value: *
   
8. ALLOWED_HOSTS
   Value: *
```

### F. Deploy
```
1. Railway auto-deploys
2. Watch "Deployments" tab
3. Wait 2-3 minutes
4. Look for green checkmark ✅
```

### G. Get URL
```
1. Go to "Settings"
2. Find "Networking"
3. Click "Generate Domain"
4. Save your URL!
```

---

## 🧪 STEP 3: TEST

### Test Health
```powershell
curl https://your-app.up.railway.app/health
```

**Expected**: `{"status": "healthy", ...}`

### Test Login
```powershell
curl -X POST https://your-app.up.railway.app/api/v1/auth/login `
  -d "username=admin@itms.com&password=YourSecurePassword123!"
```

**Expected**: `{"access_token": "...", ...}`

### Test Docs
Open in browser:
```
https://your-app.up.railway.app/api/docs
```

**Expected**: Swagger UI with all endpoints

---

## ✅ SUCCESS CHECKLIST

- [x] Code on GitHub
- [ ] Railway account created
- [ ] Project created
- [ ] PostgreSQL added
- [ ] Root directory set to `backend`
- [ ] 8 environment variables added
- [ ] Deployment successful (green ✅)
- [ ] Domain generated
- [ ] Health check works
- [ ] Login works
- [ ] API docs accessible

---

## 🎯 YOUR URLS

Save these after deployment:

```
API Base:   https://your-app.up.railway.app
API Docs:   https://your-app.up.railway.app/api/docs
Health:     https://your-app.up.railway.app/health
```

---

## 🐛 QUICK FIXES

### Build Fails?
- Check root directory = `backend`
- Verify all 8 variables set

### Database Error?
- Use `postgresql+asyncpg://` not `postgresql://`

### App Crashes?
- Check SECRET_KEY is 32+ characters
- Verify all variables set

### 502 Error?
- Wait 2-3 minutes
- Check logs for errors

---

## 💰 COST

- **Free**: $5 credit/month (testing)
- **Hobby**: $5/month (production)
- **Estimated**: ~$5-8/month total

---

## 📞 HELP

- **Railway Discord**: https://discord.gg/railway
- **Your Repo**: https://github.com/Furqan-k77/itms_api
- **Full Guide**: YOUR_RAILWAY_DEPLOYMENT_STEPS.md

---

## ⏱️ TIME ESTIMATE

- Login: 1 minute
- Create project: 2 minutes
- Add database: 1 minute
- Configure: 3 minutes
- Add variables: 3 minutes
- Deploy: 3 minutes
- Test: 2 minutes

**Total: ~15 minutes**

---

**Follow YOUR_RAILWAY_DEPLOYMENT_STEPS.md for detailed instructions!** 🚀
