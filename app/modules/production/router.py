"""
Gas Production API router.

Base prefix : /api/v1/production
Tag         : Gas Production
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app.modules.production import crud
from app.modules.production.schemas import ProductionCreate, ProductionOut, ProductionUpdate

router = APIRouter(prefix="/production", tags=["Gas Production"])


# ── GET /production ────────────────────────────────────────────────────────────
@router.get(
    "/",
    response_model=list[ProductionOut],
    summary="List all production entries",
    description="Returns all production entries ordered by newest first.",
)
def list_production(db: Session = Depends(get_db)) -> list[ProductionOut]:
    return crud.get_all_production(db)


# ── GET /production/{production_id} ───────────────────────────────────────────
@router.get(
    "/{production_id}",
    response_model=ProductionOut,
    summary="Get a single production entry",
)
def get_production(production_id: str, db: Session = Depends(get_db)) -> ProductionOut:
    entry = crud.get_production_by_id(db, production_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Production entry '{production_id}' not found.",
        )
    return entry


# ── GET /production/by-tank/{tank_id} ─────────────────────────────────────────
@router.get(
    "/by-tank/{tank_id}",
    response_model=list[ProductionOut],
    summary="Get all production entries linked to a specific tank",
)
def get_production_by_tank(tank_id: str, db: Session = Depends(get_db)) -> list[ProductionOut]:
    return crud.get_production_by_tank(db, tank_id)


# ── POST /production ───────────────────────────────────────────────────────────
@router.post(
    "/",
    response_model=ProductionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a production entry",
    description=(
        "Records internally generated gas. "
        "Use `entry_mode='draft'` to save, `entry_mode='post'` to lock."
    ),
)
def create_production(payload: ProductionCreate, db: Session = Depends(get_db)) -> ProductionOut:
    return crud.create_production(db, payload)


# ── PUT /production/{production_id} ───────────────────────────────────────────
@router.put(
    "/{production_id}",
    response_model=ProductionOut,
    summary="Update a draft production entry",
    description="Returns 409 if the record has already been posted.",
)
def update_production(
    production_id: str,
    payload: ProductionUpdate,
    db: Session = Depends(get_db),
) -> ProductionOut:
    entry = crud.get_production_by_id(db, production_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Production entry '{production_id}' not found.")
    try:
        return crud.update_production(db, entry, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


# ── PATCH /production/{production_id}/post ─────────────────────────────────────
@router.patch(
    "/{production_id}/post",
    response_model=ProductionOut,
    summary="Post (lock) a draft production entry",
)
def post_production(production_id: str, db: Session = Depends(get_db)) -> ProductionOut:
    entry = crud.get_production_by_id(db, production_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Production entry '{production_id}' not found.")
    try:
        return crud.post_production(db, entry)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
