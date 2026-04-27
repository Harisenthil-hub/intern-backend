"""
Pydantic schemas for Tank Master.

TankCreate  – payload to create / edit a tank
TankUpdate  – partial update (all fields optional)
TankOut     – response shape returned to the frontend
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


# ── Allowed choices (mirrors the frontend dropdowns) ──────────────────────────

GAS_TYPES = ["Oxygen", "Nitrogen", "LPG", "CO2", "Argon", "Hydrogen"]
CAPACITY_UNITS = ["Liters", "Kg", "m³"]
TANK_STATUSES = ["Active", "Inactive", "Maintenance"]

# ── Request schemas ───────────────────────────────────────────────────────────

class TankCreate(BaseModel):
    """Payload sent by the frontend when creating or editing a tank."""

    name: str = Field(..., min_length=1, max_length=120, description="Human-readable tank name")
    gas_type: str = Field(..., description="Type of gas stored")
    capacity_value: float = Field(..., gt=0, description="Numeric capacity")
    capacity_unit: str = Field(default="Liters", description="Unit of capacity")
    location: str = Field(..., min_length=1, max_length=150, description="Plant / zone location")

    min_level: Optional[float] = Field(default=None, ge=0)
    max_level: Optional[float] = Field(default=None, ge=0)
    calibration_ref: Optional[str] = Field(default=None, max_length=80)

    status: str = Field(default="Active")
    is_posted: int = Field(
        default=0,
        description="0 = saved; 1 = posted/locked record",
    )

    @field_validator("gas_type")
    @classmethod
    def validate_gas_type(cls, v: str) -> str:
        if v not in GAS_TYPES:
            raise ValueError(f"gas_type must be one of {GAS_TYPES}")
        return v

    @field_validator("capacity_unit")
    @classmethod
    def validate_capacity_unit(cls, v: str) -> str:
        if v not in CAPACITY_UNITS:
            raise ValueError(f"capacity_unit must be one of {CAPACITY_UNITS}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in TANK_STATUSES:
            raise ValueError(f"status must be one of {TANK_STATUSES}")
        return v


class TankUpdate(BaseModel):
    """Partial update – only changed fields are sent."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    gas_type: Optional[str] = None
    capacity_value: Optional[float] = Field(default=None, gt=0)
    capacity_unit: Optional[str] = None
    location: Optional[str] = Field(default=None, min_length=1, max_length=150)
    min_level: Optional[float] = None
    max_level: Optional[float] = None
    calibration_ref: Optional[str] = Field(default=None, max_length=80)
    status: Optional[str] = None
    is_posted: Optional[int] = None


# ── Response schema ───────────────────────────────────────────────────────────

class TankOut(BaseModel):
    """Shape returned to the frontend (maps ORM model → camelCase-friendly)."""

    tank_id: str
    name: str
    gas_type: str
    capacity_value: float
    capacity_unit: str
    capacity_display: Optional[str]
    location: str
    min_level: Optional[float]
    max_level: Optional[float]
    calibration_ref: Optional[str]
    status: str
    is_posted: int
    current_level: Optional[float]

    model_config = {"from_attributes": True}
