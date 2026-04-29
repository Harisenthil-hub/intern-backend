"""
SQLAlchemy ORM models for Gas Issue to Filling.
"""

from __future__ import annotations

import enum

from sqlalchemy import Column, Date, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database.database import Base


class IssueStatus(str, enum.Enum):
    draft = "draft"
    posted = "posted"


class GasIssue(Base):
    __tablename__ = "gas_issues"

    id = Column(Integer, primary_key=True, index=True)
    issue_code = Column(String(20), nullable=False, unique=True, index=True)
    tank_id = Column(
        String(20),
        ForeignKey("tanks.tank_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    gas_type = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)
    quantity_issued = Column(Float, nullable=False)
    filling_batch_id = Column(String(80), nullable=False)
    status = Column(
        SAEnum(IssueStatus, values_callable=lambda values: [value.value for value in values]),
        nullable=False,
        default=IssueStatus.draft.value,
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    inventory_transactions = relationship(
        "InventoryTransaction",
        primaryjoin="GasIssue.id == foreign(InventoryTransaction.reference_id)",
        viewonly=True,
    )
