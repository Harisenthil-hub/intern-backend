# app/modules/cylinder/service.py
from app.database.database import supabase_request
from app.modules.cylinder.schemas import TrackerCreate


def map_tracker_in(data: TrackerCreate) -> dict:
    return {
        "serial":          data.serial,
        "location":        data.location,
        "cylinder_status": data.cylinderStatus,
        "status":          data.status,
        "date":            data.date,
    }


def map_tracker_out(row: dict) -> dict:
    return {
        "_id":            row.get("id"),
        "serial":         row.get("serial"),
        "location":       row.get("location"),
        "cylinderStatus": row.get("cylinder_status"),
        "status":         row.get("status"),
        "date":           row.get("date"),
    }


async def get_all_trackers():
    rows = await supabase_request("GET", "trackers", filters="?order=created_at.desc")
    return [map_tracker_out(r) for r in rows]


async def create_tracker(data: TrackerCreate):
    rows = await supabase_request("POST", "trackers", data=map_tracker_in(data))
    return map_tracker_out(rows[0])


async def update_tracker(id: str, data: TrackerCreate):
    rows = await supabase_request(
        "PATCH", "trackers",
        data=map_tracker_in(data),
        filters=f"?id=eq.{id}"
    )
    return map_tracker_out(rows[0])


async def post_tracker(id: str):
    rows = await supabase_request(
        "PATCH", "trackers",
        data={"status": "posted"},
        filters=f"?id=eq.{id}"
    )
    return map_tracker_out(rows[0])