"""
Pydantic schemas for Loss / Leakage Monitoring.
"""

from __future__ import annotations

from datetime import date as date_type
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


LOSS_REASON_LABEL_TO_VALUE = {
    "leakage": "leakage",
    "measurement error": "measurement_error",
    "measurement_error": "measurement_error",
    "evaporation": "evaporation",
}


def _normalize_reason(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("Reason is required")

    normalized = LOSS_REASON_LABEL_TO_VALUE.get(cleaned.lower())
    if normalized is None:
        raise ValueError("Invalid reason")
    return normalized


class LossRecordCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tank_id: str = Field(..., alias="tankId", min_length=1, max_length=20)
    date: date_type = Field(...)
    expected_quantity: float = Field(..., alias="expectedQuantity", ge=0)
    actual_quantity: float = Field(..., alias="actualQuantity", ge=0)
    reason: str = Field(default="", max_length=50)
    status: Literal["draft", "posted"] = Field(default="draft")

    @field_validator("tank_id")
    @classmethod
    def strip_tank_id(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tank ID is required")
        return cleaned

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str) -> str:
        if value is None:
            return ""
        if not value.strip():
            return ""
        return _normalize_reason(value)


class LossRecordUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tank_id: Optional[str] = Field(default=None, alias="tankId", min_length=1, max_length=20)
    date: Optional[date_type] = None
    expected_quantity: Optional[float] = Field(default=None, alias="expectedQuantity", ge=0)
    actual_quantity: Optional[float] = Field(default=None, alias="actualQuantity", ge=0)
    reason: Optional[str] = Field(default=None, max_length=50)
    status: Optional[Literal["draft", "posted"]] = None

    @field_validator("tank_id")
    @classmethod
    def strip_optional_tank_id(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tank ID is required")
        return cleaned

    @field_validator("reason")
    @classmethod
    def normalize_optional_reason(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if not value.strip():
            return ""
        return _normalize_reason(value)


class LossRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    record_code: str = Field(..., alias="id")
    tank_id: str = Field(..., alias="tankId")
    date: date_type
    expected_quantity: float = Field(..., alias="expectedQuantity")
    actual_quantity: float = Field(..., alias="actualQuantity")
    loss_quantity: float = Field(..., alias="lossQuantity")
    reason: str
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
