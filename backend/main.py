from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import db_manager
from app.routers import auth, upload, detect, history, report

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB Atlas and build indexes (if configured)
    await db_manager.connect()
    yield
    # Shutdown: Close database connections
    db_manager.close()

app = FastAPI(
    title="Gaia Detector API",
    description="Backend API for AI Content Authenticity Detection with FastAPI, MongoDB Atlas, and Google Drive.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React Vite frontend (supports credentials for httpOnly cookies)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(detect.router)
app.include_router(history.router)
app.include_router(report.router)

@app.get("/health", tags=["System"])
async def health_check():
    """Liveness check: returns 200 as long as the application process is running."""
    return {
        "status": "healthy",
        "app_env": settings.APP_ENV,
        "database": {
            "configured": settings.is_mongodb_configured,
        },
        "google_drive": {
            "configured": settings.is_gdrive_configured
        }
    }

@app.get("/ready", tags=["System"])
async def readiness_check(response: Response):
    """
    Readiness check: checks whether dependent services are ready to accept traffic.
    Returns 200 if dependencies are ready, or 503 if required services are failing.
    """
    db_ok = False
    if settings.is_mongodb_configured:
        db_ok = await db_manager.ping()
        if not db_ok:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {
                "status": "not_ready",
                "database": {"connected": False, "error": "Database ping failed"},
                "google_drive": {"configured": settings.is_gdrive_configured}
            }
    
    return {
        "status": "ready",
        "database": {
            "configured": settings.is_mongodb_configured,
            "connected": db_ok if settings.is_mongodb_configured else "not_configured"
        },
        "google_drive": {
            "configured": settings.is_gdrive_configured
        }
    }

@app.get("/", tags=["System"])
def root():
    return {
        "name": "Gaia Detector API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.BACKEND_HOST, port=settings.BACKEND_PORT, reload=True)
