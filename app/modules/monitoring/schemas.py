"""
Pydantic schemas for Tank Monitoring (level entries).
"""

from __future__ import annotations

from datetime import date as date_type
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


MEASUREMENT_METHODS = ["Manual Dip", "Sensor", "Flow Meter", "Visual Gauge"]


# ── Request schemas ───────────────────────────────────────────────────────────

class LevelEntryCreate(BaseModel):
    """Payload from AddLevelEntryPage form."""

    tank_id: str = Field(..., max_length=20, description="FK to tanks.tank_id")
    date: date_type = Field(..., description="Date of measurement (YYYY-MM-DD)")
    opening_level: float = Field(..., ge=0, description="Level at start of period")
    quantity_added: float = Field(default=0.0, ge=0, description="Gas added to tank")
    quantity_issued: float = Field(default=0.0, ge=0, description="Gas dispensed from tank")
    measurement_method: str = Field(default="Manual Dip")
    is_posted: int = Field(default=0)

    # closing_level is computed server-side; client may send it for verification
    closing_level: Optional[float] = Field(
        default=None,
        description="Ignored if sent; always computed as opening + added − issued",
    )

    @model_validator(mode="after")
    def compute_closing_level(self) -> "LevelEntryCreate":
        self.closing_level = self.opening_level + self.quantity_added - self.quantity_issued
        return self


class LevelEntryUpdate(BaseModel):
    """Partial update for draft entries."""

    date: Optional[date_type] = None
    opening_level: Optional[float] = Field(default=None, ge=0)
    quantity_added: Optional[float] = Field(default=None, ge=0)
    quantity_issued: Optional[float] = Field(default=None, ge=0)
    measurement_method: Optional[str] = None
    is_posted: Optional[int] = None


# ── Response schema ───────────────────────────────────────────────────────────

class LevelEntryOut(BaseModel):
    entry_id: str
    tank_id: str
    date: date_type
    opening_level: float
    quantity_added: float
    quantity_issued: float
    closing_level: float
    measurement_method: str
    is_posted: int

    model_config = {"from_attributes": True}


# ── Tank snapshot (used by GET /monitoring/tanks) ─────────────────────────────

class TankSnapshot(BaseModel):
    """Summary card data for the monitoring grid view (TankCard component)."""

    tank_id: str
    name: str
    gas_type: str
    location: str
    capacity_value: float
    capacity_unit: str
    current_level: float
    fill_percentage: float             # current_level / capacity_value * 100
    status: str
    alert: bool                        # True if fill_percentage < 25

    model_config = {"from_attributes": True}
