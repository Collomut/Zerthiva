"""
Edge Node Telemetry Ingestion Endpoint
Authenticates edge devices, filters anomalies, performs cloud-side agronomic validation,
and dispatches emergency cellular SMS alerts when critical soil salinity is detected.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import verify_device_psk
from app.models.node import Node
from app.models.farm import Farm
from app.models.telemetry import Telemetry
from app.models.alert import AdvisoryAlert
from app.schemas.telemetry import TelemetryIngest
from app.services.decision_service import DecisionService
from app.services.anomaly_detector import AnomalyDetector
from app.services.sms_gateway import SMSGateway

router = APIRouter()


@router.post("/telemetry", status_code=status.HTTP_201_CREATED)
async def ingest_telemetry(
    payload: TelemetryIngest,
    db: AsyncSession = Depends(get_db),
    psk: str = Depends(verify_device_psk)
):
    """
    Ingests 15-minute telemetry from ESP32 edge node.
    """
    # 1. Anomaly & Outlier Verification
    is_valid, anomalies = AnomalyDetector.validate_reading(
        raw_ec=payload.raw_ec,
        soil_temp_c=payload.soil_temp_c,
        moisture_vwc=payload.moisture_vwc,
        battery_voltage=payload.battery_voltage or 4.0
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Sensor reading rejected due to physical anomaly", "errors": anomalies}
        )

    # 2. Check/Upsert Edge Node Record
    stmt_node = select(Node).where(Node.device_id == payload.device_id)
    res_node = await db.execute(stmt_node)
    node = res_node.scalar_one_or_none()

    if not node:
        node = Node(
            device_id=payload.device_id,
            battery_voltage=payload.battery_voltage or 4.0,
            last_seen=datetime.now(timezone.utc)
        )
        db.add(node)
        await db.flush()
    else:
        node.battery_voltage = payload.battery_voltage or 4.0
        node.last_seen = datetime.now(timezone.utc)

    # 3. Resolve Associated Farm
    farm = None
    crop = payload.crop_name or "maize"
    if node.farm_id:
        stmt_farm = select(Farm).where(Farm.id == node.farm_id)
        res_farm = await db.execute(stmt_farm)
        farm = res_farm.scalar_one_or_none()
        if farm and farm.crop_type:
            crop = farm.crop_type

    # 4. Cloud Agronomic Decision Evaluation
    eval_result = DecisionService.evaluate(
        crop_name=crop,
        raw_ec=payload.raw_ec,
        temp_c=payload.soil_temp_c,
        moisture_vwc=payload.moisture_vwc
    )

    normalized_ec = eval_result["normalized_ec_25"]
    status_str = eval_result["status"]
    action_str = eval_result["action"]
    allow_fertilizer = eval_result["allow_fertilizer"]
    leaching_fraction = eval_result["leaching_fraction"]

    # 5. Persist Telemetry Record
    telemetry_rec = Telemetry(
        device_id=payload.device_id,
        farm_id=node.farm_id,
        timestamp=datetime.now(timezone.utc),
        soil_temp_c=payload.soil_temp_c,
        raw_ec=payload.raw_ec,
        normalized_ec_25=normalized_ec,
        moisture_vwc=payload.moisture_vwc,
        battery_voltage=payload.battery_voltage or 4.0,
        status=status_str,
        action=action_str,
        allow_fertilizer=allow_fertilizer,
        leaching_fraction=leaching_fraction
    )
    db.add(telemetry_rec)
    await db.flush()

    # 6. Critical Alert Dispatch (Cellular SMS to farmer)
    sms_dispatched = False
    if status_str == "CRITICAL":
        recipient = farm.farmer_phone if farm else "+254700000000"
        sms_body = f"Zerthiva CRITICAL: High salt ({normalized_ec} dS/m) in your {crop}. Hold fertilizer! Flush root zone with {int(leaching_fraction * 100)}% extra water."

        sms_result = await SMSGateway.send_sms(recipient, sms_body)
        sms_dispatched = sms_result.get("success", False)

        alert_rec = AdvisoryAlert(
            device_id=payload.device_id,
            farm_id=node.farm_id,
            timestamp=datetime.now(timezone.utc),
            alert_level="CRITICAL",
            action=action_str,
            salinity_ec_25=normalized_ec,
            moisture_vwc=payload.moisture_vwc,
            sms_recipient=recipient,
            sms_content=sms_body,
            sms_dispatched=sms_dispatched
        )
        db.add(alert_rec)

    await db.commit()

    return {
        "status": "success",
        "telemetry_id": telemetry_rec.id,
        "device_id": payload.device_id,
        "normalized_ec_25": normalized_ec,
        "status": status_str,
        "action": action_str,
        "allow_fertilizer": allow_fertilizer,
        "sms_dispatched": sms_dispatched,
        "advisory": eval_result["advisory_message"]
    }
