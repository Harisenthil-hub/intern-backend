"""
Pydantic schemas for Gas Procurement.
"""

from __future__ import annotations

from datetime import date as date_type
from typing import Optional, Literal

from pydantic import BaseModel, Field, ConfigDict, field_validator


class ProcurementCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    vendor_name: str = Field(..., alias="vendorName", min_length=1, max_length=150)
    date: date_type = Field(...)
    gas_type: str = Field(..., alias="gasType", min_length=1, max_length=50)
    quantity_received: float = Field(..., alias="quantity", gt=0)
    tank_id: str = Field(..., alias="tankId", min_length=1, max_length=20)
    transport_details: Optional[str] = Field(default=None, alias="transportDetails", max_length=255)
    status: Literal["draft", "posted"] = Field(default="draft")

    @field_validator("vendor_name", "gas_type", "tank_id")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("This field is required")
        return cleaned

    @field_validator("transport_details")
    @classmethod
    def strip_transport_details(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class ProcurementUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    vendor_name: Optional[str] = Field(default=None, alias="vendorName", min_length=1, max_length=150)
    date: Optional[date_type] = None
    gas_type: Optional[str] = Field(default=None, alias="gasType", min_length=1, max_length=50)
    quantity_received: Optional[float] = Field(default=None, alias="quantity", gt=0)
    tank_id: Optional[str] = Field(default=None, alias="tankId", min_length=1, max_length=20)
    transport_details: Optional[str] = Field(default=None, alias="transportDetails", max_length=255)
    status: Optional[Literal["draft", "posted"]] = None

    @field_validator("vendor_name", "gas_type", "tank_id")
    @classmethod
    def strip_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("This field is required")
        return cleaned

    @field_validator("transport_details")
    @classmethod
    def strip_optional_transport(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class ProcurementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    procurement_code: str = Field(..., alias="id")
    vendor_name: str = Field(..., alias="vendorName")
    date: date_type
    gas_type: str = Field(..., alias="gasType")
    quantity_received: float = Field(..., alias="quantity")
    tank_id: str = Field(..., alias="tankId")
    transport_details: Optional[str] = Field(default=None, alias="transportDetails")
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ApiSuccess(BaseModel):
    success: bool = True
    data: object


class ApiError(BaseModel):
    success: bool = False
    message: str
