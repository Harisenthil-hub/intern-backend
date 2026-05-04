# app/modules/dispatch/service.py
from app.database.database import supabase_request
from app.modules.dispatch.schemas import DispatchCreate


# ── Convert React camelCase → DB snake_case ──
def map_dispatch_in(data: DispatchCreate) -> dict:
    return {
        "dispatch_id":   data.dispatchId,
        "customer_name": data.customerName,
        "vehicle":       data.vehicle,
        "driver":        data.driver,
        "route":         data.route,
        "date":          data.date,
        "cylinders":     [c.dict() for c in data.cylinders],
        "status":        data.status,
    }


# ── Convert DB snake_case → React camelCase ──
def map_dispatch_out(row: dict) -> dict:
    return {
        "_id":          row.get("id"),
        "dispatchId":   row.get("dispatch_id"),
        "customerName": row.get("customer_name"),
        "vehicle":      row.get("vehicle"),
        "driver":       row.get("driver"),
        "route":        row.get("route"),
        "date":         row.get("date"),
        "cylinders":    row.get("cylinders", []),
        "status":       row.get("status"),
    }


# ── Service functions ──

async def get_all_dispatches():
    rows = await supabase_request("GET", "dispatches", filters="?order=created_at.desc")
    return [map_dispatch_out(r) for r in rows]


async def create_dispatch(data: DispatchCreate):
    rows = await supabase_request("POST", "dispatches", data=map_dispatch_in(data))
    return map_dispatch_out(rows[0])


async def update_dispatch(id: str, data: DispatchCreate):
    rows = await supabase_request(
        "PATCH", "dispatches",
        data=map_dispatch_in(data),
        filters=f"?id=eq.{id}"
    )
    return map_dispatch_out(rows[0])


async def post_dispatch(id: str):
    rows = await supabase_request(
        "PATCH", "dispatches",
        data={"status": "posted"},
        filters=f"?id=eq.{id}"
    )
    return map_dispatch_out(rows[0])