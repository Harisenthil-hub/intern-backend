"""
CRUD operations for Tank Master.

All database access is isolated here so routers stay thin.
"""

from sqlalchemy.orm import Session

from app.modules.tanks.models import Tank
from app.modules.tanks.schemas import TankCreate, TankUpdate


# ── ID generation ─────────────────────────────────────────────────────────────

def _next_tank_id(db: Session) -> str:
    """Generate the next sequential TK-XXXX id."""
    last = (
        db.query(Tank.tank_id)
        .order_by(Tank.tank_id.desc())
        .first()
    )
    if last is None:
        return "TK-1001"
    try:
        num = int(last[0].split("-")[1]) + 1
    except (IndexError, ValueError):
        num = 1001
    return f"TK-{num}"


# ── Create ────────────────────────────────────────────────────────────────────

def create_tank(db: Session, payload: TankCreate) -> Tank:
    """Insert a new tank record and return the ORM instance."""
    tank_id = _next_tank_id(db)
    capacity_display = f"{payload.capacity_value} {payload.capacity_unit}"

    tank = Tank(
        tank_id=tank_id,
        name=payload.name,
        gas_type=payload.gas_type,
        capacity_value=payload.capacity_value,
        capacity_unit=payload.capacity_unit,
        capacity_display=capacity_display,
        location=payload.location,
        min_level=payload.min_level,
        max_level=payload.max_level,
        calibration_ref=payload.calibration_ref,
        status=payload.status,
        entry_mode=payload.entry_mode,
        current_level=0.0,
    )
    db.add(tank)
    db.commit()
    db.refresh(tank)
    return tank


# ── Read ──────────────────────────────────────────────────────────────────────

def get_all_tanks(db: Session) -> list[Tank]:
    """Return all tanks ordered by tank_id."""
    return db.query(Tank).order_by(Tank.tank_id).all()


def get_tank_by_id(db: Session, tank_id: str) -> Tank | None:
    """Return a single tank or None."""
    return db.query(Tank).filter(Tank.tank_id == tank_id).first()


def get_active_tanks(db: Session) -> list[Tank]:
    """Return only Active tanks (used by monitoring dropdown)."""
    return db.query(Tank).filter(Tank.status == "Active").order_by(Tank.tank_id).all()


# ── Update ────────────────────────────────────────────────────────────────────

def update_tank(db: Session, tank: Tank, payload: TankUpdate) -> Tank:
    """Apply partial update to an existing tank.

    Raises ValueError if the tank is already posted (locked).
    """
    if tank.entry_mode == "post":
        raise ValueError("Cannot edit a posted (locked) tank record.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tank, field, value)

    # Recompute display string if capacity changed
    if "capacity_value" in update_data or "capacity_unit" in update_data:
        tank.capacity_display = f"{tank.capacity_value} {tank.capacity_unit}"

    db.commit()
    db.refresh(tank)
    return tank


def post_tank(db: Session, tank: Tank) -> Tank:
    """Lock a draft tank by setting entry_mode to 'post'."""
    if tank.entry_mode == "post":
        raise ValueError("Tank is already posted.")
    tank.entry_mode = "post"
    db.commit()
    db.refresh(tank)
    return tank


# ── Internal update used by monitoring ───────────────────────────────────────

def update_tank_level(db: Session, tank_id: str, new_level: float) -> None:
    """Update current_level on a tank (called by monitoring service)."""
    db.query(Tank).filter(Tank.tank_id == tank_id).update(
        {"current_level": new_level}
    )
    db.commit()
