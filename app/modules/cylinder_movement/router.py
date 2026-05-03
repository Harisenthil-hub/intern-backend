"""
Cylinder Movement API router.

Base prefix : /api/v1/cylinder-movement
Tag         : Cylinder Movement
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app.modules.cylinder_movement import crud
from app.modules.cylinder_movement.schemas import (
    CylinderMovementCreate,
    CylinderMovementOut,
    CylinderMovementUpdate,
)

router = APIRouter(prefix="/cylinder-movement", tags=["Cylinder Movement"])


# ── GET /cylinder-movement ────────────────────────────────────────────────────
@router.get(
    "/",
    response_model=list[CylinderMovementOut],
    summary="List all cylinder movement entries",
)
def list_movements(db: Session = Depends(get_db)) -> list[CylinderMovementOut]:
    return crud.get_all_movements(db)


# ── GET /cylinder-movement/{id} ───────────────────────────────────────────────
@router.get(
    "/{movement_id}",
    response_model=CylinderMovementOut,
    summary="Get a single cylinder movement entry",
)
def get_movement(movement_id: int, db: Session = Depends(get_db)) -> CylinderMovementOut:
    entry = crud.get_movement_by_id(db, movement_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cylinder movement entry '{movement_id}' not found.",
        )
    return entry


# ── POST /cylinder-movement ───────────────────────────────────────────────────
@router.post(
    "/",
    response_model=CylinderMovementOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a cylinder movement entry",
)
def create_movement(
    payload: CylinderMovementCreate, db: Session = Depends(get_db)
) -> CylinderMovementOut:
    return crud.create_movement(db, payload)


# ── PUT /cylinder-movement/{id} ───────────────────────────────────────────────
@router.put(
    "/{movement_id}",
    response_model=CylinderMovementOut,
    summary="Update an existing cylinder movement entry",
    description="Returns 404 if the record does not exist.",
)
def update_movement(
    movement_id: int,
    payload: CylinderMovementUpdate,
    db: Session = Depends(get_db),
) -> CylinderMovementOut:
    entry = crud.get_movement_by_id(db, movement_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cylinder movement entry '{movement_id}' not found.",
        )
    return crud.update_movement(db, entry, payload)
