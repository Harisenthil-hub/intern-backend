"""
SQLAlchemy ORM model for Cylinder Filling entries.
"""

from sqlalchemy import Column, String, Float, Date, Integer, JSON

from app.database.database import Base


class CylinderFilling(Base):
    __tablename__ = "cylinder_filling_entries"

    # Primary key (auto-incremented integer, exposed as str to frontend)
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # Header fields
    batch_id = Column(String(20), nullable=False)
    date = Column(Date, nullable=False)
    gas_type = Column(String(50), nullable=False)
    tank_id = Column(String(20), nullable=False)

    # Aggregates
    cylinders = Column(Integer, nullable=False, default=0)
    net_weight = Column(Float, nullable=False, default=0.0)

    # Line-item detail stored as JSON blob
    line_items = Column(JSON, nullable=True)

    # 0 = Draft/Saved, 1 = Posted
    is_posted = Column(Integer, nullable=False, default=0)
