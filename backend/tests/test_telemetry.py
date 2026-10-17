"""
Integration tests for Telemetry querying and reporting
"""

import pytest
from app.core.config import settings


@pytest.mark.asyncio
async def test_query_telemetry_and_summary(client):
    headers = {"X-Device-PSK": settings.DEVICE_PSK}

    # Ingest 2 readings
    await client.post("/api/v1/ingest/telemetry", json={
        "device_id": "SG-NODE-001",
        "soil_temp_c": 24.0,
        "raw_ec": 1.2,
        "moisture_vwc": 28.0
    }, headers=headers)

    await client.post("/api/v1/ingest/telemetry", json={
        "device_id": "SG-NODE-001",
        "soil_temp_c": 26.0,
        "raw_ec": 1.4,
        "moisture_vwc": 31.0
    }, headers=headers)

    # Query telemetry list
    res = await client.get("/api/v1/telemetry/?device_id=SG-NODE-001")
    assert res.status_code == 200
    records = res.json()
    assert len(records) == 2
    assert records[0]["device_id"] == "SG-NODE-001"

    # Query node summary
    res_summary = await client.get("/api/v1/telemetry/summary/SG-NODE-001")
    assert res_summary.status_code == 200
    summary = res_summary.json()
    assert summary["total_records"] == 2
    assert summary["latest_moisture_vwc"] == 31.0
