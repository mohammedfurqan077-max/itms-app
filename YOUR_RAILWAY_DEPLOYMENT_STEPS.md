# Your Railway Deployment Steps

## ✅ Step 1: Code Pushed to GitHub - COMPLETE!

Your code is now at: **https://github.com/Furqan-k77/itms_api**

---

## 🚀 Step 2: Deploy on Railway (Follow These Steps)

### 2.1 Login to Railway

1. Open your browser and go to: **[https://railway.app](https://railway.app)**
2. Click **"Login"** button (top right)
3. Select **"Login with GitHub"**
4. Authorize Railway to access your GitHub account

---

### 2.2 Create New Project

1. After login, click **"New Project"** button
2. Select **"Deploy from GitHub repo"**
3. You'll see a list of your repositories
4. Find and click: **"Furqan-k77/itms_api"**
5. Railway will start analyzing your repository

---

### 2.3 Add PostgreSQL Database

1. In your project dashboard, click **"New"** button
2. Select **"Database"**
3. Choose **"PostgreSQL"**
4. Railway will provision a PostgreSQL database (takes ~30 seconds)
5. You'll see a new "PostgreSQL" service appear

---

### 2.4 Configure Backend Service

1. Click on your **backend service** (the one that's not PostgreSQL)
2. Go to **"Settings"** tab
3. Scroll down to **"Root Directory"**
4. Enter: `backend`
5. Click **"Save"** or it saves automatically

---

### 2.5 Add Environment Variables

1. Stay in your backend service
2. Click on **"Variables"** tab
3. Click **"New Variable"** button
4. Add these variables one by one:

#### Variable 1: DATABASE_URL
```
Name: DATABASE_URL
Value: [Get from PostgreSQL service - see instructions below]
```

**How to get DATABASE_URL**:
- Click on your **PostgreSQL** service
- Go to **"Variables"** tab
- Find **DATABASE_URL** and copy its value
- It will look like: `postgresql://postgres:password@host:port/railway`
- **IMPORTANT**: Change `postgresql://` to `postgresql+asyncpg://`
- Final format: `postgresql+asyncpg://postgres:password@host:port/railway`

#### Variable 2: SECRET_KEY
```
Name: SECRET_KEY
Value: [Generate using command below]
```

**Generate SECRET_KEY**:
Open PowerShell on your computer and run:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copy the output and paste it as the value.

#### Variable 3: ADMIN_EMAIL
```
Name: ADMIN_EMAIL
Value: admin@itms.com
```

#### Variable 4: ADMIN_PASSWORD
```
Name: ADMIN_PASSWORD
Value: YourSecurePassword123!
```
**Note**: Change this to a strong password you'll remember!

#### Variable 5: DEBUG
```
Name: DEBUG
Value: False
```

#### Variable 6: LOG_LEVEL
```
Name: LOG_LEVEL
Value: INFO
```

#### Variable 7: ALLOWED_ORIGINS
```
Name: ALLOWED_ORIGINS
Value: *
```
**Note**: Change this later when you have a frontend URL

#### Variable 8: ALLOWED_HOSTS
```
Name: ALLOWED_HOSTS
Value: *
```

---

### 2.6 Deploy Your Application

1. Railway will automatically start deploying
2. Click on **"Deployments"** tab to watch progress
3. Click on the latest deployment to see logs

**Expected logs** (wait 2-3 minutes):
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
[app] INFO: CommandExecutor initialized
[app] INFO: CommandExecutor started
[app] INFO: Application startup complete
```

✅ **Green checkmark** = Deployment successful!

---

### 2.7 Get Your API URL

1. Go back to your backend service
2. Click on **"Settings"** tab
3. Scroll to **"Networking"** section
4. Click **"Generate Domain"** button
5. Railway will give you a URL like: `https://itms-api-production-xxxx.up.railway.app`

**Save this URL!** This is your API endpoint.

---

## 🧪 Step 3: Test Your Deployment

### 3.1 Test Health Endpoint

Open your browser or use PowerShell:

```powershell
# Replace with your actual Railway URL
$API_URL = "https://itms-api-production-xxxx.up.railway.app"

# Test health
curl "$API_URL/health"
```

**Expected response**:
```json
{
  "status": "healthy",
  "app": "ITMS Backend",
  "version": "1.0.0"
}
```

### 3.2 Test API Documentation

Open in browser:
```
https://your-railway-url.up.railway.app/api/docs
```

You should see Swagger UI with all your API endpoints!

### 3.3 Test Login

```powershell
# Login
curl -X POST "$API_URL/api/v1/auth/login" `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=admin@itms.com&password=YourSecurePassword123!"
```

**Expected response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

✅ **If you get a token, your deployment is successful!**

---

## 📊 Step 4: Monitor Your Application

### View Logs
1. Go to your backend service in Railway
2. Click **"Logs"** tab
3. Watch real-time logs

### Check Metrics
1. Click **"Metrics"** tab
2. View CPU, Memory, Network usage

---

## 🎉 Success Checklist

- [x] Code pushed to GitHub
- [ ] Railway project created
- [ ] PostgreSQL database added
- [ ] Backend service configured (root directory = `backend`)
- [ ] All 8 environment variables added
- [ ] Deployment successful (green checkmark)
- [ ] Domain generated
- [ ] Health endpoint returns 200
- [ ] Can login with admin credentials
- [ ] API docs accessible

---

## 🐛 Troubleshooting

### Issue: Build Fails

**Check**:
1. Go to "Deployments" → Click on failed deployment
2. Read the error logs

**Common fixes**:
- Verify root directory is set to `backend`
- Check all environment variables are set
- Ensure DATABASE_URL uses `postgresql+asyncpg://`

### Issue: Database Connection Error

**Fix**:
1. Go to PostgreSQL service → Variables
2. Copy DATABASE_URL
3. Change `postgresql://` to `postgresql+asyncpg://`
4. Update in backend service variables

### Issue: App Crashes on Startup

**Check**:
1. View logs in Railway
2. Look for error messages

**Common fixes**:
- Verify SECRET_KEY is at least 32 characters
- Check all required environment variables are set
- Ensure ADMIN_PASSWORD is set

### Issue: 502 Bad Gateway

**Wait**: Give it 2-3 minutes for first deployment

**If persists**:
1. Check logs for errors
2. Verify app started successfully
3. Redeploy if needed

---

## 💰 Cost Information

### Free Tier
- $5 credit per month
- Good for testing
- May sleep after inactivity

### Hobby Plan ($5/month)
- $5 credit included
- No sleeping
- Recommended for production

### Estimated Monthly Cost
- Backend service: ~$3-5
- PostgreSQL database: ~$2-3
- **Total**: ~$5-8/month

---

## 🔄 Updating Your Deployment

When you make changes to your code:

```powershell
# In D:\ITMS_APP directory
git add .
git commit -m "Your changes description"
git push origin main
```

Railway will automatically detect the push and redeploy!

---

## 📞 Need Help?

### Railway Support
- **Discord**: https://discord.gg/railway
- **Docs**: https://docs.railway.app
- **Status**: https://status.railway.app

### Check Your Deployment
1. Go to Railway dashboard
2. Click on your backend service
3. Check "Logs" tab for errors
4. Check "Metrics" tab for resource usage

---

## 🎯 Your URLs

After deployment, save these:

- **API Base**: `https://your-app.up.railway.app`
- **API Docs**: `https://your-app.up.railway.app/api/docs`
- **Health Check**: `https://your-app.up.railway.app/health`
- **Admin Login**: Use at `/api/v1/auth/login`

---

## ✅ Next Steps After Deployment

1. **Test All Endpoints**: Use Swagger UI at `/api/docs`
2. **Create Junctions**: Add your traffic junctions via API
3. **Test Commands**: Create and monitor commands
4. **Connect Frontend**: Update frontend with your Railway URL
5. **Monitor**: Check logs and metrics regularly

---

## 🎊 Congratulations!

Once you complete all steps, your ITMS backend will be:
- ✅ Live on the internet
- ✅ Accessible via HTTPS
- ✅ Connected to PostgreSQL database
- ✅ Running command executor
- ✅ Ready for frontend integration

**Deployment Time**: ~10-15 minutes  
**Difficulty**: Easy  
**Your Repository**: https://github.com/Furqan-k77/itms_api

---

**Ready to deploy?** Follow the steps above carefully! 🚀
