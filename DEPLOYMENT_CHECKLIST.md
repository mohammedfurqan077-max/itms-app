# Railway Deployment Checklist

## Pre-Deployment

### Code Preparation
- [ ] All code committed to Git
- [ ] `.env` file NOT committed (in `.gitignore`)
- [ ] `requirements.txt` is up to date
- [ ] All tests passing locally
- [ ] Database migrations tested

### Files Created
- [ ] `backend/railway.toml` exists
- [ ] `backend/Procfile` exists
- [ ] `backend/nixpacks.toml` exists
- [ ] `backend/.env.example` exists
- [ ] `backend/requirements-prod.txt` exists

---

## Railway Setup

### Account & Repository
- [ ] Railway account created
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] Railway connected to GitHub

### Project Creation
- [ ] New Railway project created
- [ ] Backend service deployed from GitHub
- [ ] PostgreSQL database added
- [ ] Root directory set to `backend`

---

## Environment Variables

### Required Variables
- [ ] `DATABASE_URL` (with `postgresql+asyncpg://`)
- [ ] `SECRET_KEY` (32+ characters)
- [ ] `ADMIN_EMAIL`
- [ ] `ADMIN_PASSWORD`

### Optional Variables
- [ ] `DEBUG=False`
- [ ] `LOG_LEVEL=INFO`
- [ ] `ALLOWED_ORIGINS`
- [ ] `ALLOWED_HOSTS`
- [ ] `CONTROL_SYSTEM_URL`
- [ ] `CONTROL_SYSTEM_API_KEY`

---

## Deployment

### Build & Deploy
- [ ] Deployment triggered
- [ ] Build logs show success
- [ ] Migrations ran successfully
- [ ] App started without errors
- [ ] Command executor started

### Domain & Networking
- [ ] Public domain generated
- [ ] HTTPS working
- [ ] Health endpoint accessible

---

## Testing

### Basic Tests
- [ ] `GET /health` returns 200
- [ ] `POST /auth/login` works
- [ ] `GET /auth/me` returns user
- [ ] `GET /api/docs` shows Swagger UI

### Database Tests
- [ ] Admin user exists
- [ ] Can create junction
- [ ] Can create command
- [ ] Command executor processes commands

### Full Validation
- [ ] Run `test_full_system_validation.py` against production
- [ ] All endpoints responding
- [ ] No ENUM errors
- [ ] Commands executing

---

## Post-Deployment

### Monitoring
- [ ] Logs accessible in Railway
- [ ] Metrics showing normal usage
- [ ] No error spikes

### Documentation
- [ ] API URL documented
- [ ] Admin credentials saved securely
- [ ] Environment variables documented

### Frontend Integration
- [ ] Frontend API URL updated
- [ ] CORS configured correctly
- [ ] Frontend can connect to backend

---

## Production Checklist

### Security
- [ ] `DEBUG=False`
- [ ] Strong passwords used
- [ ] CORS restricted to specific origins
- [ ] HTTPS enforced
- [ ] Rate limiting enabled

### Performance
- [ ] Database indexes created
- [ ] Connection pooling configured
- [ ] Command executor running
- [ ] No memory leaks

### Backup & Recovery
- [ ] Database backup strategy
- [ ] Deployment rollback tested
- [ ] Environment variables backed up

---

## Quick Commands

### Test Deployment
```bash
# Set your API URL
export API_URL="https://your-app.railway.app"

# Health check
curl $API_URL/health

# Login
curl -X POST $API_URL/api/v1/auth/login \
  -d "username=admin@itms.com&password=YourPassword"

# Get stats
curl -X GET $API_URL/api/v1/system/stats \
  -H "Authorization: Bearer $TOKEN"
```

### Update Deployment
```bash
git add .
git commit -m "Update"
git push origin main
```

### View Logs
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and link
railway login
railway link

# View logs
railway logs
```

---

## Troubleshooting

### Build Fails
- [ ] Check build logs in Railway
- [ ] Verify `requirements.txt`
- [ ] Test build locally

### Database Connection Error
- [ ] Verify `DATABASE_URL` format
- [ ] Check database is running
- [ ] Test connection locally

### App Crashes
- [ ] Check application logs
- [ ] Verify all env vars set
- [ ] Check for syntax errors

### 502 Bad Gateway
- [ ] Verify app listens on `$PORT`
- [ ] Check start command
- [ ] Review startup logs

---

## Success Criteria

✅ **Deployment Successful When**:
- Health endpoint returns 200
- Can login with admin credentials
- Can create and retrieve data
- Command executor is running
- No errors in logs
- Frontend can connect

---

## Timeline

- **Setup**: 5 minutes
- **Configuration**: 5 minutes
- **Deployment**: 5 minutes
- **Testing**: 5 minutes
- **Total**: ~20 minutes

---

## Support Resources

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **ITMS Guide**: `RAILWAY_DEPLOYMENT_GUIDE.md`
- **Testing Guide**: `backend/TESTING_GUIDE.md`

---

**Ready to Deploy?** Follow `RAILWAY_DEPLOYMENT_GUIDE.md` step by step!
