"""
CRUD operations for Loss / Leakage Monitoring.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.loss_records.models import LossRecord, LossReason, LossStatus
from app.modules.loss_records.schemas import LossRecordCreate, LossRecordUpdate
from app.modules.procurement.models import InventoryTransaction, InventoryType, ReferenceType
from app.modules.tanks.models import Tank


def _next_record_code(db: Session) -> str:
    last = db.query(LossRecord.record_code).order_by(LossRecord.record_code.desc()).first()
    if last is None:
        return "LS-001"

    try:
        number = int(last[0].split("-")[1]) + 1
    except (IndexError, ValueError):
        number = 1
    return f"LS-{number:03d}"


def _calculate_loss_quantity(expected_quantity: float, actual_quantity: float) -> float:
    return expected_quantity - actual_quantity


def _validate_frontend_rules(
    *,
    db: Session,
    tank_id: str,
    expected_quantity: float,
    actual_quantity: float,
) -> Tank:
    tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
    if not tank:
        raise ValueError("Tank not found")

    if expected_quantity <= 0:
        raise ValueError("Expected quantity must be greater than 0")

    if actual_quantity < 0:
        raise ValueError("Actual quantity cannot be negative")

    if actual_quantity > expected_quantity:
        raise ValueError("Actual quantity cannot exceed expected quantity")

    return tank


def _post_loss_record_atomic(db: Session, record: LossRecord) -> LossRecord:
    if record.status == LossStatus.posted.value:
        raise ValueError("Already posted")

    tank = db.query(Tank).filter(Tank.tank_id == record.tank_id).first()
    if not tank:
        raise ValueError("Tank not found")

    loss_quantity = _calculate_loss_quantity(record.expected_quantity, record.actual_quantity)
    current_level = tank.current_level or 0.0
    if loss_quantity < 0:
        raise ValueError("Actual quantity cannot exceed expected quantity")
    if loss_quantity > current_level:
        raise ValueError("Invalid loss quantity")

    try:
        locked_tank = (
            db.query(Tank)
            .filter(Tank.tank_id == record.tank_id)
            .with_for_update()
            .first()
        )
        if not locked_tank:
            raise ValueError("Tank not found")

        loss_quantity = _calculate_loss_quantity(record.expected_quantity, record.actual_quantity)
        current_level = locked_tank.current_level or 0.0
        if loss_quantity < 0:
            raise ValueError("Actual quantity cannot exceed expected quantity")
        if loss_quantity > current_level:
            raise ValueError("Invalid loss quantity")

        record.loss_quantity = loss_quantity

        if loss_quantity > 0:
            locked_tank.current_level = current_level - loss_quantity
            inventory_transaction = InventoryTransaction(
                tank_id=record.tank_id,
                type=InventoryType.outgoing.value,
                reference_type=ReferenceType.loss.value,
                reference_id=record.id,
                quantity=loss_quantity,
            )
            db.add(inventory_transaction)

        record.status = LossStatus.posted.value

        db.commit()
        db.refresh(record)
        return record
    except Exception:
        db.rollback()
        raise


def create_loss_record(db: Session, payload: LossRecordCreate) -> LossRecord:
    _validate_frontend_rules(
        db=db,
        tank_id=payload.tank_id,
        expected_quantity=payload.expected_quantity,
        actual_quantity=payload.actual_quantity,
    )

    should_post = payload.status == LossStatus.posted.value
    loss_quantity = _calculate_loss_quantity(payload.expected_quantity, payload.actual_quantity)

    if loss_quantity < 0:
        raise ValueError("Actual quantity cannot exceed expected quantity")
    if loss_quantity > 0 and not payload.reason:
        raise ValueError("Reason is required")

    persisted_reason = payload.reason or LossReason.leakage.value

    record = LossRecord(
        record_code=_next_record_code(db),
        tank_id=payload.tank_id,
        date=payload.date,
        expected_quantity=payload.expected_quantity,
        actual_quantity=payload.actual_quantity,
        loss_quantity=loss_quantity,
        reason=persisted_reason,
        status=LossStatus.draft.value,
    )

    db.add(record)
    if should_post:
        db.flush()
        return _post_loss_record_atomic(db, record)

    db.commit()
    db.refresh(record)
    return record


def get_all_loss_records(db: Session) -> list[LossRecord]:
    return db.query(LossRecord).order_by(LossRecord.record_code.desc()).all()


def get_loss_record_by_code(db: Session, record_code: str) -> LossRecord | None:
    return db.query(LossRecord).filter(LossRecord.record_code == record_code).first()


def update_loss_record(db: Session, record: LossRecord, payload: LossRecordUpdate) -> LossRecord:
    requested_status = payload.status if payload.status is not None else record.status
    update_data = payload.model_dump(exclude_unset=True, by_alias=False)

    if record.status == LossStatus.posted.value:
        if set(update_data.keys()) == {"status"} and requested_status == LossStatus.posted.value:
            raise ValueError("Already posted")
        raise ValueError("Posted records cannot be edited")

    for field, value in update_data.items():
        if field == "status":
            continue
        setattr(record, field, value)

    _validate_frontend_rules(
        db=db,
        tank_id=record.tank_id,
        expected_quantity=record.expected_quantity,
        actual_quantity=record.actual_quantity,
    )
    record.loss_quantity = _calculate_loss_quantity(record.expected_quantity, record.actual_quantity)

    if record.loss_quantity < 0:
        raise ValueError("Actual quantity cannot exceed expected quantity")
    if record.loss_quantity > 0 and not record.reason:
        raise ValueError("Reason is required")
    if record.loss_quantity == 0 and not record.reason:
        record.reason = LossReason.leakage.value

    if requested_status == LossStatus.posted.value:
        return _post_loss_record_atomic(db, record)

    db.commit()
    db.refresh(record)
    return record
