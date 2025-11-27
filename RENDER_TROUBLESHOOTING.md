# Render Deployment Troubleshooting Guide

## Fixed Issues

✅ **Removed duplicate dependencies** from `requirements.txt`
✅ **Created `runtime.txt`** to specify Python 3.11
✅ **Removed PYTHON_VERSION** from `render.yaml` (handled by runtime.txt)

## Common Deployment Failures

### 1. Build Failures

#### Error: "Could not find a version that satisfies the requirement"

**Solution**: Check `requirements.txt` for:
- Duplicate entries ✅ (Fixed)
- Incompatible versions
- Typos in package names

#### Error: "Python version not found"

**Solution**: Ensure `runtime.txt` exists with correct format:
```
python-3.11.0
```
✅ Created

### 2. Database Connection Failures

#### Error: "could not connect to server"

**Checklist**:
- ✅ Database created in Render
- ✅ Database name matches `render.yaml` (`odoyewu-db`)
- ✅ `DATABASE_URL` env var configured correctly

**Verify in Render Dashboard**:
1. Go to your database
2. Copy "Internal Database URL"
3. Verify it's set in web service environment variables

### 3. Application Start Failures

#### Error: "Application startup failed"

**Check**:
- Missing `SECRET_KEY` environment variable
- Database migrations not run
- Import errors in code

**Solution**:
```bash
# In Render Shell
python migrate_db.py
```

### 4. Health Check Failures

#### Error: "Health check failed"

**Verify**:
- `/health` endpoint exists and returns 200
- Application actually started
- No errors in logs

**Test locally**:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
curl http://localhost:8000/health
```

## Step-by-Step Deployment

### 1. Push Fixed Code to GitHub

```bash
cd /Users/papa/Desktop/app/backend
git add .
git commit -m "Fix Render deployment: clean requirements.txt, add runtime.txt"
git push
```

### 2. Redeploy on Render

**Option A: Automatic (if connected to GitHub)**
- Render will auto-deploy on push

**Option B: Manual**
1. Go to Render Dashboard
2. Select your web service
3. Click "Manual Deploy" → "Deploy latest commit"

### 3. Monitor Deployment

Watch the logs in real-time:
1. Go to your web service
2. Click "Logs" tab
3. Look for:
   - ✅ "Build successful"
   - ✅ "Starting service"
   - ✅ "Application startup complete"

### 4. Run Database Migrations

Once deployed:
1. Go to web service → "Shell"
2. Run:
   ```bash
   python migrate_db.py
   ```

### 5. Verify Deployment

```bash
# Replace with your Render URL
curl https://odoyewu-backend.onrender.com/health

# Should return:
# {"status": "healthy"}
```

## Environment Variables Checklist

Verify these are set in Render Dashboard → Web Service → Environment:

| Variable | Value | Source |
|----------|-------|--------|
| `DATABASE_URL` | `postgresql://...` | From database |
| `SECRET_KEY` | `<generated>` | Auto-generated |
| `ENVIRONMENT` | `production` | render.yaml |
| `DEBUG` | `false` | render.yaml |
| `ALLOWED_ORIGINS` | `http://localhost:8081,...` | render.yaml |
| `RATE_LIMIT_ENABLED` | `true` | render.yaml |
| `LOG_LEVEL` | `INFO` | render.yaml |

## Viewing Logs

### Build Logs
Shows pip install, dependency resolution:
```
Render Dashboard → Web Service → Events → Select deploy → View logs
```

### Runtime Logs
Shows application startup, errors, requests:
```
Render Dashboard → Web Service → Logs
```

### Database Logs
Shows connection attempts, queries:
```
Render Dashboard → Database → Logs
```

## Common Error Messages

### "ModuleNotFoundError: No module named 'X'"

**Cause**: Missing dependency in `requirements.txt`

**Solution**: Add to `requirements.txt` and redeploy

### "sqlalchemy.exc.OperationalError: could not connect"

**Cause**: Database not ready or wrong connection string

**Solution**:
1. Check database is running
2. Verify `DATABASE_URL` in environment variables
3. Check database is in same region as web service

### "SECRET_KEY validation error"

**Cause**: SECRET_KEY not set or too short

**Solution**:
1. Go to Environment variables
2. Verify `SECRET_KEY` exists
3. Should be at least 32 characters

### "Port already in use"

**Cause**: Not using Render's `$PORT` variable

**Solution**: Verify `startCommand` in `render.yaml`:
```yaml
startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
```
✅ Already correct

## Testing Checklist

After successful deployment:

- [ ] Health check responds: `/health`
- [ ] API docs accessible (if not production): `/docs`
- [ ] Admin panel accessible: `/admin`
- [ ] Database migrations run successfully
- [ ] Can create test user
- [ ] API endpoints work: `/api/v1/auth/signup`
- [ ] WebSocket connections work
- [ ] Logs show no errors

## Getting Help

If deployment still fails:

1. **Check Render Status**: https://status.render.com
2. **Review logs**: Copy full error message
3. **Check Render Community**: https://community.render.com
4. **Contact Support**: support@render.com (for paid plans)

## Next Steps After Successful Deployment

1. ✅ Note your Render URL: `https://odoyewu-backend.onrender.com`
2. Update mobile app `.env`:
   ```bash
   EXPO_PUBLIC_API_URL=https://odoyewu-backend.onrender.com
   ```
3. Test mobile app connection
4. Set up custom domain (optional)
5. Configure monitoring/alerts
6. Set up automatic backups (paid plan)

## Rollback Plan

If deployment breaks production:

1. Go to Render Dashboard → Web Service
2. Click "Manual Deploy"
3. Select previous working commit
4. Click "Deploy"

Your previous version will be restored.
