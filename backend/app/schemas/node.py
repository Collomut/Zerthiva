"""
Node Request & Response Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NodeBase(BaseModel):
    device_id: str
    firmware_version: str = "1.0.0"
    farm_id: Optional[int] = None
    is_active: bool = True


class NodeCreate(NodeBase):
    pass


class NodeOut(NodeBase):
    id: int
    battery_voltage: float
    last_seen: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
