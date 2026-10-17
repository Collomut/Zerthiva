"""
Farm Entity Model
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from ..core.database import Base


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    farmer_name = Column(String(100), nullable=False)
    farmer_phone = Column(String(30), nullable=False, index=True)
    district = Column(String(100), nullable=False, default="Central")
    crop_type = Column(String(50), nullable=False, default="maize")
    hectares = Column(Float, nullable=False, default=1.5)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    nodes = relationship("Node", back_populates="farm", cascade="all, delete-orphan")
    telemetry = relationship("Telemetry", back_populates="farm", cascade="all, delete-orphan")
    alerts = relationship("AdvisoryAlert", back_populates="farm", cascade="all, delete-orphan")
