"""
CRUD operations for Gas Production entries.
"""

from datetime import date as date_type
from sqlalchemy.orm import Session

from app.modules.production.models import Production
from app.modules.production.schemas import ProductionCreate, ProductionUpdate


# ── ID generation ─────────────────────────────────────────────────────────────

def _next_production_id(db: Session) -> str:
    last = (
        db.query(Production.production_id)
        .order_by(Production.production_id.desc())
        .first()
    )
    if last is None:
        return "PROD-2001"
    try:
        num = int(last[0].split("-")[1]) + 1
    except (IndexError, ValueError):
        num = 2001
    return f"PROD-{num}"


# ── Create ────────────────────────────────────────────────────────────────────

def create_production(db: Session, payload: ProductionCreate) -> Production:
    prod_id = _next_production_id(db)
    quantity_display = f"{payload.quantity} {payload.quantity_unit}"

    entry = Production(
        production_id=prod_id,
        date=payload.date,
        plant=payload.plant,
        gas_type=payload.gas_type,
        quantity=payload.quantity,
        quantity_unit=payload.quantity_unit,
        quantity_display=quantity_display,
        batch=payload.batch,
        linked_tank_id=payload.linked_tank_id,
        entry_mode=payload.entry_mode,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


# ── Read ──────────────────────────────────────────────────────────────────────

def get_all_production(db: Session) -> list[Production]:
    return db.query(Production).order_by(Production.production_id.desc()).all()


def get_production_by_id(db: Session, production_id: str) -> Production | None:
    return db.query(Production).filter(Production.production_id == production_id).first()


def get_production_by_date(db: Session, target_date: date_type) -> list[Production]:
    """Used by dashboard to compute today's total production."""
    return db.query(Production).filter(Production.date == target_date).all()


def get_production_by_tank(db: Session, tank_id: str) -> list[Production]:
    """All production entries linked to a specific tank."""
    return (
        db.query(Production)
        .filter(Production.linked_tank_id == tank_id)
        .order_by(Production.production_id.desc())
        .all()
    )


# ── Update ────────────────────────────────────────────────────────────────────

def update_production(db: Session, entry: Production, payload: ProductionUpdate) -> Production:
    if entry.entry_mode == "post":
        raise ValueError("Cannot edit a posted (locked) production entry.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)

    if "quantity" in update_data or "quantity_unit" in update_data:
        entry.quantity_display = f"{entry.quantity} {entry.quantity_unit}"

    db.commit()
    db.refresh(entry)
    return entry


def post_production(db: Session, entry: Production) -> Production:
    if entry.entry_mode == "post":
        raise ValueError("Production entry is already posted.")
    entry.entry_mode = "post"
    db.commit()
    db.refresh(entry)
    return entry
