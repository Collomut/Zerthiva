"""
Agronomic Advisory & Leaching Calculation Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.models.alert import AdvisoryAlert
from app.schemas.advisory import AdvisoryOut, AlertOut, LeachingRequest, LeachingResponse
from app.services.decision_service import DecisionService

router = APIRouter()


@router.post("/evaluate", response_model=AdvisoryOut)
async def evaluate_soil_metrics(crop_name: str, raw_ec: float, temp_c: float, moisture_vwc: float):
    """
    Simulates or verifies FAO-56 decision evaluation for an arbitrary field vector.
    """
    res = DecisionService.evaluate(
        crop_name=crop_name,
        raw_ec=raw_ec,
        temp_c=temp_c,
        moisture_vwc=moisture_vwc
    )
    return AdvisoryOut(**res)


@router.post("/leaching", response_model=LeachingResponse)
async def calculate_leaching(payload: LeachingRequest):
    """
    Computes standard FAO-56 Leaching Requirement (LR):
    LR = ECw / (5 * ECe - ECw)
    """
    crop = DecisionService.get_crop(payload.crop_name)
    threshold_ec = crop["threshold_ec"]
    lr = DecisionService.calculate_leaching_requirement(
        ec_soil_target=threshold_ec,
        ec_water=payload.irrigation_water_ec or 0.6
    )
    return LeachingResponse(
        crop_name=crop["display_name"],
        safe_threshold_ec=threshold_ec,
        irrigation_water_ec=payload.irrigation_water_ec or 0.6,
        leaching_requirement=lr,
        extra_water_percent=int(lr * 100)
    )


@router.get("/alerts", response_model=List[AlertOut])
async def list_alerts(
    device_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """
    Query historical critical alerts and SMS dispatch records.
    """
    stmt = select(AdvisoryAlert)
    if device_id:
        stmt = stmt.where(AdvisoryAlert.device_id == device_id)
    stmt = stmt.order_by(desc(AdvisoryAlert.timestamp)).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()
