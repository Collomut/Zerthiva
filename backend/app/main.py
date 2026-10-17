"""
SoilGuard Cloud Platform — FastAPI Application Entrypoint
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from .core.config import settings
from .core.database import init_db, async_session_maker
from .models.farm import Farm
from .models.node import Node
from .api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables on startup
    await init_db()

    # Seed baseline pilot farm and default node if empty
    async with async_session_maker() as db:
        res = await db.execute(select(Farm).where(Farm.id == 1))
        if not res.scalar_one_or_none():
            pilot_farm = Farm(
                id=1,
                name="Pilot Farm 1 - Central Valley",
                farmer_name="Amara Mwangi",
                farmer_phone="+254712345678",
                district="Machakos",
                crop_type="maize",
                hectares=1.5,
                latitude=-1.5177,
                longitude=37.2634
            )
            db.add(pilot_farm)
            await db.flush()

            pilot_node = Node(
                device_id="SG-NODE-001",
                firmware_version="1.0.0",
                farm_id=1,
                is_active=True,
                battery_voltage=4.05
            )
            db.add(pilot_node)
            await db.commit()

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Industrial-grade Cloud Platform & Agronomic Advisory Engine for SoilGuard (SIS)",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Route Mounts
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System"])
async def health_check():
    """Service health probe"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/", tags=["System"])
async def root():
    """Platform root information and documentation link"""
    return {
        "message": "Welcome to SoilGuard Cloud Platform API",
        "docs_url": "/docs",
        "health_check": "/health",
        "api_v1": settings.API_V1_STR
    }
