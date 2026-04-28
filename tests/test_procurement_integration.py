import os
import json
from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database.database import engine

client = TestClient(app)

# NOTE: These tests assume a test database is configured via env and available.
# They are smoke/integration tests and may modify DB state.

def test_create_and_post_procurement():
    # Create a test tank first (API generates tank_id)
    tank_payload = {
        "name": "Test Tank",
        "gas_type": "Oxygen",
        "capacity_value": 1000.0,
        "capacity_unit": "Liters",
        "location": "Test Plant",
    }
    tank_resp = client.post("/api/v1/tanks/", json=tank_payload)
    assert tank_resp.status_code == 201
    tank_data = tank_resp.json()
    # tank_data may be the TankOut object directly or wrapped by success flag depending on router
    if isinstance(tank_data, dict) and tank_data.get("tank_id") is None and tank_data.get("success"):
        created_tank = tank_data["data"]
    else:
        created_tank = tank_data
    tank_id = created_tank.get("tank_id") or created_tank.get("tankId")
    assert tank_id

    payload = {
        "vendorName": "Test Vendor",
        "date": date.today().isoformat(),
        "gasType": "Oxygen",
        "quantity": 10.0,
        "tankId": tank_id,
        "transportDetails": "Truck 1",
        "status": "draft",
    }

    # Create (draft)
    resp = client.post("/api/v1/procurements/", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    procurement_id = data["id"]

    # Post (update to posted)
    update_payload = {**payload, "status": "posted"}
    resp2 = client.put(f"/api/v1/procurements/{procurement_id}", json=update_payload)
    assert resp2.status_code == 200
    body2 = resp2.json()
    assert body2["success"] is True
    assert body2["data"]["status"] == "posted"

    # Fetch procurement
    resp3 = client.get(f"/api/v1/procurements/{procurement_id}")
    assert resp3.status_code == 200
    body3 = resp3.json()
    assert body3["success"] is True

