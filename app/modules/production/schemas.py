"""
Pydantic schemas for Gas Production entries.
"""

from __future__ import annotations

from datetime import date as date_type
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


GAS_TYPES = ["Oxygen", "Nitrogen", "LPG", "CO2", "Argon", "Hydrogen"]
QUANTITY_UNITS = ["Liters", "Kg", "m³"]


# ── Request schemas ───────────────────────────────────────────────────────────

class ProductionCreate(BaseModel):
    """Payload from AddProductionPage form."""

    date: date_type = Field(..., description="Production date (ISO 8601: YYYY-MM-DD)")
    plant: str = Field(..., min_length=1, max_length=100)
    gas_type: str = Field(..., description="Gas produced")
    quantity: float = Field(..., gt=0, description="Amount produced")
    quantity_unit: str = Field(default="Liters")
    batch: Optional[str] = Field(default=None, max_length=80)
    linked_tank_id: Optional[str] = Field(default=None, max_length=20, description="FK to tanks.tank_id")
    is_posted: int = Field(default=0)

    @field_validator("gas_type")
    @classmethod
    def validate_gas_type(cls, v: str) -> str:
        if v not in GAS_TYPES:
            raise ValueError(f"gas_type must be one of {GAS_TYPES}")
        return v

    @field_validator("quantity_unit")
    @classmethod
    def validate_quantity_unit(cls, v: str) -> str:
        if v not in QUANTITY_UNITS:
            raise ValueError(f"quantity_unit must be one of {QUANTITY_UNITS}")
        return v


class ProductionUpdate(BaseModel):
    """Partial update for draft records."""

    date: Optional[date_type] = None
    plant: Optional[str] = Field(default=None, min_length=1, max_length=100)
    gas_type: Optional[str] = None
    quantity: Optional[float] = Field(default=None, gt=0)
    quantity_unit: Optional[str] = None
    batch: Optional[str] = Field(default=None, max_length=80)
    linked_tank_id: Optional[str] = Field(default=None, max_length=20)
    is_posted: Optional[int] = None


# ── Response schema ───────────────────────────────────────────────────────────

class ProductionOut(BaseModel):
    production_id: str
    date: date_type
    plant: str
    gas_type: str
    quantity: float
    quantity_unit: str
    quantity_display: Optional[str]
    batch: Optional[str]
    linked_tank_id: Optional[str]
    is_posted: int

    model_config = {"from_attributes": True}
