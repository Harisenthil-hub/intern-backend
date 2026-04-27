"""
SQLAlchemy ORM model for the Tank Master module.

Columns mirror the fields collected in AddTankPage.jsx:
  tankId, name, gasType, capacityValue, capacityUnit, location,
  minLevel, maxLevel, calibrationRef, status, entryMode
"""

from sqlalchemy import Column, String, Float, Enum as SAEnum
import enum

from app.database.database import Base


class TankStatus(str, enum.Enum):
    active = "Active"
    inactive = "Inactive"
    maintenance = "Maintenance"


class TankEntryMode(str, enum.Enum):
    draft = "draft"
    posted = "post"


class Tank(Base):
    __tablename__ = "tanks"

    # ── Primary key ───────────────────────────────────────────────
    tank_id = Column(String(20), primary_key=True, index=True)   # e.g. TK-1006

    # ── Core fields ───────────────────────────────────────────────
    name = Column(String(120), nullable=False)
    gas_type = Column(String(50), nullable=False)                 # Oxygen | Nitrogen | LPG | CO2 | Argon | Hydrogen

    # Capacity stored as value + unit separately so we can compute later
    capacity_value = Column(Float, nullable=False)
    capacity_unit = Column(String(20), nullable=False, default="Liters")  # Liters | Kg | m³
    capacity_display = Column(String(50), nullable=True)          # "5000 Liters"

    location = Column(String(150), nullable=False)

    # Optional fields
    min_level = Column(Float, nullable=True)
    max_level = Column(Float, nullable=True)
    calibration_ref = Column(String(80), nullable=True)

    # Workflow
    status = Column(
        SAEnum(TankStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=TankStatus.active.value,
    )
    entry_mode = Column(
        SAEnum(TankEntryMode, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=TankEntryMode.draft.value,
    )

    # Current stock level (updated by monitoring entries)
    current_level = Column(Float, nullable=True, default=0.0)
