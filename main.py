"""
DropFlow v2 - FastAPI Application
Unified via CLAUDE CORE decision engine

Production-ready with:
- Type hints strict
- Lifespan handlers
- Structured logging
- Prometheus metrics
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path
import logging
from typing import List, Optional

from config import settings
from database import get_db, init_db, DatabaseQueries
from models import StoreResponse, StatsResponse, ProductResponse
from sentry_config import setup_sentry, is_enabled
import stripe

# CLAUDE CORE - Central decision engine
import sys
sys.path.insert(0, str(Path(__file__).parent))
from claude_core import ClaudeCore, ProjectType, RequestType
from agents import UnifiedAgent, AgentType
from projects import PROJECTS

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Logging - use structured JSON
from logging_json import setup_json_logging, get_json_logger
setup_json_logging("dropflow", settings.LOG_LEVEL)
logger = get_json_logger()

# Prometheus imports - use REGISTRY to avoid duplicates
from prometheus_client import CollectorRegistry, Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Use custom registry to avoid conflicts
custom_registry = CollectorRegistry()
http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'], registry=custom_registry)
http_request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'], registry=custom_registry)
http_active_connections = Gauge('http_active_connections', 'Active HTTP connections', registry=custom_registry)

# Structured logging setup function (currently using stdlib logging)
def setup_structured_logging() -> None:
    """Configure structured JSON logging - placeholder for future"""
    pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler for startup/shutdown"""
    global claude_core, agent
    
    # Setup Sentry for error tracking
    import os
    sentry_dsn = os.environ.get("SENTRY_DSN")
    if sentry_dsn:
        setup_sentry(sentry_dsn, settings.ENVIRONMENT)
        logger.info("Sentry error tracking enabled")
    
    logger.info("DropFlow v2 starting - version 2.0.0")
    
    init_db()
    logger.info("Database initialized")
    
    claude_core = ClaudeCore()
    logger.info("CLAUDE CORE initialized")
    
    agent = UnifiedAgent(agent_id="main-agent", name="DropFlow Main Agent", agent_type=AgentType.GENERIC)
    logger.info("Unified Agent initialized")
    
    project_type_map = {
        "p1_product_discovery": ProjectType.P1_PRODUCT_DISCOVERY,
        "p2_media_automation": ProjectType.P2_MEDIA_AUTOMATION,
        "p3_kids_content": ProjectType.P3_KIDS_CONTENT,
        "p4_music_generation": ProjectType.P4_MUSIC_GENERATION,
        "p5_future": ProjectType.P5_FUTURE,
    }
    
    for project_id, orchestrator_class in PROJECTS.items():
        orchestrator = orchestrator_class()
        project_type = project_type_map.get(project_id)
        if project_type:
            claude_core.register_project(project_type, orchestrator)
            logger.info(f"Project {project_id} registered")
    
    logger.info("DropFlow v2 CLAUDE CORE - READY")
    
    yield
    logger.info("Application shutting down")

# FastAPI app with lifespan
app = FastAPI(
    title="DropFlow v2 - CLAUDE CORE",
    version="2.0.0",
    description="Production-ready dropshipping automation via unified decision engine",
    lifespan=lifespan
)

# CORS configuration
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://dropflow.example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Content-Type", "Authorization"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "dropflow.example.com"]
)

# Global services
claude_core: Optional[ClaudeCore] = None
agent: Optional[UnifiedAgent] = None

# Metrics middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Metrics collection middleware"""
    http_active_connections.inc()
    method = request.method
    path = request.url.path
    
    try:
        response = await call_next(request)
        http_requests_total.labels(method=method, endpoint=path, status=response.status_code).inc()
        return response
    finally:
        http_active_connections.dec()

# ============ HEALTH & INFO ============

@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health/live")
async def liveness():
    """Kubernetes liveness probe"""
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness():
    """Kubernetes readiness probe - checks dependencies"""
    checks = {
        "database": "unknown",
        "redis": "unknown"
    }
    
    # Check database
    try:
        from database import engine
        with engine.connect() as conn:
            checks["database"] = "healthy"
    except Exception:
        checks["database"] = "unhealthy"
    
    # Check Redis
    try:
        import redis as redis_lib
        r = redis_lib.from_url(settings.REDIS_URL)
        r.ping()
        checks["redis"] = "healthy"
    except Exception:
        checks["redis"] = "unhealthy"
    
    all_healthy = all(v == "healthy" for v in checks.values())
    
    return JSONResponse(
        content={
            "status": "ready" if all_healthy else "not_ready",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        },
        status_code=200 if all_healthy else 503
    )

