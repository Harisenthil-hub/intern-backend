"""
Cylinder Filling API router.

Base prefix : /api/v1/cylinder-filling
Tag         : Cylinder Filling
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app.modules.cylinder_filling import crud
from app.modules.cylinder_filling.schemas import (
    CylinderFillingCreate,
    CylinderFillingOut,
    CylinderFillingUpdate,
)

router = APIRouter(prefix="/cylinder-filling", tags=["Cylinder Filling"])


# ── GET /cylinder-filling ─────────────────────────────────────────────────────
@router.get(
    "/",
    response_model=list[CylinderFillingOut],
    summary="List all cylinder filling entries",
)
def list_fillings(db: Session = Depends(get_db)) -> list[CylinderFillingOut]:
    return crud.get_all_fillings(db)


# ── GET /cylinder-filling/{id} ────────────────────────────────────────────────
@router.get(
    "/{filling_id}",
    response_model=CylinderFillingOut,
    summary="Get a single cylinder filling entry",
)
def get_filling(filling_id: int, db: Session = Depends(get_db)) -> CylinderFillingOut:
    entry = crud.get_filling_by_id(db, filling_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cylinder filling entry '{filling_id}' not found.",
        )
    return entry


# ── POST /cylinder-filling ────────────────────────────────────────────────────
@router.post(
    "/",
    response_model=CylinderFillingOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a cylinder filling entry",
)
def create_filling(
    payload: CylinderFillingCreate, db: Session = Depends(get_db)
) -> CylinderFillingOut:
    return crud.create_filling(db, payload)


# ── PUT /cylinder-filling/{id} ────────────────────────────────────────────────
@router.put(
    "/{filling_id}",
    response_model=CylinderFillingOut,
    summary="Update an existing cylinder filling entry",
    description="Returns 404 if the record does not exist.",
)
def update_filling(
    filling_id: int,
    payload: CylinderFillingUpdate,
    db: Session = Depends(get_db),
) -> CylinderFillingOut:
    entry = crud.get_filling_by_id(db, filling_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cylinder filling entry '{filling_id}' not found.",
        )
    return crud.update_filling(db, entry, payload)
