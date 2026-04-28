"""
Pydantic schemas for Gas Issue to Filling.
"""

from __future__ import annotations

from datetime import date as date_type
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class IssueCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tank_id: str = Field(..., alias="tankId", min_length=1, max_length=20)
    gas_type: str = Field(..., alias="gasType", min_length=1, max_length=50)
    date: date_type = Field(...)
    quantity_issued: float = Field(..., alias="quantity", gt=0)
    filling_batch_id: str = Field(..., alias="batchId", min_length=1, max_length=80)
    status: Literal["draft", "posted"] = Field(default="draft")

    @field_validator("tank_id", "gas_type", "filling_batch_id")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Required field")
        return cleaned


class IssueUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tank_id: Optional[str] = Field(default=None, alias="tankId", min_length=1, max_length=20)
    gas_type: Optional[str] = Field(default=None, alias="gasType", min_length=1, max_length=50)
    date: Optional[date_type] = None
    quantity_issued: Optional[float] = Field(default=None, alias="quantity", gt=0)
    filling_batch_id: Optional[str] = Field(default=None, alias="batchId", min_length=1, max_length=80)
    status: Optional[Literal["draft", "posted"]] = None

    @field_validator("tank_id", "gas_type", "filling_batch_id")
    @classmethod
    def strip_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Required field")
        return cleaned


class IssueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    issue_code: str = Field(..., alias="id")
    tank_id: str = Field(..., alias="tankId")
    gas_type: str = Field(..., alias="gasType")
    date: date_type
    quantity_issued: float = Field(..., alias="quantity")
    filling_batch_id: str = Field(..., alias="batchId")
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
