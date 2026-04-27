from sqlalchemy.orm import Session
from app.modules.lookups.models import Lookup

def get_lookups_by_category(db: Session, category: str) -> list[str]:
    records = db.query(Lookup).filter(Lookup.category == category).all()
    return [r.value for r in records]

def seed_lookups_if_empty(db: Session) -> None:
    if db.query(Lookup).first() is not None:
        return
    
    defaults = {
        "gas_type": ["Oxygen", "Nitrogen", "LPG", "CO2", "Argon", "Hydrogen"],
        "capacity_unit": ["Liters", "Kg", "m³"],
        "tank_status": ["Active", "Inactive", "Maintenance"],
        "measurement_method": ["Manual Dip", "Sensor", "Flow Meter", "Visual Gauge"],
        "plant": ["Main Plant", "North Facility", "South Hub"]
    }
    
    for cat, values in defaults.items():
        for val in values:
            db.add(Lookup(category=cat, value=val))
    db.commit()
