"""
Health check and monitoring endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from datetime import datetime
import psutil
import sys

router = APIRouter(prefix="/health", tags=["Health"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Odoyewu API"
    }

@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with database and system info"""
    
    # Check database connection
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
        db_error = None
    except Exception as e:
        db_status = "unhealthy"
        db_error = str(e)
    
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": {
                "status": db_status,
                "error": db_error
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / 1048576,
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / 1073741824
            }
        },
        "version": {
            "python": sys.version,
            "api": "1.0.0"
        }
    }

@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Kubernetes readiness probe"""
    try:
        db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not ready", "error": str(e)}

@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive"}
