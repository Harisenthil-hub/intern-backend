"""
Loss / Leakage Monitoring API router.

Base prefix : /api/v1/loss-records
Tag         : Loss / Leakage Monitoring
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app.modules.loss_records import crud
from app.modules.loss_records.schemas import LossRecordCreate, LossRecordUpdate

router = APIRouter(prefix="/loss-records", tags=["Loss / Leakage Monitoring"])


def _first_validation_message(exc: ValidationError) -> str:
    errors = exc.errors()
    if not errors:
        return "Invalid input"

    first_error = errors[0]
    field_name = first_error.get("loc", [None])[-1]
    error_type = first_error.get("type")

    if error_type == "missing":
        if field_name == "tankId":
            return "Tank ID is required"
        if field_name == "expectedQuantity":
            return "Expected quantity is required"
        if field_name == "actualQuantity":
            return "Actual quantity is required"
        if field_name == "reason":
            return "Reason is required"
        return "Required field"

    if field_name in {"expectedQuantity", "expected_quantity"} and error_type in {
        "float_parsing",
        "float_type",
        "greater_than_equal",
        "int_parsing",
        "int_type",
    }:
        return "Invalid expected quantity"

    if field_name in {"actualQuantity", "actual_quantity"} and error_type in {
        "float_parsing",
        "float_type",
        "greater_than_equal",
        "int_parsing",
        "int_type",
    }:
        return "Invalid actual quantity"

    return first_error.get("msg", "Invalid input")


def _serialize(entry) -> dict:
    status_value = entry.status.value if hasattr(entry.status, "value") else entry.status
    reason_value = entry.reason.value if hasattr(entry.reason, "value") else entry.reason
    loss_quantity = entry.loss_quantity or 0.0
    return {
        "id": entry.record_code,
        "tankId": entry.tank_id,
        "date": entry.date.isoformat(),
        "expectedQuantity": entry.expected_quantity,
        "actualQuantity": entry.actual_quantity,
        "lossQuantity": loss_quantity,
        "reason": "" if loss_quantity == 0 else reason_value,
        "status": status_value,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
        "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_loss_record(payload: dict, db: Session = Depends(get_db)):
    try:
        parsed_payload = LossRecordCreate.model_validate(payload)
    except ValidationError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": _first_validation_message(exc)},
        )

    try:
        entry = crud.create_loss_record(db, parsed_payload)
        return {"success": True, "data": _serialize(entry)}
    except ValueError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": str(exc)},
        )


@router.get("/")
def list_loss_records(db: Session = Depends(get_db)):
    entries = crud.get_all_loss_records(db)
    return {"success": True, "data": [_serialize(entry) for entry in entries]}


@router.get("/{record_code}")
def get_loss_record(record_code: str, db: Session = Depends(get_db)):
    entry = crud.get_loss_record_by_code(db, record_code)
    if not entry:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": f"Loss record '{record_code}' not found."},
        )
    return {"success": True, "data": _serialize(entry)}


@router.put("/{record_code}")
def update_loss_record(record_code: str, payload: dict, db: Session = Depends(get_db)):
    entry = crud.get_loss_record_by_code(db, record_code)
    if not entry:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": f"Loss record '{record_code}' not found."},
        )

    try:
        parsed_payload = LossRecordUpdate.model_validate(payload)
    except ValidationError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": _first_validation_message(exc)},
        )

    try:
        updated = crud.update_loss_record(db, entry, parsed_payload)
        return {"success": True, "data": _serialize(updated)}
    except ValueError as exc:
        error_text = str(exc)
        status_code = (
            status.HTTP_409_CONFLICT
            if error_text in {"Already posted", "Posted records cannot be edited"}
            else status.HTTP_400_BAD_REQUEST
        )
        return JSONResponse(
            status_code=status_code,
            content={"success": False, "message": error_text},
        )
