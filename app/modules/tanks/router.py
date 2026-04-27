"""
Tank Master API router.

Base prefix : /api/v1/tanks
Tag         : Tank Master
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app.modules.tanks import crud
from app.modules.tanks.schemas import TankCreate, TankOut, TankUpdate

router = APIRouter(prefix="/tanks", tags=["Tank Master"])


# ── GET /tanks ─────────────────────────────────────────────────────────────────
@router.get(
    "/",
    response_model=list[TankOut],
    summary="List all tanks",
    description="Returns every tank registered in the system, ordered by Tank ID.",
)
def list_tanks(db: Session = Depends(get_db)) -> list[TankOut]:
    return crud.get_all_tanks(db)


# ── GET /tanks/active ──────────────────────────────────────────────────────────
@router.get(
    "/active",
    response_model=list[TankOut],
    summary="List active tanks",
    description="Returns only Active tanks. Used to populate the 'Linked Tank ID' dropdown in Production and Monitoring forms.",
)
def list_active_tanks(db: Session = Depends(get_db)) -> list[TankOut]:
    return crud.get_active_tanks(db)


# ── GET /tanks/{tank_id} ───────────────────────────────────────────────────────
@router.get(
    "/{tank_id}",
    response_model=TankOut,
    summary="Get a single tank by ID",
)
def get_tank(tank_id: str, db: Session = Depends(get_db)) -> TankOut:
    tank = crud.get_tank_by_id(db, tank_id)
    if not tank:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tank '{tank_id}' not found.")
    return tank


# ── POST /tanks ────────────────────────────────────────────────────────────────
@router.post(
    "/",
    response_model=TankOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tank",
    description=(
        "Creates a new tank record. "
        "Set `entry_mode='draft'` to save for later editing, "
        "or `entry_mode='post'` to finalise immediately."
    ),
)
def create_tank(payload: TankCreate, db: Session = Depends(get_db)) -> TankOut:
    return crud.create_tank(db, payload)


# ── PUT /tanks/{tank_id} ───────────────────────────────────────────────────────
@router.put(
    "/{tank_id}",
    response_model=TankOut,
    summary="Update a draft tank",
    description="Updates fields on a draft tank. Returns 409 if the tank has already been posted (locked).",
)
def update_tank(tank_id: str, payload: TankUpdate, db: Session = Depends(get_db)) -> TankOut:
    tank = crud.get_tank_by_id(db, tank_id)
    if not tank:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tank '{tank_id}' not found.")
    try:
        return crud.update_tank(db, tank, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


# ── PATCH /tanks/{tank_id}/post ────────────────────────────────────────────────
@router.patch(
    "/{tank_id}/post",
    response_model=TankOut,
    summary="Post (lock) a draft tank",
    description="Transitions a tank from Draft → Posted. Posted tanks cannot be edited.",
)
def post_tank(tank_id: str, db: Session = Depends(get_db)) -> TankOut:
    tank = crud.get_tank_by_id(db, tank_id)
    if not tank:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tank '{tank_id}' not found.")
    try:
        return crud.post_tank(db, tank)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
