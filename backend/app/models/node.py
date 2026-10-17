"""
Edge Node Entity Model
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..core.database import Base


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), unique=True, index=True, nullable=False)
    firmware_version = Column(String(20), default="1.0.0")
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    battery_voltage = Column(Float, default=4.0)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="nodes")
    telemetry = relationship("Telemetry", back_populates="node", cascade="all, delete-orphan")
