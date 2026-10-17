"""
Integration tests for Advisory, Leaching, and System Endpoints
"""

import pytest


@pytest.mark.asyncio
async def test_health_and_root(client):
    res_health = await client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    res_root = await client.get("/")
    assert res_root.status_code == 200
    assert "SoilGuard" in res_root.json()["message"]


@pytest.mark.asyncio
async def test_evaluate_advisory_endpoint(client):
    params = {
        "crop_name": "tomato",
        "raw_ec": 3.2,
        "temp_c": 25.0,
        "moisture_vwc": 35.0
    }
    res = await client.post("/api/v1/advisory/evaluate", params=params)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "CRITICAL"
    assert data["action"] == "FLUSH_SALTS"
    assert data["allow_fertilizer"] is False
    assert data["extra_water_percent"] > 0


@pytest.mark.asyncio
async def test_leaching_calculation_endpoint(client):
    payload = {
        "crop_name": "maize",
        "soil_ec": 2.5,
        "irrigation_water_ec": 0.6
    }
    res = await client.post("/api/v1/advisory/leaching", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["crop_name"] == "Maize"
    assert data["safe_threshold_ec"] == 1.7
    assert data["leaching_requirement"] > 0.05
    assert data["extra_water_percent"] > 5
