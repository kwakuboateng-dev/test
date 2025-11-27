# NearLove - Docker Deployment Guide

## 🚀 Quick Start with Docker

### Prerequisites
- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

### One-Command Deployment

```bash
# Clone or navigate to the project
cd /path/to/nearlove

# Create .env file from example
cp .env.example .env

# Start the entire stack
docker-compose up -d
```

That's it! The API will be available at `http://localhost:8000`

---

## 📦 What Gets Deployed

The `docker-compose up` command starts:
1. **PostgreSQL Database** (port 5432)
   - Automatically creates `nearlove` database
   - Persistent data storage via Docker volumes
   
2. **FastAPI Backend** (port 8000)
   - Automatically creates all database tables
   - Hot-reload enabled for development
   - API docs at `http://localhost:8000/docs`

---

## 🔧 Configuration

### Environment Variables

Edit `.env` file to configure:

```bash
# Database
POSTGRES_USER=nearlove
POSTGRES_PASSWORD=nearlove123
POSTGRES_DB=nearlove

# Backend
SECRET_KEY=your-super-secret-jwt-key-change-in-production
DATABASE_URL=postgresql://nearlove:nearlove123@db:5432/nearlove
```

**⚠️ IMPORTANT**: Change `SECRET_KEY` for production deployments!

---

## 📋 Common Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Just backend
docker-compose logs -f backend

# Just database
docker-compose logs -f db
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

### Stop and Remove Everything (including volumes)
```bash
docker-compose down -v
```

---

## 🗄️ Database Management

### Access PostgreSQL CLI
```bash
docker-compose exec db psql -U nearlove -d nearlove
```

### Run SQL Commands
```bash
docker-compose exec db psql -U nearlove -d nearlove -c "SELECT * FROM users;"
```

### Backup Database
```bash
docker-compose exec db pg_dump -U nearlove nearlove > backup.sql
```

### Restore Database
```bash
docker-compose exec -T db psql -U nearlove nearlove < backup.sql
```

---

## 🔍 Testing the API

Once running, you can:

1. **View API Documentation**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

2. **Test Endpoints**
   ```bash
   # Health check
   curl http://localhost:8000/
   
   # Create user
   curl -X POST http://localhost:8000/auth/signup \
     -H "Content-Type: application/json" \
     -d '{"email":"test@test.com","password":"test123","anonymous_handle":"TestUser1"}'
   ```

---

## 📱 Connecting Mobile App

Update `mobile/src/services/api.js`:

```javascript
// For local development with Docker
const API_BASE_URL = 'http://localhost:8000';

// For physical device (replace with your computer's IP)
const API_BASE_URL = 'http://192.168.1.XXX:8000';
```

Find your IP:
- **Mac/Linux**: `ifconfig | grep "inet "`
- **Windows**: `ipconfig`

---

## 🏗️ Production Deployment

### 1. Update Environment Variables
```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env
SECRET_KEY=<generated-key>
POSTGRES_PASSWORD=<strong-password>
```

### 2. Disable Hot-Reload
Edit `docker-compose.yml`, change backend CMD:
```yaml
command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Deploy to Cloud

**Option A: Docker Compose on VPS (DigitalOcean, AWS EC2)**
```bash
# On server
git clone <your-repo>
cd nearlove
cp .env.example .env
# Edit .env with production values
docker-compose up -d
```

**Option B: Container Registry (Docker Hub, ECR, GCR)**
```bash
# Build and push
docker build -t yourusername/nearlove-backend ./backend
docker push yourusername/nearlove-backend

# Deploy on cloud platform
```

### 4. Setup Nginx (Recommended)
```nginx
server {
    listen 80;
    server_name api.nearlove.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🐛 Troubleshooting

### Database Connection Errors
```bash
# Check if database is running
docker-compose ps

# View database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Backend Won't Start
```bash
# View backend logs
docker-compose logs backend

# Rebuild backend
docker-compose up -d --build backend
```

### Port Already in Use
```bash
# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Instead of 8000:8000
```

### Reset Everything
```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Rebuild from scratch
docker-compose up -d --build
```

---

## 📊 Monitoring

### Check Service Health
```bash
# View running containers
docker-compose ps

# Check resource usage
docker stats
```

### Database Size
```bash
docker-compose exec db psql -U nearlove -d nearlove -c "
SELECT pg_size_pretty(pg_database_size('nearlove'));
"
```

---

## 🎯 Next Steps

1. ✅ Start services: `docker-compose up -d`
2. ✅ Check API: `http://localhost:8000/docs`
3. ✅ Update mobile app API URL
4. ✅ Test the full flow
5. ✅ Deploy to production

---

## 📝 Directory Structure

```
nearlove/
├── docker-compose.yml       # Orchestration config
├── .env.example             # Environment template
├── .env                     # Your config (gitignored)
├── backend/
│   ├── Dockerfile           # Backend container
│   ├── entrypoint.sh        # Startup script
│   ├── requirements.txt     # Python dependencies
│   └── ... (FastAPI code)
└── mobile/
    └── ... (React Native code)
```

---

## ✅ Deployment Checklist

- [ ] Update `SECRET_KEY` in `.env`
- [ ] Update `POSTGRES_PASSWORD` in `.env`
- [ ] Test locally with `docker-compose up`
- [ ] Update mobile app API URL
- [ ] Test signup/login flow
- [ ] Test proximity matching
- [ ] Test chat functionality
- [ ] Setup backup strategy
- [ ] Configure monitoring
- [ ] Setup HTTPS (Let's Encrypt)
- [ ] Deploy to production server

Happy deploying! 🚀
