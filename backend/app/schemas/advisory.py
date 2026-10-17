"""
Agronomic Advisory & Alert Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AdvisoryOut(BaseModel):
    crop_name: str
    status: str
    action: str
    allow_fertilizer: bool
    normalized_ec_25: float
    threshold_ec: float
    leaching_fraction: float
    extra_water_percent: int
    projected_yield_loss_percent: float
    fertilizer_guidance: str
    advisory_message: str


class AlertOut(BaseModel):
    id: int
    device_id: str
    farm_id: Optional[int]
    timestamp: datetime
    alert_level: str
    action: str
    salinity_ec_25: float
    moisture_vwc: float
    sms_recipient: Optional[str]
    sms_content: str
    sms_dispatched: bool

    model_config = ConfigDict(from_attributes=True)


class LeachingRequest(BaseModel):
    crop_name: str
    soil_ec: float
    irrigation_water_ec: Optional[float] = 0.6


class LeachingResponse(BaseModel):
    crop_name: str
    safe_threshold_ec: float
    irrigation_water_ec: float
    leaching_requirement: float
    extra_water_percent: int
    formula_reference: str = "FAO-56: LR = ECw / (5 * ECe - ECw)"
