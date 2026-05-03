"""
CRUD operations for Cylinder Filling entries.
"""

from sqlalchemy.orm import Session

from app.modules.cylinder_filling.models import CylinderFilling
from app.modules.cylinder_filling.schemas import CylinderFillingCreate, CylinderFillingUpdate


# ── Create ────────────────────────────────────────────────────────────────────

def create_filling(db: Session, payload: CylinderFillingCreate) -> CylinderFilling:
    entry = CylinderFilling(
        batch_id=payload.batch_id,
        date=payload.date,
        gas_type=payload.gas_type,
        tank_id=payload.tank_id,
        cylinders=payload.cylinders,
        net_weight=payload.net_weight,
        line_items=payload.line_items,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


# ── Read ──────────────────────────────────────────────────────────────────────

def get_all_fillings(db: Session) -> list[CylinderFilling]:
    return (
        db.query(CylinderFilling)
        .order_by(CylinderFilling.id.desc())
        .all()
    )


def get_filling_by_id(db: Session, filling_id: int) -> CylinderFilling | None:
    return (
        db.query(CylinderFilling)
        .filter(CylinderFilling.id == filling_id)
        .first()
    )


# ── Update ────────────────────────────────────────────────────────────────────

def update_filling(
    db: Session, entry: CylinderFilling, payload: CylinderFillingUpdate
) -> CylinderFilling:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return entry