@app.get("/v1/info")
async def api_info():
    """API version and capabilities"""
    return {
        "name": "DropFlow v2 API",
        "version": API_VERSION,
        "endpoints": {
            "v1": {
                "process": "/v1/process",
                "status": "/v1/status",
                "stats": "/v1/stats",
                "stores": "/v1/stores",
                "products": "/v1/products"
            }
        },
        "features": [
            "circuit_breaker",
            "rate_limiting",
            "prometheus_metrics",
            "structured_logging"
        ]
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(custom_registry), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    """Root endpoint"""
    if not claude_core:
        return {"status": "initializing"}
    
    status = claude_core.get_system_status()
    return {
        "name": "DropFlow v2",
        "version": "2.0.0",
        "status": "ready",
        "core_status": status,
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "process": "/process (POST)",
            "stats": "/stats",
            "stores": "/stores",
            "products": "/products",
            "docs": "/docs"
        }
    }

# ============ API VERSIONING ============
# Base version info
API_VERSION = "1.0.0"

# ============ CLAUDE CORE ROUTING (v1) ============

@app.post("/v1/process")
@app.post("/process")
@limiter.limit("10/minute")
async def process_request(request: Request, request_text: str, context: Optional[dict] = None):
    """Main entry point: Route any request through CLAUDE CORE (v1)"""
    if not claude_core:
        raise HTTPException(status_code=503, detail="System initializing")
    
    try:
        logger.info(f"[PROCESS] {request_text[:100]}")
        result = claude_core.process_request(request_text, context)
        return {
            "success": True,
            "api_version": API_VERSION,
            "request": request_text,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"[PROCESS] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/status")
@app.get("/system/status")
async def get_system_status():
    """Get CLAUDE CORE system status (v1)"""
    if not claude_core:
        raise HTTPException(status_code=503, detail="System initializing")
    return {
        "api_version": API_VERSION,
        "status": claude_core.get_system_status(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/system/status")
async def get_system_status():
    """Get CLAUDE CORE system status"""
    if not claude_core:
        raise HTTPException(status_code=503, detail="System initializing")
    return {
        "status": claude_core.get_system_status(),
        "timestamp": datetime.now().isoformat()
    }

# ============ DATABASE ENDPOINTS ============

@app.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """Get platform statistics"""
    try:
        stats = DatabaseQueries.get_stats(db)
        return StatsResponse(**stats, uptime_hours=1.0, revenue_pending=0.0)
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stores")
async def get_stores(db: Session = Depends(get_db)):
    """Get all stores"""
    try:
        stores = DatabaseQueries.get_all_stores(db)
        return [
            StoreResponse(
                id=s.id,
                product_name=s.product_name,
                niche=s.niche,
                domain=s.domain,
                status=s.status.value,
                created_at=s.created_at,
                revenue=s.revenue
            )
            for s in stores
        ]
    except Exception as e:
        logger.error(f"Stores error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stores/{store_id}")
async def get_store(store_id: int, db: Session = Depends(get_db)):
    """Get specific store"""
    try:
        store = DatabaseQueries.get_store_by_id(db, store_id)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        return StoreResponse(
            id=store.id,
            product_name=store.product_name,
            niche=store.niche,
            domain=store.domain,
            status=store.status.value,
            created_at=store.created_at,
            revenue=store.revenue
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Store error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products")
async def get_products(db: Session = Depends(get_db)):
    """Get all products"""
    try:
        from models import Product
        products = db.query(Product).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "niche": p.niche,
                "searches": p.monthly_searches,
                "competition": p.competition_level,
                "margin": p.profit_margin,
                "score": p.score
            }
            for p in products
        ]
    except Exception as e:
        logger.error(f"Products error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ ERROR HANDLERS ============

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle all exceptions"""
    logger.error(f"[ERROR] {exc}")
    return {
        "success": False,
        "error": "Internal server error",
        "detail": str(exc) if settings.DEBUG else "An error occurred"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )