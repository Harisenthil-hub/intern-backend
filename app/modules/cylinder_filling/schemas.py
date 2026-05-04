"""
Pydantic schemas for Cylinder Filling entries.
"""

from __future__ import annotations

from datetime import date as date_type
from typing import Any, List, Optional

from pydantic import BaseModel, Field


GAS_TYPES = ["Oxygen", "Nitrogen", "Argon", "CO2"]
TANK_IDS = ["T-01", "T-02", "T-03"]


# ── Request schemas ───────────────────────────────────────────────────────────

class CylinderFillingCreate(BaseModel):
    batch_id: str = Field(..., min_length=1, max_length=20)
    date: date_type
    gas_type: str = Field(..., description=f"One of {GAS_TYPES}")
    tank_id: str = Field(..., description=f"One of {TANK_IDS}")
    cylinders: int = Field(..., ge=1)
    net_weight: float = Field(..., ge=0)
    line_items: Optional[List[Any]] = None
    is_posted: int = 0


class CylinderFillingUpdate(BaseModel):
    batch_id: Optional[str] = Field(default=None, min_length=1, max_length=20)
    date: Optional[date_type] = None
    gas_type: Optional[str] = None
    tank_id: Optional[str] = None
    cylinders: Optional[int] = Field(default=None, ge=1)
    net_weight: Optional[float] = Field(default=None, ge=0)
    line_items: Optional[List[Any]] = None
    is_posted: Optional[int] = None


# ── Response schema ───────────────────────────────────────────────────────────

class CylinderFillingOut(BaseModel):
    id: int
    batch_id: str
    date: date_type
    gas_type: str
    tank_id: str
    cylinders: int
    net_weight: float
    line_items: Optional[List[Any]] = None
    is_posted: int

    model_config = {"from_attributes": True}
