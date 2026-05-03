"""
GasTrack Pro – FastAPI application entry point.

All module routers are registered here under the /api/v1 prefix.
CORS is configured to allow requests from the Vite dev server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.database import Base, engine, SessionLocal

# ── Import all models so SQLAlchemy registers them before create_all ──────────
from app.modules.tanks.models import Tank                    # noqa: F401
from app.modules.production.models import Production         # noqa: F401
from app.modules.monitoring.models import LevelEntry         # noqa: F401
from app.modules.lookups.models import Lookup                # noqa: F401
from app.modules.procurement.models import GasProcurement, InventoryTransaction  # noqa: F401
from app.modules.issues.models import GasIssue              # noqa: F401
from app.modules.loss_records.models import LossRecord      # noqa: F401
from app.modules.cylinder_filling.models import CylinderFilling  # noqa: F401
from app.modules.cylinder_movement.models import CylinderMovement  # noqa: F401

# ── Import routers ────────────────────────────────────────────────────────────
from app.modules.tanks.router import router as tanks_router
from app.modules.production.router import router as production_router
from app.modules.monitoring.router import router as monitoring_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.lookups.router import router as lookups_router
from app.modules.procurement.router import router as procurement_router
from app.modules.issues.router import router as issues_router
from app.modules.loss_records.router import router as loss_records_router
from app.modules.cylinder_filling.router import router as cylinder_filling_router
from app.modules.cylinder_movement.router import router as cylinder_movement_router
from app.modules.lookups.crud import seed_lookups_if_empty
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed lookups on startup
    db = SessionLocal()
    try:
        seed_lookups_if_empty(db)
    finally:
        db.close()
    yield

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
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
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
app.include_router(lookups_router,    prefix=API_PREFIX)
app.include_router(procurement_router, prefix=API_PREFIX)
app.include_router(issues_router, prefix=API_PREFIX)
app.include_router(loss_records_router, prefix=API_PREFIX)
app.include_router(cylinder_filling_router, prefix=API_PREFIX)
app.include_router(cylinder_movement_router, prefix=API_PREFIX)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"], summary="Health check")
def health_check() -> dict:
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
