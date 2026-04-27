"""
SQLAlchemy ORM model for Gas Production entries.

Columns mirror the fields in AddProductionPage.jsx:
  productionId, date, plant, gasType, quantity, quantityUnit,
  batch, linkedTankId, entryMode
"""

from sqlalchemy import Column, String, Float, Date, ForeignKey, Enum as SAEnum, Integer
import enum

from app.database.database import Base



class Production(Base):
    __tablename__ = "production_entries"

    # ── Primary key ───────────────────────────────────────────────
    production_id = Column(String(20), primary_key=True, index=True)   # e.g. PROD-2006

    # ── Core fields ───────────────────────────────────────────────
    date = Column(Date, nullable=False)
    plant = Column(String(100), nullable=False)
    gas_type = Column(String(50), nullable=False)
    quantity = Column(Float, nullable=False)
    quantity_unit = Column(String(20), nullable=False, default="Liters")
    quantity_display = Column(String(50), nullable=True)               # "500 Liters"

    # Optional
    batch = Column(String(80), nullable=True)
    linked_tank_id = Column(
        String(20),
        ForeignKey("tanks.tank_id", ondelete="SET NULL"),
        nullable=True,
    )

    # Workflow
    is_posted = Column(Integer, nullable=False, default=0)
