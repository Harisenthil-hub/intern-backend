# app/modules/cylinder/schemas.py
from pydantic import BaseModel
from typing import Optional


class TrackerCreate(BaseModel):
    serial: str
    location: str
    cylinderStatus: str
    status: str
    date: Optional[str] = None