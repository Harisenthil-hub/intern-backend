"""
GasTrack Pro – FastAPI application entry point.

All module routers are registered here under the /api/v1 prefix.
CORS is configured to allow requests from the Vite dev server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.database import Base, engine

# ── Import all models so SQLAlchemy registers them before create_all ──────────
from app.modules.tanks.models import Tank                    # noqa: F401
from app.modules.production.models import Production         # noqa: F401
from app.modules.monitoring.models import LevelEntry         # noqa: F401

# ── Import routers ────────────────────────────────────────────────────────────
from app.modules.tanks.router import router as tanks_router
from app.modules.production.router import router as production_router
from app.modules.monitoring.router import router as monitoring_router
from app.modules.dashboard.router import router as dashboard_router

# ── Create all tables (dev convenience; use Alembic in production) ────────────
Base.metadata.create_all(bind=engine)

# ── Application ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "RESTful backend for GasTrack Pro – a gas inventory management system. "
        "Provides APIs for Tank Master, Gas Production, Tank Monitoring, and Dashboard."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ──────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(tanks_router,      prefix=API_PREFIX)
app.include_router(production_router, prefix=API_PREFIX)
app.include_router(monitoring_router, prefix=API_PREFIX)
app.include_router(dashboard_router,  prefix=API_PREFIX)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"], summary="Health check")
def health_check() -> dict:
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
