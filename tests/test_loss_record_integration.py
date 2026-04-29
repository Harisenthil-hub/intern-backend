from datetime import date

from fastapi.testclient import TestClient

from app.main import app
from app.database.database import SessionLocal
from app.modules.procurement.models import InventoryTransaction
from app.modules.tanks.models import Tank

client = TestClient(app)


def _create_posted_tank(*, name: str, gas_type: str = "Oxygen", capacity_value: float = 1000.0) -> str:
    response = client.post(
        "/api/v1/tanks/",
        json={
            "name": name,
            "gas_type": gas_type,
            "capacity_value": capacity_value,
            "capacity_unit": "Liters",
            "location": f"{name} Plant",
            "status": "Active",
            "is_posted": 1,
        },
    )
    assert response.status_code == 201
    return response.json()["tank_id"]


def test_create_and_post_loss_record():
    tank_id = _create_posted_tank(name="Loss Post Tank")

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        tank.current_level = 250.0
        existing_loss_tx_count = (
            db.query(InventoryTransaction)
            .filter(InventoryTransaction.reference_type == "loss")
            .filter(InventoryTransaction.tank_id == tank_id)
            .count()
        )
        db.commit()
    finally:
        db.close()

    create_payload = {
        "tankId": tank_id,
        "date": date.today().isoformat(),
        "expectedQuantity": 100.0,
        "actualQuantity": 90.0,
        "reason": "Leakage",
        "status": "draft",
    }

    create_resp = client.post("/api/v1/loss-records/", json=create_payload)
    assert create_resp.status_code == 201
    create_body = create_resp.json()
    assert create_body["success"] is True
    assert create_body["data"]["status"] == "draft"
    assert create_body["data"]["lossQuantity"] == 10.0
    record_code = create_body["data"]["id"]

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        assert tank.current_level == 250.0
    finally:
        db.close()

    post_resp = client.put(
        f"/api/v1/loss-records/{record_code}",
        json={**create_payload, "status": "posted"},
    )
    assert post_resp.status_code == 200
    post_body = post_resp.json()
    assert post_body["success"] is True
    assert post_body["data"]["status"] == "posted"
    assert post_body["data"]["lossQuantity"] == 10.0
    assert post_body["data"]["reason"] == "leakage"

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        assert tank.current_level == 240.0

        loss_tx_count = (
            db.query(InventoryTransaction)
            .filter(InventoryTransaction.reference_type == "loss")
            .filter(InventoryTransaction.tank_id == tank_id)
            .count()
        )
        assert loss_tx_count == existing_loss_tx_count + 1

        inventory_row = (
            db.query(InventoryTransaction)
            .filter(InventoryTransaction.reference_type == "loss")
            .filter(InventoryTransaction.tank_id == tank_id)
            .order_by(InventoryTransaction.id.desc())
            .first()
        )
        assert inventory_row is not None
        assert inventory_row.type == "OUT"
        assert inventory_row.quantity == 10.0
    finally:
        db.close()


