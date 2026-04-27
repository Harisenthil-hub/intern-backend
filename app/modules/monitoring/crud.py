"""
CRUD operations for Tank Monitoring (level entries).

After each posted entry the tank's current_level is updated automatically.
"""

from sqlalchemy.orm import Session

from app.modules.monitoring.models import LevelEntry
from app.modules.monitoring.schemas import LevelEntryCreate, LevelEntryUpdate, TankSnapshot
from app.modules.tanks.models import Tank
from app.modules.tanks import crud as tank_crud


# ── ID generation ─────────────────────────────────────────────────────────────

def _next_entry_id(db: Session) -> str:
    last = (
        db.query(LevelEntry.entry_id)
        .order_by(LevelEntry.entry_id.desc())
        .first()
    )
    if last is None:
        return "ENT-3001"
    try:
        num = int(last[0].split("-")[1]) + 1
    except (IndexError, ValueError):
        num = 3001
    return f"ENT-{num}"


# ── Create ────────────────────────────────────────────────────────────────────

def create_level_entry(db: Session, payload: LevelEntryCreate) -> LevelEntry:
    entry_id = _next_entry_id(db)

    entry = LevelEntry(
        entry_id=entry_id,
        tank_id=payload.tank_id,
        date=payload.date,
        opening_level=payload.opening_level,
        quantity_added=payload.quantity_added,
        quantity_issued=payload.quantity_issued,
        closing_level=payload.closing_level,  # already computed by validator
        measurement_method=payload.measurement_method,
        entry_mode=payload.entry_mode,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Sync tank's current_level with the new closing level
    tank_crud.update_tank_level(db, payload.tank_id, payload.closing_level)

    return entry


# ── Read ──────────────────────────────────────────────────────────────────────

def get_all_entries(db: Session) -> list[LevelEntry]:
    return db.query(LevelEntry).order_by(LevelEntry.entry_id.desc()).all()


def get_entry_by_id(db: Session, entry_id: str) -> LevelEntry | None:
    return db.query(LevelEntry).filter(LevelEntry.entry_id == entry_id).first()


def get_entries_by_tank(db: Session, tank_id: str) -> list[LevelEntry]:
    return (
        db.query(LevelEntry)
        .filter(LevelEntry.tank_id == tank_id)
        .order_by(LevelEntry.entry_id.desc())
        .all()
    )


# ── Tank snapshot list (for monitoring grid) ──────────────────────────────────

def get_tank_snapshots(db: Session) -> list[TankSnapshot]:
    """Return all tanks enriched with current fill percentage and alert flag."""
    tanks = db.query(Tank).order_by(Tank.tank_id).all()
    snapshots: list[TankSnapshot] = []
    for t in tanks:
        pct = 0.0
        if t.capacity_value and t.capacity_value > 0:
            pct = min(100.0, round((t.current_level or 0) / t.capacity_value * 100, 1))
        snapshots.append(
            TankSnapshot(
                tank_id=t.tank_id,
                name=t.name,
                gas_type=t.gas_type,
                location=t.location,
                capacity_value=t.capacity_value,
                capacity_unit=t.capacity_unit,
                current_level=t.current_level or 0,
                fill_percentage=pct,
                status=t.status,
                alert=pct < 25.0,
            )
        )
    return snapshots


# ── Update ────────────────────────────────────────────────────────────────────

def update_level_entry(db: Session, entry: LevelEntry, payload: LevelEntryUpdate) -> LevelEntry:
    if entry.entry_mode == "post":
        raise ValueError("Cannot edit a posted (locked) level entry.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)

    # Recompute closing level
    entry.closing_level = entry.opening_level + entry.quantity_added - entry.quantity_issued

    db.commit()
    db.refresh(entry)

    # Sync tank level
    tank_crud.update_tank_level(db, entry.tank_id, entry.closing_level)

    return entry


def post_level_entry(db: Session, entry: LevelEntry) -> LevelEntry:
    if entry.entry_mode == "post":
        raise ValueError("Level entry is already posted.")
    entry.entry_mode = "post"
    db.commit()
    db.refresh(entry)
    return entry
