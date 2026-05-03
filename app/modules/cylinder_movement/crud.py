"""
CRUD operations for Cylinder Movement entries.
"""

from sqlalchemy.orm import Session

from app.modules.cylinder_movement.models import CylinderMovement
from app.modules.cylinder_movement.schemas import CylinderMovementCreate, CylinderMovementUpdate


# ── Create ────────────────────────────────────────────────────────────────────

def create_movement(db: Session, payload: CylinderMovementCreate) -> CylinderMovement:
    entry = CylinderMovement(
        movement_id=payload.movement_id,
        date=payload.date,
        from_location=payload.from_location,
        to_location=payload.to_location,
        movement_type=payload.movement_type,
        cylinders=payload.cylinders,
        line_items=payload.line_items,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


# ── Read ──────────────────────────────────────────────────────────────────────

def get_all_movements(db: Session) -> list[CylinderMovement]:
    return (
        db.query(CylinderMovement)
        .order_by(CylinderMovement.id.desc())
        .all()
    )


def get_movement_by_id(db: Session, movement_id: int) -> CylinderMovement | None:
    return (
        db.query(CylinderMovement)
        .filter(CylinderMovement.id == movement_id)
        .first()
    )


# ── Update ────────────────────────────────────────────────────────────────────

def update_movement(
    db: Session, entry: CylinderMovement, payload: CylinderMovementUpdate
) -> CylinderMovement:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return entry
