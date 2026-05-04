# app/modules/dispatch/schemas.py
from pydantic import BaseModel
from typing import List


class Cylinder(BaseModel):
    serial: str
    gasType: str
    qty: str
    unit: str


class DispatchCreate(BaseModel):
    dispatchId: str
    customerName: str
    vehicle: str
    driver: str
    route: str
    date: str
    cylinders: List[Cylinder]
    status: str  # "draft" or "posted"


class DispatchResponse(BaseModel):
    _id: str
    dispatchId: str
    customerName: str
    vehicle: str
    driver: str
    route: str
    date: str
    cylinders: List[dict]
    status: str