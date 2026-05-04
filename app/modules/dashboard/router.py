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
from sqlalchemy import func
from app.modules.cylinder_filling.models import CylinderFilling
from app.modules.cylinder_movement.models import CylinderMovement

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

# ── GET /dashboard/cylinder ───────────────────────────────────────────────────
@router.get(
    "/cylinder",
    summary="Cylinder Dashboard summary",
)
def get_cylinder_dashboard(db: Session = Depends(get_db)):
    # Compute from DB
    base_cylinders = 1500
    total_cylinders_filled = db.query(func.sum(CylinderFilling.cylinders)).scalar() or 0
    
    filled = db.query(func.sum(CylinderFilling.cylinders)).filter(CylinderFilling.is_posted == 1).scalar() or 0
    
    in_transit = db.query(func.sum(CylinderMovement.cylinders)).filter(
        CylinderMovement.movement_type == "Dispatch",
        CylinderMovement.is_posted == 1
    ).scalar() or 0

    returned = db.query(func.sum(CylinderMovement.cylinders)).filter(
        CylinderMovement.movement_type == "Return",
        CylinderMovement.is_posted == 1
    ).scalar() or 0
    
    with_customers = max(0, in_transit - returned)
    
    totalCylinders = base_cylinders + total_cylinders_filled
    empty = max(0, totalCylinders - filled - in_transit)
    underMaintenance = 60 # arbitrary default
    
    return {
        "totalCylinders": totalCylinders,
        "filled": filled,
        "empty": empty,
        "inTransit": in_transit,
        "withCustomers": with_customers,
        "underMaintenance": underMaintenance,
    }
