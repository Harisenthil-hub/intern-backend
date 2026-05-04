"""
Database engine, session factory, and declarative Base.
All models import Base from here and SessionLocal is injected into routes via dependency.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# ── Engine ────────────────────────────────────────────────────────────────────
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# ── Session factory ───────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ── Declarative base ──────────────────────────────────────────────────────────
Base = declarative_base()

import httpx
from app.core.config import settings

async def supabase_request(method: str, table: str, data: dict = None, filters: str = ""):
    url = f"{settings.SUPABASE_URL}/rest/v1/{table}{filters}"
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
