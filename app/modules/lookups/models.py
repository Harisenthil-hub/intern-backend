from sqlalchemy import Column, Integer, String
from app.database.database import Base

class Lookup(Base):
    __tablename__ = "lookups"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False, index=True)
    value = Column(String(100), nullable=False)
