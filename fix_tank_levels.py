import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database.database import engine
from app.modules.tanks.models import Tank
from app.modules.monitoring.models import LevelEntry

def run_fix():
    with Session(engine) as db:
        tanks = db.query(Tank).all()
        for t in tanks:
            # Find the last posted entry for this tank
            last_posted = (
                db.query(LevelEntry)
                .filter(LevelEntry.tank_id == t.tank_id)
                .filter(LevelEntry.is_posted == 1)
                .order_by(LevelEntry.entry_id.desc())
                .first()
            )
            
            correct_level = last_posted.closing_level if last_posted else 0.0
            
            if t.current_level != correct_level:
                print(f"Fixing Tank {t.tank_id}: {t.current_level} -> {correct_level}")
                t.current_level = correct_level
        db.commit()

if __name__ == "__main__":
    run_fix()
