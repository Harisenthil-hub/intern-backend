from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app.modules.lookups import crud
from app.modules.lookups.schemas import AllLookupsOut

router = APIRouter(prefix="/lookups", tags=["Lookups"])

@router.get("", response_model=AllLookupsOut)
def get_all_lookups(db: Session = Depends(get_db)):
    """Returns all dropdown options from the database."""
    return AllLookupsOut(
        gas_types=crud.get_lookups_by_category(db, "gas_type"),
        capacity_units=crud.get_lookups_by_category(db, "capacity_unit"),
        tank_statuses=crud.get_lookups_by_category(db, "tank_status"),
        measurement_methods=crud.get_lookups_by_category(db, "measurement_method"),
        plants=crud.get_lookups_by_category(db, "plant"),
    )
