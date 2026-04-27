"""
Pydantic schemas for the Dashboard API.

Mirrors the static data shapes in Dashboard.jsx:
  - Summary stats cards (total tanks, active, today's production, low alerts)
  - Recent activity feed (last N events across all modules)
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


# ── Stats card ────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_tanks: int
    active_tanks: int
    inactive_tanks: int
    maintenance_tanks: int
    low_level_alerts: int                  # tanks with fill % < 25
    today_production_total: float          # sum of today's posted quantities
    today_production_unit: str             # dominant unit (Liters / Kg / m³)
    today_production_entries: int          # count of today's entries


# ── Activity item ─────────────────────────────────────────────────────────────

ActivityType = Literal["Production", "Level Entry", "Tank Added", "Alert"]
ActivityStatus = Literal["Posted", "Draft", "Active", "Warning"]


class ActivityItem(BaseModel):
    type: ActivityType
    detail: str
    tank: Optional[str]
    time: str                             # human-readable e.g. "Today, 09:15 AM"
    status: ActivityStatus
    reference_id: str                     # PROD-xxxx | ENT-xxxx | TK-xxxx


# ── Dashboard response ────────────────────────────────────────────────────────

class DashboardOut(BaseModel):
    stats: DashboardStats
    recent_activity: list[ActivityItem]
