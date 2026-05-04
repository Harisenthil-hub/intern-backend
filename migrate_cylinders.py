import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database.database import engine

def run_migration():
    with engine.begin() as conn:
        tables = ["cylinder_filling_entries", "cylinder_movement_entries"]
        
        for table in tables:
            print(f"Migrating table: {table}")
            try:
                # Add the new column
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN is_posted INT NOT NULL DEFAULT 0;"))
                print(f"Successfully migrated {table}")
            except Exception as e:
                print(f"Skipping {table} or error occurred: {e}")

if __name__ == "__main__":
    run_migration()