def test_loss_record_allows_zero_loss_without_inventory_adjustment():
    tank_id = _create_posted_tank(name="Loss Zero Tank", capacity_value=700.0)

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        tank.current_level = 180.0
        existing_loss_tx_count = (
            db.query(InventoryTransaction)
            .filter(InventoryTransaction.reference_type == "loss")
            .filter(InventoryTransaction.tank_id == tank_id)
            .count()
        )
        db.commit()
    finally:
        db.close()

    response = client.post(
        "/api/v1/loss-records/",
        json={
            "tankId": tank_id,
            "date": date.today().isoformat(),
            "expectedQuantity": 90.0,
            "actualQuantity": 90.0,
            "status": "posted",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "posted"
    assert body["data"]["lossQuantity"] == 0.0
    assert body["data"]["reason"] == ""

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        assert tank.current_level == 180.0

        loss_tx_count = (
            db.query(InventoryTransaction)
            .filter(InventoryTransaction.reference_type == "loss")
            .filter(InventoryTransaction.tank_id == tank_id)
            .count()
        )
        assert loss_tx_count == existing_loss_tx_count
    finally:
        db.close()


def test_loss_record_rejects_missing_fields_and_invalid_numbers():
    tank_id = _create_posted_tank(name="Loss Validation Tank")

    missing_tank_resp = client.post(
        "/api/v1/loss-records/",
        json={
            "date": date.today().isoformat(),
            "expectedQuantity": 50.0,
            "actualQuantity": 45.0,
            "reason": "Leakage",
        },
    )
    assert missing_tank_resp.status_code == 400
    assert missing_tank_resp.json() == {"success": False, "message": "Tank ID is required"}

    missing_reason_resp = client.post(
        "/api/v1/loss-records/",
        json={
            "tankId": tank_id,
            "date": date.today().isoformat(),
            "expectedQuantity": 50.0,
            "actualQuantity": 45.0,
        },
    )
    assert missing_reason_resp.status_code == 400
    assert missing_reason_resp.json() == {"success": False, "message": "Reason is required"}

    invalid_expected_resp = client.post(
        "/api/v1/loss-records/",
        json={
            "tankId": tank_id,
            "date": date.today().isoformat(),
            "expectedQuantity": -1,
            "actualQuantity": 45.0,
            "reason": "Leakage",
        },
    )
    assert invalid_expected_resp.status_code == 400
    assert invalid_expected_resp.json() == {
        "success": False,
        "message": "Invalid expected quantity",
    }

    invalid_actual_resp = client.post(
        "/api/v1/loss-records/",
        json={
            "tankId": tank_id,
            "date": date.today().isoformat(),
            "expectedQuantity": 60.0,
            "actualQuantity": -5,
            "reason": "Evaporation",
        },
    )
    assert invalid_actual_resp.status_code == 400
    assert invalid_actual_resp.json() == {
        "success": False,
        "message": "Invalid actual quantity",
    }


def test_loss_record_get_all_and_single_record():
    tank_id = _create_posted_tank(name="Loss Read Tank", capacity_value=650.0)

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        tank.current_level = 210.0
        db.commit()
    finally:
        db.close()

    create_resp = client.post(
        "/api/v1/loss-records/",
        json={
            "tankId": tank_id,
            "date": date.today().isoformat(),
            "expectedQuantity": 80.0,
            "actualQuantity": 72.0,
            "reason": "Leakage",
            "status": "draft",
        },
    )
    assert create_resp.status_code == 201
    record_code = create_resp.json()["data"]["id"]

    list_resp = client.get("/api/v1/loss-records/")
    assert list_resp.status_code == 200
    list_body = list_resp.json()
    assert list_body["success"] is True
    assert any(entry["id"] == record_code for entry in list_body["data"])

    single_resp = client.get(f"/api/v1/loss-records/{record_code}")
    assert single_resp.status_code == 200
    single_body = single_resp.json()
    assert single_body["success"] is True
    assert single_body["data"]["id"] == record_code
    assert single_body["data"]["tankId"] == tank_id


def test_loss_record_rejects_invalid_tank_and_negative_loss_on_post():
    invalid_tank_resp = client.post(
        "/api/v1/loss-records/",
        json={
            "tankId": "TK-DOES-NOT-EXIST",
            "date": date.today().isoformat(),
            "expectedQuantity": 50.0,
            "actualQuantity": 45.0,
            "reason": "Leakage",
            "status": "draft",
        },
    )
    assert invalid_tank_resp.status_code == 400
    assert invalid_tank_resp.json() == {"success": False, "message": "Tank not found"}

    tank_id = _create_posted_tank(name="Loss No Negative Tank", capacity_value=600.0)

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        tank.current_level = 150.0
        db.commit()
    finally:
        db.close()

    create_resp = client.post(
        "/api/v1/loss-records/",
        json={
            "tankId": tank_id,
            "date": date.today().isoformat(),
            "expectedQuantity": 75.0,
            "actualQuantity": 90.0,
            "reason": "Evaporation",
            "status": "posted",
        },
    )
    assert create_resp.status_code == 400
    assert create_resp.json() == {
        "success": False,
        "message": "Actual quantity cannot exceed expected quantity",
    }

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        assert tank.current_level == 150.0
    finally:
        db.close()


def test_loss_record_rejects_zero_expected_quantity():
    tank_id = _create_posted_tank(name="Loss Zero Expected Tank", capacity_value=500.0)

    response = client.post(
        "/api/v1/loss-records/",
        json={
            "tankId": tank_id,
            "date": date.today().isoformat(),
            "expectedQuantity": 0.0,
            "actualQuantity": 0.0,
            "reason": "Leakage",
            "status": "draft",
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "message": "Expected quantity must be greater than 0",
    }


def test_draft_loss_record_can_be_edited_before_posting():
    tank_id = _create_posted_tank(name="Loss Draft Tank", capacity_value=900.0)

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        tank.current_level = 300.0
        db.commit()
    finally:
        db.close()

    create_resp = client.post(
        "/api/v1/loss-records/",
        json={
            "tankId": tank_id,
            "date": date.today().isoformat(),
            "expectedQuantity": 120.0,
            "actualQuantity": 118.0,
            "reason": "Evaporation",
            "status": "draft",
        },
    )
    assert create_resp.status_code == 201
    record_code = create_resp.json()["data"]["id"]

    update_resp = client.put(
        f"/api/v1/loss-records/{record_code}",
        json={
            "tankId": tank_id,
            "date": date.today().isoformat(),
            "expectedQuantity": 120.0,
            "actualQuantity": 110.0,
            "reason": "Measurement Error",
            "status": "draft",
        },
    )
    assert update_resp.status_code == 200
    body = update_resp.json()
    assert body["success"] is True
    assert body["data"]["status"] == "draft"
    assert body["data"]["lossQuantity"] == 10.0
    assert body["data"]["reason"] == "measurement_error"

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        assert tank.current_level == 300.0
    finally:
        db.close()


def test_posted_loss_record_cannot_be_edited_or_reposted():
    tank_id = _create_posted_tank(name="Loss Locked Tank")

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        tank.current_level = 220.0
        db.commit()
    finally:
        db.close()

    create_resp = client.post(
        "/api/v1/loss-records/",
        json={
            "tankId": tank_id,
            "date": date.today().isoformat(),
            "expectedQuantity": 150.0,
            "actualQuantity": 140.0,
            "reason": "Leakage",
            "status": "posted",
        },
    )
    assert create_resp.status_code == 201
    record_code = create_resp.json()["data"]["id"]

    update_resp = client.put(
        f"/api/v1/loss-records/{record_code}",
        json={
            "tankId": tank_id,
            "date": date.today().isoformat(),
            "expectedQuantity": 150.0,
            "actualQuantity": 145.0,
            "reason": "Evaporation",
            "status": "posted",
        },
    )
    assert update_resp.status_code == 409
    assert update_resp.json() == {
        "success": False,
        "message": "Posted records cannot be edited",
    }

    repost_resp = client.put(
        f"/api/v1/loss-records/{record_code}",
        json={"status": "posted"},
    )
    assert repost_resp.status_code == 409
    assert repost_resp.json() == {"success": False, "message": "Already posted"}


def test_loss_record_rejects_when_loss_exceeds_current_level():
    tank_id = _create_posted_tank(name="Loss Exceeds Tank", capacity_value=500.0)

    db = SessionLocal()
    try:
        tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
        assert tank is not None
        tank.current_level = 5.0
        db.commit()
    finally:
        db.close()

    response = client.post(
        "/api/v1/loss-records/",
        json={
            "tankId": tank_id,
            "date": date.today().isoformat(),
            "expectedQuantity": 30.0,
            "actualQuantity": 10.0,
            "reason": "Leakage",
            "status": "posted",
        },
    )
    assert response.status_code == 400
    assert response.json() == {"success": False, "message": "Invalid loss quantity"}
