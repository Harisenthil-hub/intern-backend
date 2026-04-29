"""
Gas Procurement API router.

Base prefix : /api/v1/procurements
Tag         : Gas Procurement
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app.modules.procurement import crud
from app.modules.procurement.schemas import ProcurementCreate, ProcurementUpdate

router = APIRouter(prefix="/procurements", tags=["Gas Procurement"])


def _serialize(entry) -> dict:
    status_value = entry.status.value if hasattr(entry.status, "value") else entry.status
    return {
        "id": entry.procurement_code,
        "vendorName": entry.vendor_name,
        "date": entry.date.isoformat(),
        "gasType": entry.gas_type,
        "quantity": entry.quantity_received,
        "tankId": entry.tank_id,
        "transportDetails": entry.transport_details,
        "status": status_value,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
        "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_procurement(payload: dict, db: Session = Depends(get_db)):
    try:
        parsed_payload = ProcurementCreate.model_validate(payload)
    except ValidationError as exc:
        first_error = exc.errors()[0]["msg"] if exc.errors() else "Invalid input"
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": first_error},
        )

    try:
        entry = crud.create_procurement(db, parsed_payload)
        return {"success": True, "data": _serialize(entry)}
    except ValueError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": str(exc)},
        )


@router.get("/")
def list_procurements(db: Session = Depends(get_db)):
    entries = crud.get_all_procurements(db)
    return {"success": True, "data": [_serialize(entry) for entry in entries]}


@router.get("/{procurement_code}")
def get_procurement(procurement_code: str, db: Session = Depends(get_db)):
    entry = crud.get_procurement_by_code(db, procurement_code)
    if not entry:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": f"Procurement '{procurement_code}' not found."},
        )
    return {"success": True, "data": _serialize(entry)}


@router.put("/{procurement_code}")
def update_procurement(procurement_code: str, payload: dict, db: Session = Depends(get_db)):
    entry = crud.get_procurement_by_code(db, procurement_code)
    if not entry:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": f"Procurement '{procurement_code}' not found."},
        )

    try:
        parsed_payload = ProcurementUpdate.model_validate(payload)
    except ValidationError as exc:
        first_error = exc.errors()[0]["msg"] if exc.errors() else "Invalid input"
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": first_error},
        )

    try:
        updated = crud.update_procurement(db, entry, parsed_payload)
        return {"success": True, "data": _serialize(updated)}
    except ValueError as exc:
        error_text = str(exc)
        status_code = status.HTTP_409_CONFLICT if error_text in {"Already posted", "Posted records cannot be edited"} else status.HTTP_400_BAD_REQUEST
        return JSONResponse(
            status_code=status_code,
            content={"success": False, "message": error_text},
        )
