"""
CRUD operations for Gas Procurement (Bulk Purchase).
"""

from __future__ import annotations

from datetime import date as date_type

from sqlalchemy.orm import Session

from app.modules.tanks.models import Tank
from app.modules.procurement.models import (
    GasProcurement,
    InventoryTransaction,
    InventoryType,
    ProcurementStatus,
    ReferenceType,
)
from app.modules.procurement.schemas import ProcurementCreate, ProcurementUpdate


def _next_procurement_code(db: Session) -> str:
    last = (
        db.query(GasProcurement.procurement_code)
        .order_by(GasProcurement.procurement_code.desc())
        .first()
    )
    if last is None:
        return "PR-001"

    try:
        num = int(last[0].split("-")[1]) + 1
    except (IndexError, ValueError):
        num = 1
    return f"PR-{num:03d}"


def _validate_frontend_rules(
    *,
    db: Session,
    gas_type: str,
    tank_id: str,
    quantity_received: float,
    doc_date: date_type,
) -> Tank:
    today = date_type.today()
    if doc_date > today:
        raise ValueError("Future dates are not allowed")

    tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
    if not tank:
        raise ValueError("Tank not found")

    if tank.gas_type != gas_type:
        raise ValueError("Selected tank does not match gas type")

    current_level = tank.current_level or 0.0
    available_space = tank.capacity_value - current_level
    if quantity_received > available_space:
        raise ValueError("Exceeds available tank capacity")

    return tank


def _post_procurement_atomic(db: Session, procurement: GasProcurement) -> GasProcurement:
    if procurement.status == ProcurementStatus.posted.value:
        raise ValueError("Already posted")

    # Step 1: fetch tank details
    tank = db.query(Tank).filter(Tank.tank_id == procurement.tank_id).first()
    if not tank:
        raise ValueError("Tank not found")

    # Step 2: validate using current snapshot
    if tank.gas_type != procurement.gas_type:
        raise ValueError("Selected tank does not match gas type")

    if (tank.current_level or 0.0) + procurement.quantity_received > tank.capacity_value:
        raise ValueError("Exceeds available tank capacity")

    try:
        # Step 3: lock tank row
        locked_tank = (
            db.query(Tank)
            .filter(Tank.tank_id == procurement.tank_id)
            .with_for_update()
            .first()
        )
        if not locked_tank:
            raise ValueError("Tank not found")

        # Re-validate after lock to prevent race conditions
        if locked_tank.gas_type != procurement.gas_type:
            raise ValueError("Selected tank does not match gas type")

        next_level = (locked_tank.current_level or 0.0) + procurement.quantity_received
        if next_level > locked_tank.capacity_value:
            raise ValueError("Exceeds available tank capacity")

        # Step 4: update tank level
        locked_tank.current_level = next_level

        # Step 5: insert inventory transaction
        inv = InventoryTransaction(
            tank_id=procurement.tank_id,
            type=InventoryType.incoming.value,
            reference_type=ReferenceType.procurement.value,
            reference_id=procurement.id,
            quantity=procurement.quantity_received,
        )
        db.add(inv)

        # Step 6: mark procurement posted
        procurement.status = ProcurementStatus.posted.value

        # Step 7: commit
        db.commit()
        db.refresh(procurement)
        return procurement
    except Exception:
        db.rollback()
        raise


def create_procurement(db: Session, payload: ProcurementCreate) -> GasProcurement:
    _validate_frontend_rules(
        db=db,
        gas_type=payload.gas_type,
        tank_id=payload.tank_id,
        quantity_received=payload.quantity_received,
        doc_date=payload.date,
    )

    should_post = payload.status == ProcurementStatus.posted.value

    procurement = GasProcurement(
        procurement_code=_next_procurement_code(db),
        vendor_name=payload.vendor_name,
        date=payload.date,
        gas_type=payload.gas_type,
        quantity_received=payload.quantity_received,
        tank_id=payload.tank_id,
        transport_details=payload.transport_details,
        status=ProcurementStatus.draft.value,
    )

    db.add(procurement)
    if should_post:
        db.flush()
        return _post_procurement_atomic(db, procurement)

    db.commit()
    db.refresh(procurement)

    return procurement


def get_all_procurements(db: Session) -> list[GasProcurement]:
    return db.query(GasProcurement).order_by(GasProcurement.procurement_code.desc()).all()


def get_procurement_by_code(db: Session, procurement_code: str) -> GasProcurement | None:
    return (
        db.query(GasProcurement)
        .filter(GasProcurement.procurement_code == procurement_code)
        .first()
    )


def update_procurement(db: Session, procurement: GasProcurement, payload: ProcurementUpdate) -> GasProcurement:
    requested_status = payload.status if payload.status is not None else procurement.status
    update_data = payload.model_dump(exclude_unset=True, by_alias=False)

    if procurement.status == ProcurementStatus.posted.value:
        if set(update_data.keys()) == {"status"} and requested_status == ProcurementStatus.posted.value:
            raise ValueError("Already posted")
        raise ValueError("Posted records cannot be edited")

    for field, value in update_data.items():
        if field == "status":
            continue
        setattr(procurement, field, value)

    _validate_frontend_rules(
        db=db,
        gas_type=procurement.gas_type,
        tank_id=procurement.tank_id,
        quantity_received=procurement.quantity_received,
        doc_date=procurement.date,
    )

    if requested_status == ProcurementStatus.posted.value:
        return _post_procurement_atomic(db, procurement)

    db.commit()
    db.refresh(procurement)

    return procurement
