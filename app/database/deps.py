"""
FastAPI dependency: yields a database session and guarantees its closure.
Usage in route:  db: Session = Depends(get_db)
"""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
