"""
Farm Request & Response Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class FarmBase(BaseModel):
    name: str
    farmer_name: str
    farmer_phone: str
    district: str = "Central"
    crop_type: str = "maize"
    hectares: float = 1.5
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class FarmCreate(FarmBase):
    pass


class FarmUpdate(BaseModel):
    name: Optional[str] = None
    farmer_name: Optional[str] = None
    farmer_phone: Optional[str] = None
    district: Optional[str] = None
    crop_type: Optional[str] = None
    hectares: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class FarmOut(FarmBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
