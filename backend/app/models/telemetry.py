"""
Telemetry Time-Series Entity Model
Designed for TimescaleDB hypertable conversion or standard relational time-series.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..core.database import Base


class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), ForeignKey("nodes.device_id"), index=True, nullable=False)
    farm_id = Column(Integer, ForeignKey("farms.id"), index=True, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    soil_temp_c = Column(Float, nullable=False)
    raw_ec = Column(Float, nullable=False)
    normalized_ec_25 = Column(Float, nullable=False)
    moisture_vwc = Column(Float, nullable=False)
    battery_voltage = Column(Float, default=4.0)
    status = Column(String(20), default="OPTIMAL")
    action = Column(String(30), default="NONE")
    allow_fertilizer = Column(Boolean, default=True)
    leaching_fraction = Column(Float, default=0.0)

    node = relationship("Node", back_populates="telemetry")
    farm = relationship("Farm", back_populates="telemetry")
