"""
Advisory Alert & SMS Dispatch Audit Log Model
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..core.database import Base


class AdvisoryAlert(Base):
    __tablename__ = "advisory_alerts"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), nullable=False, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    alert_level = Column(String(20), nullable=False) # "CAUTION", "CRITICAL"
    action = Column(String(30), nullable=False)
    salinity_ec_25 = Column(Float, nullable=False)
    moisture_vwc = Column(Float, nullable=False)
    sms_recipient = Column(String(30), nullable=True)
    sms_content = Column(String(500), nullable=False)
    sms_dispatched = Column(Boolean, default=False)

    farm = relationship("Farm", back_populates="alerts")
