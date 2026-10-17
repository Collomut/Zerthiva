"""
Integration tests for Edge Ingest endpoint
"""

import pytest
from app.core.config import settings


@pytest.mark.asyncio
async def test_ingest_unauthorized_without_psk(client):
    payload = {
        "device_id": "SG-NODE-001",
        "soil_temp_c": 24.5,
        "raw_ec": 1.2,
        "moisture_vwc": 30.0
    }
    response = await client.post("/api/v1/ingest/telemetry", json=payload)
    assert response.status_code == 401
    assert "Invalid or missing" in response.json()["detail"]


@pytest.mark.asyncio
async def test_ingest_successful_optimal_telemetry(client):
    payload = {
        "device_id": "SG-NODE-001",
        "crop_name": "maize",
        "soil_temp_c": 25.0,
        "raw_ec": 1.2,
        "moisture_vwc": 30.0,
        "battery_voltage": 4.1
    }
    headers = {"X-Device-PSK": settings.DEVICE_PSK}
    response = await client.post("/api/v1/ingest/telemetry", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "OPTIMAL"
    assert data["action"] == "NONE"
    assert data["allow_fertilizer"] is True
    assert data["sms_dispatched"] is False


@pytest.mark.asyncio
async def test_ingest_critical_salinity_triggers_sms_and_lockout(client):
    payload = {
        "device_id": "SG-NODE-001",
        "crop_name": "maize",
        "soil_temp_c": 25.0,
        "raw_ec": 2.8,  # Exceeds maize 1.7 threshold
        "moisture_vwc": 30.0,
        "battery_voltage": 3.9
    }
    headers = {"X-Device-PSK": settings.DEVICE_PSK}
    response = await client.post("/api/v1/ingest/telemetry", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "CRITICAL"
    assert data["action"] == "FLUSH_SALTS"
    assert data["allow_fertilizer"] is False
    assert data["sms_dispatched"] is True
    assert "Hold fertilizer" in data["advisory"]


@pytest.mark.asyncio
async def test_ingest_anomaly_rejection(client):
    payload = {
        "device_id": "SG-NODE-001",
        "crop_name": "maize",
        "soil_temp_c": 95.0,  # Physically impossible soil temp
        "raw_ec": 1.2,
        "moisture_vwc": 30.0
    }
    headers = {"X-Device-PSK": settings.DEVICE_PSK}
    response = await client.post("/api/v1/ingest/telemetry", json=payload, headers=headers)
    assert response.status_code == 422
    assert "Sensor reading rejected" in response.json()["detail"]["message"]
