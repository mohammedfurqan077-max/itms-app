# Deploy ITMS Backend to Railway - Quick Start

## 🚀 5-Minute Deployment

### Step 1: Push to GitHub (2 minutes)

```bash
# Initialize git (if not done)
cd D:\ITMS_APP
git init
git add .
git commit -m "Initial commit"

# Create GitHub repo and push
# Go to github.com → New Repository → "itms-backend"
git remote add origin https://github.com/YOUR_USERNAME/itms-backend.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Railway (3 minutes)

1. **Go to [railway.app](https://railway.app)** → Login with GitHub

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `itms-backend`

3. **Add PostgreSQL**:
   - Click "New" → "Database" → "PostgreSQL"

4. **Configure Backend Service**:
   - Click on your backend service
   - Go to "Settings"
   - Set "Root Directory" to: `backend`

5. **Add Environment Variables**:
   Click "Variables" tab and add:

   ```bash
   # Copy DATABASE_URL from PostgreSQL service
   # IMPORTANT: Change postgresql:// to postgresql+asyncpg://
   DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
   
   # Generate secret key (run locally):
   # python -c "import secrets; print(secrets.token_urlsafe(32))"
   SECRET_KEY=your-generated-secret-key-here
   
   # Admin credentials
   ADMIN_EMAIL=admin@itms.com
   ADMIN_PASSWORD=YourSecurePassword123!
   
   # Application settings
   DEBUG=False
   LOG_LEVEL=INFO
   ALLOWED_ORIGINS=*
   ALLOWED_HOSTS=*
   ```

6. **Deploy**:
   - Railway will automatically deploy
   - Wait for build to complete (~2-3 minutes)

7. **Get Your URL**:
   - Go to "Settings" → "Networking"
   - Click "Generate Domain"
   - You'll get: `https://your-app.railway.app`

### Step 3: Test Your Deployment

```bash
# Set your URL
export API_URL="https://your-app.railway.app"

# Test health
curl $API_URL/health

# Test login
curl -X POST $API_URL/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@itms.com&password=YourSecurePassword123!"
```

**Expected Response**:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

✅ **Done!** Your backend is live at `https://your-app.railway.app`

---

## 📋 What Railway Does Automatically

✅ Detects Python project  
✅ Installs dependencies from `requirements.txt`  
✅ Runs database migrations (`alembic upgrade head`)  
✅ Starts the application  
✅ Provides HTTPS  
✅ Auto-restarts on crashes  
✅ Scales automatically  

---

## 🔧 Configuration Files

Railway uses these files (already created):

- **`backend/railway.toml`** - Railway configuration
- **`backend/Procfile`** - Start command
- **`backend/nixpacks.toml`** - Build settings
- **`backend/start.sh`** - Startup script

---

## 🌐 Your API Endpoints

Once deployed, your API will be available at:

- **Health**: `https://your-app.railway.app/health`
- **API Docs**: `https://your-app.railway.app/api/docs`
- **API Base**: `https://your-app.railway.app/api/v1`

### Example Endpoints:
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user
- `GET /api/v1/junctions` - List junctions
- `POST /api/v1/commands/send` - Create command
- `GET /api/v1/system/stats` - System statistics

---

## 🔐 Important Security Notes

### 1. Change Default Passwords
```bash
# Generate strong secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Use strong admin password (min 8 chars, mixed case, numbers, symbols)
ADMIN_PASSWORD=MySecure@Pass123!
```

### 2. Configure CORS
Once you have a frontend:
```bash
ALLOWED_ORIGINS=https://your-frontend.railway.app,https://yourdomain.com
```

### 3. Set DEBUG to False
```bash
DEBUG=False
```

---

## 📊 Monitoring Your App

### View Logs
1. Go to Railway dashboard
2. Click on your service
3. Click "Logs" tab
4. Watch real-time logs

### Check Metrics
1. Click "Metrics" tab
2. View CPU, Memory, Network usage

### Expected Logs
```
INFO: Starting ITMS Backend...
INFO: CommandExecutor initialized
INFO: CommandExecutor started
INFO: CommandExecutor loop started
INFO: Application startup complete
INFO: Uvicorn running on http://0.0.0.0:PORT
```

---

## 🔄 Updating Your Deployment

### Automatic (Recommended)
```bash
# Make changes
git add .
git commit -m "Your changes"
git push origin main

# Railway automatically deploys
```

### Manual
1. Go to Railway dashboard
2. Click "Deploy"
3. Select commit

### Rollback
1. Go to "Deployments"
2. Find previous version
3. Click "Redeploy"

---

## 🧪 Testing Your Deployment

### Quick Test
```bash
# Install test dependencies
pip install httpx

# Run validation
cd backend
python test_full_system_validation.py
```

### Manual Test
```bash
export API_URL="https://your-app.railway.app"
export TOKEN="your-token-here"

# Create junction
curl -X POST $API_URL/api/v1/junctions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Main Junction",
    "location": "City Center",
    "ip_address": "192.168.1.100",
    "status": "active"
  }'

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

## 💰 Cost

### Free Tier
- $5 credit per month
- Good for testing
- May sleep after inactivity

### Hobby Plan ($5/month)
- $5 credit included
- No sleeping
- Better for production

### Estimated Cost
- Backend: ~$3-5/month
- PostgreSQL: ~$2-3/month
- **Total**: ~$5-8/month

---

## 🐛 Troubleshooting

### Build Fails
**Check**: Build logs in Railway  
**Fix**: Verify `requirements.txt` and `backend/` directory

### Database Connection Error
**Check**: `DATABASE_URL` format  
**Fix**: Ensure it uses `postgresql+asyncpg://` (not just `postgresql://`)

### App Crashes
**Check**: Application logs  
**Fix**: Verify all environment variables are set

### 502 Bad Gateway
**Check**: Start command  
**Fix**: Ensure app listens on `0.0.0.0:$PORT`

### Migrations Fail
**Check**: Database is accessible  
**Fix**: Verify `DATABASE_URL` is correct

---

## 📚 Additional Resources

- **Full Guide**: `RAILWAY_DEPLOYMENT_GUIDE.md`
- **Checklist**: `DEPLOYMENT_CHECKLIST.md`
- **Testing**: `backend/TESTING_GUIDE.md`
- **Railway Docs**: https://docs.railway.app

---

## ✅ Success Checklist

- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] PostgreSQL database added
- [ ] Environment variables configured
- [ ] Deployment successful
- [ ] Health endpoint returns 200
- [ ] Can login with admin credentials
- [ ] API documentation accessible
- [ ] Command executor running

---

## 🎉 Next Steps

1. **Test All Endpoints**: Use Swagger UI at `/api/docs`
2. **Create Junctions**: Add your traffic junctions
3. **Test Commands**: Create and monitor commands
4. **Connect Frontend**: Update frontend API URL
5. **Custom Domain**: Add your own domain (optional)
6. **Monitor**: Set up alerts and monitoring

---

## 🆘 Need Help?

- **Railway Discord**: https://discord.gg/railway
- **Railway Docs**: https://docs.railway.app
- **Check Logs**: Railway dashboard → Logs tab
- **Review Guide**: `RAILWAY_DEPLOYMENT_GUIDE.md`

---

**Deployment Time**: 5 minutes  
**Difficulty**: Easy  
**Cost**: ~$5-8/month  
**Status**: Production-ready ✅

Your ITMS backend is now live on Railway! 🚀
