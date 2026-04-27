"""
Tank Monitoring API router.

Base prefix : /api/v1/monitoring
Tag         : Tank Monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app.modules.monitoring import crud
from app.modules.monitoring.schemas import (
    LevelEntryCreate,
    LevelEntryOut,
    LevelEntryUpdate,
    TankSnapshot,
)
from app.modules.tanks import crud as tank_crud

router = APIRouter(prefix="/monitoring", tags=["Tank Monitoring"])


# ── GET /monitoring/tanks ──────────────────────────────────────────────────────
@router.get(
    "/tanks",
    response_model=list[TankSnapshot],
    summary="Tank snapshot grid",
    description=(
        "Returns all tanks enriched with current level, fill percentage, and alert flag. "
        "Powers the TankCard grid in the Monitoring page."
    ),
)
def list_tank_snapshots(db: Session = Depends(get_db)) -> list[TankSnapshot]:
    return crud.get_tank_snapshots(db)


# ── GET /monitoring/entries ────────────────────────────────────────────────────
@router.get(
    "/entries",
    response_model=list[LevelEntryOut],
    summary="List all level entries",
    description="Returns all level entries ordered by newest first (Entry Log table).",
)
def list_entries(db: Session = Depends(get_db)) -> list[LevelEntryOut]:
    return crud.get_all_entries(db)


# ── GET /monitoring/entries/{entry_id} ────────────────────────────────────────
@router.get(
    "/entries/{entry_id}",
    response_model=LevelEntryOut,
    summary="Get a single level entry",
)
def get_entry(entry_id: str, db: Session = Depends(get_db)) -> LevelEntryOut:
    entry = crud.get_entry_by_id(db, entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Level entry '{entry_id}' not found.",
        )
    return entry


# ── GET /monitoring/entries/by-tank/{tank_id} ─────────────────────────────────
@router.get(
    "/entries/by-tank/{tank_id}",
    response_model=list[LevelEntryOut],
    summary="Get all level entries for a specific tank",
)
def get_entries_by_tank(tank_id: str, db: Session = Depends(get_db)) -> list[LevelEntryOut]:
    # Validate tank exists
    tank = tank_crud.get_tank_by_id(db, tank_id)
    if not tank:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tank '{tank_id}' not found.")
    return crud.get_entries_by_tank(db, tank_id)


# ── POST /monitoring/entries ───────────────────────────────────────────────────
@router.post(
    "/entries",
    response_model=LevelEntryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a level entry",
    description=(
        "Records opening level, gas added, and gas issued for a tank. "
        "Closing level is computed server-side: opening + added − issued. "
        "The tank's current_level is updated automatically."
    ),
)
def create_entry(payload: LevelEntryCreate, db: Session = Depends(get_db)) -> LevelEntryOut:
    # Validate the referenced tank exists
    tank = tank_crud.get_tank_by_id(db, payload.tank_id)
    if not tank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tank '{payload.tank_id}' not found.",
        )
    return crud.create_level_entry(db, payload)


# ── PUT /monitoring/entries/{entry_id} ────────────────────────────────────────
@router.put(
    "/entries/{entry_id}",
    response_model=LevelEntryOut,
    summary="Update a draft level entry",
    description="Returns 409 if the record has already been posted.",
)
def update_entry(
    entry_id: str,
    payload: LevelEntryUpdate,
    db: Session = Depends(get_db),
) -> LevelEntryOut:
    entry = crud.get_entry_by_id(db, entry_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Level entry '{entry_id}' not found.")
    try:
        return crud.update_level_entry(db, entry, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


# ── PATCH /monitoring/entries/{entry_id}/post ─────────────────────────────────
@router.patch(
    "/entries/{entry_id}/post",
    response_model=LevelEntryOut,
    summary="Post (lock) a draft level entry",
)
def post_entry(entry_id: str, db: Session = Depends(get_db)) -> LevelEntryOut:
    entry = crud.get_entry_by_id(db, entry_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Level entry '{entry_id}' not found.")
    try:
        return crud.post_level_entry(db, entry)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
