# Render Deployment Guide

## Overview

This guide covers deploying the Odoyewu backend to Render with PostgreSQL.

## Prerequisites

- GitHub account with your code pushed
- Render account (free tier available)
- Domain name (optional, Render provides free subdomain)

## Quick Start

### Option 1: Deploy with Blueprint (Recommended)

1. **Push to GitHub**
   ```bash
   cd /Users/papa/Desktop/app/backend
   git add .
   git commit -m "Add Render configuration"
   git push
   ```

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Select the repository containing `render.yaml`
   - Click "Apply"

3. **Render will automatically**:
   - Create PostgreSQL database
   - Create web service
   - Set environment variables
   - Deploy your application

### Option 2: Manual Setup

#### Step 1: Create PostgreSQL Database

1. Go to Render Dashboard → "New" → "PostgreSQL"
2. Configure:
   - **Name**: `odoyewu-db`
   - **Database**: `odoyewu`
   - **User**: `odoyewu`
   - **Region**: Choose closest to your users
   - **Plan**: Free (or paid for production)
3. Click "Create Database"
4. **Save the Internal Database URL** (starts with `postgresql://`)

#### Step 2: Create Web Service

1. Go to Render Dashboard → "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `odoyewu-backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or paid for production)

#### Step 3: Set Environment Variables

In the web service settings, add these environment variables:

| Variable | Value | Notes |
|----------|-------|-------|
| `DATABASE_URL` | *From PostgreSQL database* | Use Internal Database URL |
| `SECRET_KEY` | *Generate strong key* | Min 32 characters, use password generator |
| `ENVIRONMENT` | `production` | Required |
| `DEBUG` | `false` | Never true in production |
| `ALLOWED_ORIGINS` | `https://yourdomain.com` | Your frontend URL(s), comma-separated |
| `RATE_LIMIT_ENABLED` | `true` | Recommended |
| `LOG_LEVEL` | `INFO` | Or `WARNING` for less verbose logs |

**Generate SECRET_KEY**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Step 4: Deploy

1. Click "Create Web Service"
2. Render will build and deploy automatically
3. Monitor the logs for any errors

## Post-Deployment

### Run Database Migrations

1. Go to your web service → "Shell"
2. Run migrations:
   ```bash
   python migrate_db.py
   ```

3. Create admin user (optional):
   ```bash
   python create_superuser.py
   ```

### Verify Deployment

1. **Health Check**:
   ```bash
   curl https://your-app.onrender.com/health
   ```

2. **API Docs**:
   - Visit `https://your-app.onrender.com/docs`
   - Note: Disabled in production by default for security

3. **Admin Panel**:
   - Visit `https://your-app.onrender.com/admin`
   - Login with superuser credentials

## Environment Variables Reference

### Required

- `DATABASE_URL` - PostgreSQL connection string (auto-provided by Render)
- `SECRET_KEY` - JWT signing key (min 32 chars)
- `ENVIRONMENT` - Must be `production`

### Optional (with defaults)

- `DEBUG` - Default: `false`
- `ALLOWED_ORIGINS` - Default: empty (configure for CORS)
- `RATE_LIMIT_ENABLED` - Default: `true`
- `RATE_LIMIT_PER_MINUTE` - Default: `60`
- `LOG_LEVEL` - Default: `INFO`
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Default: `30`
- `MAX_UPLOAD_SIZE` - Default: `5242880` (5MB)

## Monitoring

### View Logs

1. Go to your web service
2. Click "Logs" tab
3. Filter by severity if needed

### Metrics

1. Go to your web service
2. Click "Metrics" tab
3. Monitor:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

### Alerts

Set up alerts in Render:
1. Service Settings → "Notifications"
2. Configure email/Slack alerts for:
   - Deploy failures
   - Service crashes
   - High error rates

## Scaling

### Vertical Scaling (Upgrade Plan)

1. Service Settings → "Plan"
2. Choose higher tier for:
   - More CPU/RAM
   - Faster builds
   - Better performance

### Database Scaling

1. Database Settings → "Plan"
2. Upgrade for:
   - More storage
   - Better performance
   - Automatic backups

## Custom Domain

1. Service Settings → "Custom Domain"
2. Add your domain: `api.yourdomain.com`
3. Update DNS records as instructed
4. Render provides free SSL certificate

## Troubleshooting

### Build Failures

**Check Python version**:
- Ensure `requirements.txt` is compatible with Python 3.11
- Check build logs for dependency conflicts

**Missing dependencies**:
- Add system dependencies to `Dockerfile` if needed
- Render uses Ubuntu-based images

### Runtime Errors

**Database connection issues**:
- Verify `DATABASE_URL` is set correctly
- Check database is in same region (lower latency)
- Ensure migrations have run

**Import errors**:
- Check all files are committed to Git
- Verify file paths are correct (case-sensitive)

### Performance Issues

**Slow responses**:
- Upgrade to paid plan for better resources
- Enable database connection pooling (already configured)
- Check database query performance

**Memory issues**:
- Monitor memory usage in Metrics
- Optimize large data operations
- Consider upgrading plan

## Continuous Deployment

Render automatically deploys when you push to your main branch:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

**Disable auto-deploy** (if needed):
- Service Settings → "Auto-Deploy"
- Toggle off
- Deploy manually via "Manual Deploy" button

## Backup & Recovery

### Database Backups

**Free plan**: No automatic backups
**Paid plans**: Daily automatic backups

**Manual backup**:
1. Database → "Backups"
2. Click "Create Backup"

**Restore**:
1. Database → "Backups"
2. Select backup
3. Click "Restore"

### Code Backups

Your code is in Git - always backed up!

## Cost Optimization

### Free Tier Limits

- Web service: Spins down after 15 min inactivity
- Database: 90 days retention, then deleted
- 750 hours/month free

### Recommendations

- **Development**: Use free tier
- **Production**: Upgrade to paid ($7/month web + $7/month DB)
- **Keep services active**: Paid plans don't spin down

## Support

- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)
- [Status Page](https://status.render.com)

## Next Steps

1. ✅ Deploy backend to Render
2. Configure custom domain
3. Set up monitoring alerts
4. Deploy mobile app (Expo EAS)
5. Configure production environment variables in mobile app
