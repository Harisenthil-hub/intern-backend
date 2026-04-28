from datetime import date

from fastapi.testclient import TestClient

from app.main import app
from app.database.database import SessionLocal
from app.modules.procurement.models import InventoryTransaction
from app.modules.tanks.models import Tank

client = TestClient(app)


def test_create_and_post_issue():
    tank_payload = {
        "name": "Issue Test Tank",
        "gas_type": "Oxygen",
        "capacity_value": 1000.0,
        "capacity_unit": "Liters",
        "location": "Issue Test Plant",
        "status": "Active",
        "is_posted": 1,
    }
    tank_resp = client.post("/api/v1/tanks/", json=tank_payload)
    assert tank_resp.status_code == 201
    tank_data = tank_resp.json()
    tank_id = tank_data["tank_id"]

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        tank.current_level = 250.0
        existing_issue_tx_count = (
            db.query(InventoryTransaction)
            .filter(InventoryTransaction.reference_type == "issue")
            .filter(InventoryTransaction.tank_id == tank_id)
            .count()
        )
        db.commit()
    finally:
        db.close()

    payload = {
        "tankId": tank_id,
        "gasType": "Oxygen",
        "date": date.today().isoformat(),
        "quantity": 25.0,
        "batchId": "FB-TEST-001",
        "status": "draft",
    }

    resp = client.post("/api/v1/issues/", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    issue_id = body["data"]["id"]
    assert body["data"]["status"] == "draft"

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        assert tank.current_level == 250.0

        issue_tx_count = (
            db.query(InventoryTransaction)
            .filter(InventoryTransaction.reference_type == "issue")
            .filter(InventoryTransaction.tank_id == tank_id)
            .count()
        )
        assert issue_tx_count == existing_issue_tx_count
    finally:
        db.close()

    update_payload = {**payload, "status": "posted"}
    resp2 = client.put(f"/api/v1/issues/{issue_id}", json=update_payload)
    assert resp2.status_code == 200
    body2 = resp2.json()
    assert body2["success"] is True
    assert body2["data"]["status"] == "posted"

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        assert tank.current_level == 225.0

        issue_tx_count = (
            db.query(InventoryTransaction)
            .filter(InventoryTransaction.reference_type == "issue")
            .filter(InventoryTransaction.tank_id == tank_id)
            .count()
        )
        assert issue_tx_count == existing_issue_tx_count + 1

        inventory_row = (
            db.query(InventoryTransaction)
            .filter(InventoryTransaction.reference_type == "issue")
            .filter(InventoryTransaction.tank_id == tank_id)
            .order_by(InventoryTransaction.id.desc())
            .first()
        )
        assert inventory_row is not None
        assert inventory_row.type == "OUT"
        assert inventory_row.quantity == 25.0
    finally:
        db.close()


def test_issue_validation_matches_frontend_rules():
    tank_payload = {
        "name": "Issue Validation Tank",
        "gas_type": "Oxygen",
        "capacity_value": 500.0,
        "capacity_unit": "Liters",
        "location": "Issue Validation Plant",
        "status": "Active",
        "is_posted": 1,
    }
    tank_resp = client.post("/api/v1/tanks/", json=tank_payload)
    assert tank_resp.status_code == 201
    tank_id = tank_resp.json()["tank_id"]

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        tank.current_level = 100.0
        db.commit()
    finally:
        db.close()

    missing_field_resp = client.post(
        "/api/v1/issues/",
        json={
            "gasType": "Oxygen",
            "date": date.today().isoformat(),
            "quantity": 10.0,
            "batchId": "FB-TEST-REQ",
        },
    )
    assert missing_field_resp.status_code == 400
    assert missing_field_resp.json() == {"success": False, "message": "Required field"}

    invalid_quantity_resp = client.post(
        "/api/v1/issues/",
        json={
            "tankId": tank_id,
            "gasType": "Oxygen",
            "date": date.today().isoformat(),
            "quantity": 0,
            "batchId": "FB-TEST-ZERO",
        },
    )
    assert invalid_quantity_resp.status_code == 400
    assert invalid_quantity_resp.json() == {"success": False, "message": "Invalid quantity"}

    over_issue_resp = client.post(
        "/api/v1/issues/",
        json={
            "tankId": tank_id,
            "gasType": "Oxygen",
            "date": date.today().isoformat(),
            "quantity": 125.0,
            "batchId": "FB-TEST-OVER",
        },
    )
    assert over_issue_resp.status_code == 400
    assert over_issue_resp.json() == {"success": False, "message": "Insufficient gas in tank"}


def test_draft_issue_can_be_edited_before_posting():
    tank_payload = {
        "name": "Issue Draft Edit Tank",
        "gas_type": "Oxygen",
        "capacity_value": 600.0,
        "capacity_unit": "Liters",
        "location": "Issue Draft Edit Plant",
        "status": "Active",
        "is_posted": 1,
    }
    tank_resp = client.post("/api/v1/tanks/", json=tank_payload)
    assert tank_resp.status_code == 201
    tank_id = tank_resp.json()["tank_id"]

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        tank.current_level = 180.0
        db.commit()
    finally:
        db.close()

    create_payload = {
        "tankId": tank_id,
        "gasType": "Oxygen",
        "date": date.today().isoformat(),
        "quantity": 20.0,
        "batchId": "FB-TEST-DRAFT",
        "status": "draft",
    }
    create_resp = client.post("/api/v1/issues/", json=create_payload)
    assert create_resp.status_code == 201
    issue_id = create_resp.json()["data"]["id"]

    update_payload = {**create_payload, "quantity": 35.0, "batchId": "FB-TEST-DRAFT-EDIT"}
    update_resp = client.put(f"/api/v1/issues/{issue_id}", json=update_payload)
    assert update_resp.status_code == 200
    body = update_resp.json()
    assert body["success"] is True
    assert body["data"]["status"] == "draft"
    assert body["data"]["quantity"] == 35.0
    assert body["data"]["batchId"] == "FB-TEST-DRAFT-EDIT"

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        assert tank.current_level == 180.0
    finally:
        db.close()


def test_issue_rejects_gas_type_mismatch():
    tank_payload = {
        "name": "Issue Gas Mismatch Tank",
        "gas_type": "Oxygen",
        "capacity_value": 400.0,
        "capacity_unit": "Liters",
        "location": "Issue Gas Mismatch Plant",
        "status": "Active",
        "is_posted": 1,
    }
    tank_resp = client.post("/api/v1/tanks/", json=tank_payload)
    assert tank_resp.status_code == 201
    tank_id = tank_resp.json()["tank_id"]

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        tank.current_level = 120.0
        db.commit()
    finally:
        db.close()

    mismatch_resp = client.post(
        "/api/v1/issues/",
        json={
            "tankId": tank_id,
            "gasType": "Nitrogen",
            "date": date.today().isoformat(),
            "quantity": 10.0,
            "batchId": "FB-TEST-MISMATCH",
            "status": "draft",
        },
    )
    assert mismatch_resp.status_code == 400
    assert mismatch_resp.json() == {
        "success": False,
        "message": "Selected tank does not match gas type",
    }


def test_posted_issue_cannot_be_edited():
    tank_payload = {
        "name": "Issue Locked Tank",
        "gas_type": "Oxygen",
        "capacity_value": 800.0,
        "capacity_unit": "Liters",
        "location": "Issue Locked Plant",
        "status": "Active",
        "is_posted": 1,
    }
    tank_resp = client.post("/api/v1/tanks/", json=tank_payload)
    assert tank_resp.status_code == 201
    tank_id = tank_resp.json()["tank_id"]

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        tank.current_level = 300.0
        db.commit()
    finally:
        db.close()

    create_payload = {
        "tankId": tank_id,
        "gasType": "Oxygen",
        "date": date.today().isoformat(),
        "quantity": 30.0,
        "batchId": "FB-TEST-LOCK",
        "status": "posted",
    }
    create_resp = client.post("/api/v1/issues/", json=create_payload)
    assert create_resp.status_code == 201
    issue_id = create_resp.json()["data"]["id"]

    update_resp = client.put(
        f"/api/v1/issues/{issue_id}",
        json={**create_payload, "quantity": 20.0},
    )
    assert update_resp.status_code == 409
    assert update_resp.json() == {
        "success": False,
        "message": "Posted records cannot be edited",
    }

    repost_resp = client.put(
        f"/api/v1/issues/{issue_id}",
        json={"status": "posted"},
    )
    assert repost_resp.status_code == 409
    assert repost_resp.json() == {"success": False, "message": "Already posted"}
