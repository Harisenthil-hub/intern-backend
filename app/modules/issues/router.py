"""
Gas Issue to Filling API router.

Base prefix : /api/v1/issues
Tag         : Gas Issue to Filling
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app.modules.issues import crud
from app.modules.issues.schemas import IssueCreate, IssueUpdate

router = APIRouter(prefix="/issues", tags=["Gas Issue to Filling"])


def _first_validation_message(exc: ValidationError) -> str:
    errors = exc.errors()
    if not errors:
        return "Invalid input"

    first_error = errors[0]
    field_name = first_error.get("loc", [None])[-1]
    error_type = first_error.get("type")

    if error_type == "missing":
        return "Required field"

    if field_name in {"quantity", "quantity_issued"} and error_type in {
        "float_parsing",
        "float_type",
        "greater_than",
        "int_parsing",
        "int_type",
    }:
        return "Invalid quantity"

    return first_error.get("msg", "Invalid input")


def _serialize(entry) -> dict:
    status_value = entry.status.value if hasattr(entry.status, "value") else entry.status
    return {
        "id": entry.issue_code,
        "tankId": entry.tank_id,
        "gasType": entry.gas_type,
        "date": entry.date.isoformat(),
        "quantity": entry.quantity_issued,
        "batchId": entry.filling_batch_id,
        "status": status_value,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
        "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_issue(payload: dict, db: Session = Depends(get_db)):
    try:
        parsed_payload = IssueCreate.model_validate(payload)
    except ValidationError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": _first_validation_message(exc)},
        )

    try:
        entry = crud.create_issue(db, parsed_payload)
        return {"success": True, "data": _serialize(entry)}
    except ValueError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": str(exc)},
        )


@router.get("/")
def list_issues(db: Session = Depends(get_db)):
    entries = crud.get_all_issues(db)
    return {"success": True, "data": [_serialize(entry) for entry in entries]}


@router.get("/{issue_code}")
def get_issue(issue_code: str, db: Session = Depends(get_db)):
    entry = crud.get_issue_by_code(db, issue_code)
    if not entry:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": f"Issue '{issue_code}' not found."},
        )
    return {"success": True, "data": _serialize(entry)}


@router.put("/{issue_code}")
def update_issue(issue_code: str, payload: dict, db: Session = Depends(get_db)):
    entry = crud.get_issue_by_code(db, issue_code)
    if not entry:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": f"Issue '{issue_code}' not found."},
        )

    try:
        parsed_payload = IssueUpdate.model_validate(payload)
    except ValidationError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": _first_validation_message(exc)},
        )

    try:
        updated = crud.update_issue(db, entry, parsed_payload)
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
