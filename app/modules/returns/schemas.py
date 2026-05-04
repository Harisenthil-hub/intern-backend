# app/modules/returns/schemas.py
from pydantic import BaseModel
from typing import List


class ReturnCylinder(BaseModel):
    serial: str
    condition: str


class ReturnCreate(BaseModel):
    returnId: str
    customerName: str
    date: str
    cylinders: List[ReturnCylinder]
    status: str  # "draft" or "posted"