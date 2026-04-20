"""
DropFlow v2 - FastAPI Application
Unified via CLAUDE CORE decision engine
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path
import logging
import asyncio
import json
from enum import Enum
from typing import List, Optional

from config import settings
from database import get_db, init_db, DatabaseQueries
from models import (
    StoreResponse, StatsResponse, ScenarioResponse,
    CreateStoreRequest, ProductResponse
)
import stripe
import time

# CLAUDE CORE - Central decision engine
import sys
sys.path.insert(0, str(Path(__file__).parent))
from claude_core import ClaudeCore, ProjectType, RequestType
from agents import UnifiedAgent
from projects import PROJECTS

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="DropFlow v2 - CLAUDE CORE",
    version="2.0.0",
    description="Production-ready dropshipping automation via unified decision engine"
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
claude_core: ClaudeCore = None
agent: UnifiedAgent = None


@app.on_event("startup")
async def startup():
    """Initialize CLAUDE CORE and all projects"""
    global claude_core, agent

    logger.info("[STARTUP] DropFlow v2 CLAUDE CORE starting...")

    # Initialize database
    init_db()
    logger.info("[OK] Database initialized")

    # Initialize CLAUDE CORE
    claude_core = ClaudeCore()
    logger.info("[OK] CLAUDE CORE initialized")

    # Initialize unified agent
    agent = UnifiedAgent(agent_type="GENERIC")
    logger.info("[OK] Unified Agent initialized")

    # Register all project orchestrators
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
            logger.info(f"[OK] Project {project_id} registered")

    logger.info("[STARTUP] DropFlow v2 CLAUDE CORE - READY!")


# ============ HEALTH & INFO ============

@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "core": "CLAUDE CORE"
    }


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
            "process": "/process (POST)",
            "stats": "/stats",
            "stores": "/stores",
            "products": "/products",
            "docs": "/docs"
        }
    }


# ============ CLAUDE CORE ROUTING ============

@app.post("/process")
@limiter.limit("10/minute")
async def process_request(request_text: str, context: Optional[dict] = None):
    """
    Main entry point: Route any request through CLAUDE CORE
    CLAUDE CORE will parse, classify, and route to appropriate handler
    """
    if not claude_core:
        raise HTTPException(status_code=503, detail="System initializing")

    try:
        logger.info(f"[PROCESS] {request_text[:100]}")
        result = claude_core.process_request(request_text, context)

        return {
            "success": True,
            "request": request_text,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"[PROCESS] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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
