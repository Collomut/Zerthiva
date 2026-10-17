"""
Telemetry Query & Time-Series Reporting Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.core.database import get_db
from app.models.telemetry import Telemetry
from app.schemas.telemetry import TelemetryOut, TelemetrySummary

router = APIRouter()


@router.get("/", response_model=List[TelemetryOut])
async def query_telemetry(
    device_id: Optional[str] = None,
    farm_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns time-series telemetry records ordered by timestamp descending.
    """
    stmt = select(Telemetry)

    if device_id:
        stmt = stmt.where(Telemetry.device_id == device_id)
    if farm_id:
        stmt = stmt.where(Telemetry.farm_id == farm_id)
    if status:
        stmt = stmt.where(Telemetry.status == status.upper())

    stmt = stmt.order_by(desc(Telemetry.timestamp)).limit(limit)
    res = await db.execute(stmt)
    records = res.scalars().all()
    return records


@router.get("/summary/{device_id}", response_model=TelemetrySummary)
async def get_node_telemetry_summary(device_id: str, db: AsyncSession = Depends(get_db)):
    """
    Computes quick real-time status summary for a specific edge node.
    """
    # Total count
    count_stmt = select(func.count(Telemetry.id)).where(Telemetry.device_id == device_id)
    count_res = await db.execute(count_stmt)
    total_count = count_res.scalar_one()

    if total_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No telemetry data found for node {device_id}"
        )

    # Latest record
    latest_stmt = select(Telemetry).where(Telemetry.device_id == device_id).order_by(desc(Telemetry.timestamp)).limit(1)
    latest_res = await db.execute(latest_stmt)
    latest = latest_res.scalar_one()

    return TelemetrySummary(
        total_records=total_count,
        latest_ec_25=latest.normalized_ec_25,
        latest_moisture_vwc=latest.moisture_vwc,
        latest_soil_temp_c=latest.soil_temp_c,
        status=latest.status,
        action=latest.action,
        allow_fertilizer=latest.allow_fertilizer
    )
