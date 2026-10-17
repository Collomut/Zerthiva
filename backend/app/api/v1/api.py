"""
API v1 Router Aggregator
"""

from fastapi import APIRouter
from .endpoints import ingest, farms, nodes, telemetry, advisory

api_router = APIRouter()

api_router.include_router(ingest.router, prefix="/ingest", tags=["Edge Ingest"])
api_router.include_router(farms.router, prefix="/farms", tags=["Farms"])
api_router.include_router(nodes.router, prefix="/nodes", tags=["Nodes"])
api_router.include_router(telemetry.router, prefix="/telemetry", tags=["Telemetry"])
api_router.include_router(advisory.router, prefix="/advisory", tags=["Advisory"])
