"""
DropFlow v2 - FastAPI Application (Simplified for Render)
Minimal production-ready version without heavy dependencies
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="DropFlow v2 API",
    version="2.0.0",
    description="Dropshipping automation engine"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Content-Type", "Authorization"],
)

# ============ HEALTH & INFO ============

@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "DropFlow v2",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health/live")
async def liveness():
    """Kubernetes liveness probe"""
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness():
    """Kubernetes readiness probe"""
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/v1/info")
async def api_info():
    """API version and capabilities"""
    return {
        "name": "DropFlow v2 API",
        "version": "2.0.0",
        "status": "production-ready"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "DropFlow v2",
        "version": "2.0.0",
        "status": "ready",
        "endpoints": {
            "health": "/health",
            "info": "/v1/info",
            "docs": "/docs"
        }
    }

# ============ ERROR HANDLERS ============

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle all exceptions"""
    logger.error(f"[ERROR] {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
