# Command Execution System - Integration Checklist

## Pre-Deployment Checklist

### ✅ Code Implementation
- [x] Command model created with all fields
- [x] Command schemas created with validation
- [x] Command service created with business logic
- [x] Command API endpoints created
- [x] Commands router integrated into main router
- [x] Database migration created
- [x] All tests passing (31/31)

### ✅ Documentation
- [x] Comprehensive guide created
- [x] API examples script created
- [x] Test report generated
- [x] Summary documents created

### 🔲 Database Setup (TODO)
- [ ] Run database migration: `alembic upgrade head`
- [ ] Verify commands table created
- [ ] Verify indexes created
- [ ] Verify foreign keys working

### 🔲 API Testing (TODO)
- [ ] Test POST /commands/send endpoint
- [ ] Test GET /commands/{id} endpoint
- [ ] Test GET /commands endpoint (list)
- [ ] Test POST /commands/{id}/retry endpoint
- [ ] Test POST /commands/{id}/cancel endpoint
- [ ] Test GET /commands/stats/overview endpoint
- [ ] Test GET /commands/pending/list endpoint

### 🔲 Integration Testing (TODO)
- [ ] Test SET_MODE command execution
- [ ] Test SET_TIME command execution
- [ ] Test VIP_MODE command execution
- [ ] Test EMERGENCY_STOP command execution
- [ ] Test HEARTBEAT command execution
- [ ] Test GET_STATUS command execution
- [ ] Test retry logic
- [ ] Test cancel logic
- [ ] Test statistics calculation

### 🔲 Security Testing (TODO)
- [ ] Verify JWT authentication required
- [ ] Verify permission checks working
- [ ] Verify admin-only endpoints protected
- [ ] Verify input validation working
- [ ] Verify SQL injection prevention

### 🔲 Performance Testing (TODO)
- [ ] Test pagination with large datasets
- [ ] Test filtering performance
- [ ] Verify index usage in queries
- [ ] Test concurrent command execution

---

## Deployment Steps

### Step 1: Database Migration
```bash
cd backend
alembic upgrade head
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Running upgrade 003 -> 004, Add command model for command execution tracking
```

**Verification:**
```sql
-- Check table exists
SELECT * FROM commands LIMIT 1;

-- Check indexes
SELECT indexname FROM pg_indexes WHERE tablename = 'commands';
```

### Step 2: Restart Backend Server
```bash
cd backend
# If using Docker
docker-compose restart backend

# If running directly
# Stop current server (Ctrl+C)
uvicorn app.main:app --reload
```

### Step 3: Verify API Endpoints
```bash
# Get JWT token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# Test send command
curl -X POST http://localhost:8000/api/v1/commands/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "junction_id": 1,
    "command_type": "set_mode",
    "payload": {"mode": "auto"},
    "execute_immediately": true
  }' | jq '.'

# Expected: Success response with command_id
```

### Step 4: Test All Command Types
```bash
# Use the provided script
cd backend
chmod +x COMMAND_API_EXAMPLES.sh
# Edit TOKEN variable in script
./COMMAND_API_EXAMPLES.sh
```

### Step 5: Monitor Logs
```bash
# Check for any errors
tail -f logs/app.log

# Look for:
# - Command created messages
# - Command executed messages
# - Any error messages
```

### Step 6: Verify Database
```sql
-- Check commands created
SELECT id, command_type, status, created_at 
FROM commands 
ORDER BY created_at DESC 
LIMIT 10;

-- Check statistics
SELECT 
    command_type,
    status,
    COUNT(*) as count
FROM commands
GROUP BY command_type, status;
```

---

## Post-Deployment Verification

### Functional Tests
- [ ] Can create commands
- [ ] Can execute commands
- [ ] Can retrieve command details
- [ ] Can list commands with pagination
- [ ] Can filter commands by junction/type/status
- [ ] Can retry failed commands
- [ ] Can cancel pending commands
- [ ] Can get statistics
- [ ] Can get pending commands (admin)

### Integration Tests
- [ ] Commands integrate with control service
- [ ] Commands reference junctions correctly
- [ ] Commands track users correctly
- [ ] Status transitions work correctly
- [ ] Retry logic works correctly
- [ ] Error handling works correctly

### Performance Tests
- [ ] Pagination works with 1000+ commands
- [ ] Filtering is fast with indexes
- [ ] Concurrent commands don't conflict
- [ ] Statistics calculation is efficient

