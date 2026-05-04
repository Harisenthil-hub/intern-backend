"""
SQLAlchemy ORM model for Cylinder Movement entries.
"""

from sqlalchemy import Column, String, Float, Date, Integer, JSON

from app.database.database import Base


class CylinderMovement(Base):
    __tablename__ = "cylinder_movement_entries"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # Header fields
    movement_id = Column(String(20), nullable=False)
    date = Column(Date, nullable=False)
    from_location = Column(String(100), nullable=False)
    to_location = Column(String(100), nullable=False)
    movement_type = Column(String(50), nullable=False)

    # Aggregate
    cylinders = Column(Integer, nullable=False, default=0)

    # Line-item detail stored as JSON blob
    line_items = Column(JSON, nullable=True)

    # 0 = Draft/Saved, 1 = Posted
    is_posted = Column(Integer, nullable=False, default=0)
