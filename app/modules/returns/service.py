# app/modules/returns/service.py
from app.database.database import supabase_request
from app.modules.returns.schemas import ReturnCreate


def map_return_in(data: ReturnCreate) -> dict:
    return {
        "return_id":     data.returnId,
        "customer_name": data.customerName,
        "date":          data.date,
        "cylinders":     [c.dict() for c in data.cylinders],
        "status":        data.status,
    }


def map_return_out(row: dict) -> dict:
    return {
        "_id":          row.get("id"),
        "returnId":     row.get("return_id"),
        "customerName": row.get("customer_name"),
        "date":         row.get("date"),
        "cylinders":    row.get("cylinders", []),
        "status":       row.get("status"),
    }


async def get_all_returns():
    rows = await supabase_request("GET", "returns", filters="?order=created_at.desc")
    return [map_return_out(r) for r in rows]


async def create_return(data: ReturnCreate):
    rows = await supabase_request("POST", "returns", data=map_return_in(data))
    return map_return_out(rows[0])


async def update_return(id: str, data: ReturnCreate):
    rows = await supabase_request(
        "PATCH", "returns",
        data=map_return_in(data),
        filters=f"?id=eq.{id}"
    )
    return map_return_out(rows[0])


async def post_return(id: str):
    rows = await supabase_request(
        "PATCH", "returns",
        data={"status": "posted"},
        filters=f"?id=eq.{id}"
    )
    return map_return_out(rows[0])