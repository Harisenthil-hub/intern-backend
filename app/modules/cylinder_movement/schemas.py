"""
Pydantic schemas for Cylinder Movement entries.
"""

from __future__ import annotations

from datetime import date as date_type
from typing import Any, List, Optional

from pydantic import BaseModel, Field


MOVEMENT_TYPES = ["Dispatch", "Return", "Internal"]


# ── Request schemas ───────────────────────────────────────────────────────────

class CylinderMovementCreate(BaseModel):
    movement_id: str = Field(..., min_length=1, max_length=20)
    date: date_type
    from_location: str = Field(..., min_length=1, max_length=100)
    to_location: str = Field(..., min_length=1, max_length=100)
    movement_type: str = Field(..., description=f"One of {MOVEMENT_TYPES}")
    cylinders: int = Field(..., ge=1)
    line_items: Optional[List[Any]] = None


class CylinderMovementUpdate(BaseModel):
    movement_id: Optional[str] = Field(default=None, min_length=1, max_length=20)
    date: Optional[date_type] = None
    from_location: Optional[str] = Field(default=None, min_length=1, max_length=100)
    to_location: Optional[str] = Field(default=None, min_length=1, max_length=100)
    movement_type: Optional[str] = None
    cylinders: Optional[int] = Field(default=None, ge=1)
    line_items: Optional[List[Any]] = None


# ── Response schema ───────────────────────────────────────────────────────────

class CylinderMovementOut(BaseModel):
    id: int
    movement_id: str
    date: date_type
    from_location: str
    to_location: str
    movement_type: str
    cylinders: int
    line_items: Optional[List[Any]] = None

    model_config = {"from_attributes": True}
