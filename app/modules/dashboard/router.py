"""
Dashboard API router.

Base prefix : /api/v1/dashboard
Tag         : Dashboard
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app.modules.dashboard.schemas import DashboardOut
from app.modules.dashboard.service import build_dashboard

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# ── GET /dashboard ─────────────────────────────────────────────────────────────
@router.get(
    "/",
    response_model=DashboardOut,
    summary="Dashboard summary",
    description=(
        "Aggregates stats (total/active tanks, today's production, low-level alerts) "
        "and returns the most recent activity feed across all modules."
    ),
)
def get_dashboard(
    activity_limit: int = Query(default=10, ge=1, le=50, description="Max number of recent activity items"),
    db: Session = Depends(get_db),
) -> DashboardOut:
    return build_dashboard(db, activity_limit=activity_limit)
