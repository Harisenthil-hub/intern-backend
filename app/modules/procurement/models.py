"""
SQLAlchemy ORM models for Gas Procurement and Inventory Transactions.
"""

from __future__ import annotations

import enum

from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey, Integer, Enum as SAEnum, func
from sqlalchemy.orm import relationship

from app.database.database import Base


class ProcurementStatus(str, enum.Enum):
    draft = "draft"
    posted = "posted"


class InventoryType(str, enum.Enum):
    incoming = "IN"
    outgoing = "OUT"


class ReferenceType(str, enum.Enum):
    procurement = "procurement"
    issue = "issue"


class GasProcurement(Base):
    __tablename__ = "gas_procurements"

    id = Column(Integer, primary_key=True, index=True)
    procurement_code = Column(String(20), nullable=False, unique=True, index=True)  # PR-001
    vendor_name = Column(String(150), nullable=False)
    date = Column(Date, nullable=False)
    gas_type = Column(String(50), nullable=False)
    quantity_received = Column(Float, nullable=False)

    tank_id = Column(
        String(20),
        ForeignKey("tanks.tank_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    transport_details = Column(String(255), nullable=True)
    status = Column(
        SAEnum(ProcurementStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ProcurementStatus.draft.value,
    )

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    inventory_transactions = relationship(
        "InventoryTransaction",
        primaryjoin="GasProcurement.id == foreign(InventoryTransaction.reference_id)",
        viewonly=True,
    )


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True)

    tank_id = Column(
        String(20),
        ForeignKey("tanks.tank_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    type = Column(
        SAEnum(InventoryType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=InventoryType.incoming.value,
    )

    reference_type = Column(
        SAEnum(ReferenceType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ReferenceType.procurement.value,
    )

    reference_id = Column(Integer, nullable=False, index=True)

    quantity = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
