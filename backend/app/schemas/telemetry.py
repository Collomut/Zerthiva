"""
Telemetry Request & Response Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class TelemetryIngest(BaseModel):
    device_id: str = Field(..., json_schema_extra={"example": "SG-NODE-001"})
    timestamp: Optional[int] = None
    crop_name: Optional[str] = "maize"
    soil_temp_c: float = Field(..., json_schema_extra={"example": 24.5})
    raw_ec: float = Field(..., json_schema_extra={"example": 1.45})
    normalized_ec_25: Optional[float] = None
    moisture_vwc: float = Field(..., json_schema_extra={"example": 32.0})
    battery_voltage: Optional[float] = 4.0
    status: Optional[str] = None
    action: Optional[str] = None
    allow_fertilizer: Optional[bool] = None
    leaching_fraction: Optional[float] = None


class TelemetryOut(BaseModel):
    id: int
    device_id: str
    farm_id: Optional[int]
    timestamp: datetime
    soil_temp_c: float
    raw_ec: float
    normalized_ec_25: float
    moisture_vwc: float
    battery_voltage: float
    status: str
    action: str
    allow_fertilizer: bool
    leaching_fraction: float

    model_config = ConfigDict(from_attributes=True)


class TelemetrySummary(BaseModel):
    total_records: int
    latest_ec_25: float
    latest_moisture_vwc: float
    latest_soil_temp_c: float
    status: str
    action: str
    allow_fertilizer: bool
