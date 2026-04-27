"""
SQLAlchemy ORM model for Tank Monitoring level entries.

Columns mirror the AddLevelEntryPage.jsx form:
  entryId, tankId, datetime, openingLevel, quantityAdded,
  quantityIssued, closingLevel (auto-calculated), measurementMethod, entryMode
"""

from sqlalchemy import Column, String, Float, Date, ForeignKey, Enum as SAEnum
import enum

from app.database.database import Base


class MonitoringEntryMode(str, enum.Enum):
    draft = "draft"
    posted = "post"


class MeasurementMethod(str, enum.Enum):
    manual_dip = "Manual Dip"
    sensor = "Sensor"
    flow_meter = "Flow Meter"
    visual_gauge = "Visual Gauge"


class LevelEntry(Base):
    __tablename__ = "level_entries"

    # ── Primary key ───────────────────────────────────────────────
    entry_id = Column(String(20), primary_key=True, index=True)    # e.g. ENT-3006

    # ── Foreign key ───────────────────────────────────────────────
    tank_id = Column(
        String(20),
        ForeignKey("tanks.tank_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Core fields ───────────────────────────────────────────────
    date = Column(Date, nullable=False)
    opening_level = Column(Float, nullable=False)
    quantity_added = Column(Float, nullable=False, default=0.0)
    quantity_issued = Column(Float, nullable=False, default=0.0)
    closing_level = Column(Float, nullable=False)                   # opening + added − issued

    measurement_method = Column(
        SAEnum(MeasurementMethod, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=MeasurementMethod.manual_dip.value,
    )

    # Workflow
    entry_mode = Column(
        SAEnum(MonitoringEntryMode, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=MonitoringEntryMode.draft.value,
    )
