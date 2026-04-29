"""
SQLAlchemy ORM models for Loss / Leakage Monitoring.
"""

from __future__ import annotations

import enum

from sqlalchemy import Column, Date, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database.database import Base


class LossReason(str, enum.Enum):
    leakage = "leakage"
    measurement_error = "measurement_error"
    evaporation = "evaporation"


class LossStatus(str, enum.Enum):
    draft = "draft"
    posted = "posted"


class LossRecord(Base):
    __tablename__ = "loss_records"

    id = Column(Integer, primary_key=True, index=True)
    record_code = Column(String(20), nullable=False, unique=True, index=True)
    tank_id = Column(
        String(20),
        ForeignKey("tanks.tank_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    date = Column(Date, nullable=False)
    expected_quantity = Column(Float, nullable=False)
    actual_quantity = Column(Float, nullable=False)
    loss_quantity = Column(Float, nullable=False, default=0.0)
    reason = Column(
        SAEnum(LossReason, values_callable=lambda values: [value.value for value in values]),
        nullable=False,
    )
    status = Column(
        SAEnum(LossStatus, values_callable=lambda values: [value.value for value in values]),
        nullable=False,
        default=LossStatus.draft.value,
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    inventory_transactions = relationship(
        "InventoryTransaction",
        primaryjoin="LossRecord.id == foreign(InventoryTransaction.reference_id)",
        viewonly=True,
    )