### Security Tests
- [ ] Unauthenticated requests are rejected
- [ ] Unauthorized requests are rejected
- [ ] Admin-only endpoints are protected
- [ ] Invalid input is rejected
- [ ] SQL injection attempts fail

---

## Rollback Plan

If issues are found, rollback using:

### Step 1: Rollback Database
```bash
cd backend
alembic downgrade -1
```

### Step 2: Revert Code Changes
```bash
git revert <commit-hash>
# Or manually remove:
# - backend/app/models/command.py
# - backend/app/schemas/command.py
# - backend/app/services/command_service.py
# - backend/app/api/v1/endpoints/commands.py
# - backend/alembic/versions/004_add_command_model.py
# And revert backend/app/api/v1/router.py
```

### Step 3: Restart Server
```bash
docker-compose restart backend
# Or restart uvicorn
```

---

## Monitoring

### Metrics to Monitor
- **Command Success Rate**: Should be > 95%
- **Average Execution Time**: Should be < 2 seconds
- **Pending Commands**: Should be < 10
- **Failed Commands**: Should be < 5%
- **Retry Rate**: Should be < 10%

### Alerts to Set Up
- High failure rate (> 10%)
- Long execution time (> 5 seconds)
- Many pending commands (> 100)
- Repeated failures for same junction
- System errors

### Log Messages to Watch
- "Command created" - Normal
- "Command executed successfully" - Normal
- "Command execution failed" - Investigate
- "Command execution exception" - Alert
- "Retrying command" - Monitor

---

## Troubleshooting

### Issue: Migration Fails
**Symptoms:** Alembic upgrade fails
**Solution:**
1. Check database connection
2. Verify previous migrations applied
3. Check for conflicting table/enum names
4. Review migration file for errors

### Issue: Commands Not Executing
**Symptoms:** Commands stuck in PENDING
**Solution:**
1. Check control service is running
2. Verify junction exists
3. Check logs for errors
4. Verify permissions

### Issue: High Failure Rate
**Symptoms:** Many commands with FAILED status
**Solution:**
1. Check control service logs
2. Verify junction connectivity
3. Check payload validation
4. Review error messages

### Issue: Slow Performance
**Symptoms:** API responses are slow
**Solution:**
1. Verify indexes are created
2. Check database query performance
3. Review pagination settings
4. Monitor database connections

---

## Success Criteria

### Minimum Requirements
- [x] All code files created
- [x] All tests passing
- [ ] Database migration successful
- [ ] All API endpoints working
- [ ] At least one command executed successfully

### Optimal Requirements
- [ ] All command types tested
- [ ] Retry logic verified
- [ ] Statistics working
- [ ] Performance acceptable (< 2s per command)
- [ ] No errors in logs

### Production Ready
- [ ] All functional tests passing
- [ ] All integration tests passing
- [ ] All security tests passing
- [ ] Performance tests passing
- [ ] Monitoring set up
- [ ] Documentation reviewed
- [ ] Team trained

---

## Next Steps After Deployment

### Immediate (Week 1)
1. Monitor command execution
2. Review error logs daily
3. Collect performance metrics
4. Gather user feedback

### Short Term (Month 1)
1. Optimize based on metrics
2. Add missing features if needed
3. Improve error messages
4. Enhance documentation

### Long Term (Quarter 1)
1. Implement WebSocket support
2. Add command scheduling
3. Implement Raspberry Pi integration
4. Add advanced monitoring

---

## Contact & Support

### For Issues
- Check logs first
- Review troubleshooting section
- Check test report for known issues
- Review documentation

### For Questions
- See COMMAND_EXECUTION_GUIDE.md
- See COMMAND_API_EXAMPLES.sh
- See COMMAND_TEST_REPORT.md

---

## Sign-Off

### Development Team
- [ ] Code reviewed
- [ ] Tests passing
- [ ] Documentation complete

### QA Team
- [ ] Functional tests passed
- [ ] Integration tests passed
- [ ] Security tests passed
- [ ] Performance tests passed

### DevOps Team
- [ ] Migration tested
- [ ] Deployment plan reviewed
- [ ] Rollback plan tested
- [ ] Monitoring configured

### Product Owner
- [ ] Requirements met
- [ ] Features verified
- [ ] Documentation approved
- [ ] Ready for production

---

**Status:** Ready for deployment pending checklist completion  
**Date:** April 30, 2026  
**Version:** 1.0
