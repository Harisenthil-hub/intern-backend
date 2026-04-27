"""
Dashboard aggregation service.

Queries all three domain tables (tanks, production_entries, level_entries)
and builds the DashboardOut response in a single call.
"""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.modules.tanks.models import Tank
from app.modules.production.models import Production
from app.modules.monitoring.models import LevelEntry
from app.modules.dashboard.schemas import (
    ActivityItem,
    DashboardOut,
    DashboardStats,
)


# ── Helper ────────────────────────────────────────────────────────────────────

def _human_time(d: date) -> str:
    """Convert a date to a display string like 'Today, 09:00 AM' or '26 Apr 2025'."""
    today = date.today()
    if d == today:
        return "Today"
    yesterday = date(today.year, today.month, today.day - 1)
    if d == yesterday:
        return "Yesterday"
    return d.strftime("%d %b %Y")


# ── Main service function ─────────────────────────────────────────────────────

def build_dashboard(db: Session, activity_limit: int = 10) -> DashboardOut:
    """Aggregate stats and recent activity from the database."""

    today = date.today()

    # ── Tank stats ────────────────────────────────────────────────
    all_tanks: list[Tank] = db.query(Tank).all()
    total_tanks = len(all_tanks)
    active_tanks = sum(1 for t in all_tanks if t.status == "Active")
    inactive_tanks = sum(1 for t in all_tanks if t.status == "Inactive")
    maintenance_tanks = sum(1 for t in all_tanks if t.status == "Maintenance")

    low_level_alerts = sum(
        1 for t in all_tanks
        if t.capacity_value and t.capacity_value > 0
        and ((t.current_level or 0) / t.capacity_value) < 0.25
    )

    # ── Today's production ────────────────────────────────────────
    today_entries: list[Production] = (
        db.query(Production)
        .filter(Production.date == today)
        .all()
    )
    today_production_total = sum(e.quantity for e in today_entries)
    today_production_entries = len(today_entries)

    # Dominant unit
    unit_counts = Counter(e.quantity_unit for e in today_entries)
    today_production_unit = unit_counts.most_common(1)[0][0] if unit_counts else "Liters"

    stats = DashboardStats(
        total_tanks=total_tanks,
        active_tanks=active_tanks,
        inactive_tanks=inactive_tanks,
        maintenance_tanks=maintenance_tanks,
        low_level_alerts=low_level_alerts,
        today_production_total=today_production_total,
        today_production_unit=today_production_unit,
        today_production_entries=today_production_entries,
    )

    # ── Recent activity feed ──────────────────────────────────────
    activity: list[ActivityItem] = []

    # Latest production entries
    recent_prod: list[Production] = (
        db.query(Production)
        .order_by(Production.production_id.desc())
        .limit(activity_limit)
        .all()
    )
    for p in recent_prod:
        activity.append(
            ActivityItem(
                type="Production",
                detail=f"{p.gas_type} — {p.quantity_display or f'{p.quantity} {p.quantity_unit}'}",
                tank=p.linked_tank_id,
                time=_human_time(p.date),
                status="Posted" if p.entry_mode == "post" else "Draft",
                reference_id=p.production_id,
            )
        )

    # Latest level entries
    recent_entries: list[LevelEntry] = (
        db.query(LevelEntry)
        .order_by(LevelEntry.entry_id.desc())
        .limit(activity_limit)
        .all()
    )
    for e in recent_entries:
        activity.append(
            ActivityItem(
                type="Level Entry",
                detail=f"Closing: {e.closing_level} L",
                tank=e.tank_id,
                time=_human_time(e.date),
                status="Posted" if e.entry_mode == "post" else "Draft",
                reference_id=e.entry_id,
            )
        )

    # Low-level alert items
    low_tanks = [
        t for t in all_tanks
        if t.capacity_value and t.capacity_value > 0
        and ((t.current_level or 0) / t.capacity_value) < 0.25
    ]
    for t in low_tanks:
        activity.append(
            ActivityItem(
                type="Alert",
                detail=f"{t.name} below minimum level",
                tank=t.tank_id,
                time="Now",
                status="Warning",
                reference_id=t.tank_id,
            )
        )

    # Sort combined feed: alerts first, then by reference_id descending (newest)
    activity.sort(key=lambda x: (x.status != "Warning", x.reference_id), reverse=True)

    return DashboardOut(
        stats=stats,
        recent_activity=activity[:activity_limit],
    )
