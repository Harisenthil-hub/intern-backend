from app.database.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1')).scalar()
        print("Successfully connected! Result of SELECT 1:", result)
except Exception as e:
    print("Failed to connect:")
    print(e)
