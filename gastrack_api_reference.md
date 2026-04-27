# GasTrack Pro – Backend API Reference

> **Base URL:** `http://localhost:8000/api/v1`  
> **Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)  
> **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🏥 Health Check

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Returns `{ status: "ok" }` – used to verify the server is up |

---

## 🛢️ Tank Master — `/api/v1/tanks`

Manages the **Tank Master** — the registry of all gas storage tanks.  
Mirrors the `TankMasterView`, `AddTankPage`, `TankTable`, and `ViewTankPage` frontend components.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/tanks/` | List all tanks ordered by Tank ID |
| `GET` | `/tanks/active` | List only Active tanks (used to populate the Linked Tank dropdown in Production & Monitoring forms) |
| `GET` | `/tanks/{tank_id}` | Get details of a single tank |
| `POST` | `/tanks/` | Create a new tank (auto-generates `TK-XXXX` ID) |
| `PUT` | `/tanks/{tank_id}` | Update a **draft** tank (returns `409` if already posted) |
| `PATCH` | `/tanks/{tank_id}/post` | Lock a draft → posted (irreversible) |

### Tank fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | ✅ | e.g. "Oxygen Storage Unit 1" |
| `gas_type` | enum | ✅ | Oxygen, Nitrogen, LPG, CO2, Argon, Hydrogen |
| `capacity_value` | float | ✅ | Numeric capacity (e.g. 5000) |
| `capacity_unit` | enum | ✅ | Liters, Kg, m³ |
| `location` | string | ✅ | e.g. "Plant A - Zone 2" |
| `min_level` | float | ❌ | Alert threshold (optional) |
| `max_level` | float | ❌ | Max fill level (optional) |
| `calibration_ref` | string | ❌ | e.g. "CAL-2024-001" |
| `status` | enum | ✅ | Active, Inactive, Maintenance |
| `entry_mode` | enum | ✅ | `draft` = editable, `post` = locked |

---

## 🔥 Gas Production — `/api/v1/production`

Manages **production entries** — internally generated gas batches.  
Mirrors `ProductionView`, `AddProductionPage`, `ProductionTable`, `ViewProductionPage`.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/production/` | List all entries (newest first) |
| `GET` | `/production/{production_id}` | Get a single entry |
| `GET` | `/production/by-tank/{tank_id}` | All entries linked to a specific tank |
| `POST` | `/production/` | Create a new entry (auto-generates `PROD-XXXX` ID) |
| `PUT` | `/production/{production_id}` | Update a **draft** entry |
| `PATCH` | `/production/{production_id}/post` | Lock a draft → posted |

### Production entry fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `date` | date (ISO) | ✅ | YYYY-MM-DD |
| `plant` | string | ✅ | e.g. "Plant A" |
| `gas_type` | enum | ✅ | Oxygen, Nitrogen, LPG, CO2, Argon |
| `quantity` | float | ✅ | Amount produced |
| `quantity_unit` | enum | ✅ | Liters, Kg, m³ |
| `batch` | string | ❌ | e.g. "BATCH-2025-041" |
| `linked_tank_id` | FK | ❌ | Links to `tanks.tank_id` |
| `entry_mode` | enum | ✅ | `draft` / `post` |

---

## 💧 Tank Monitoring — `/api/v1/monitoring`

Manages **daily level entries** per tank — opening, added, issued, and auto-computed closing level.  
Mirrors `MonitoringView`, `AddLevelEntryPage`, `TankCard`.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/monitoring/tanks` | **Tank snapshot grid** — all tanks with `current_level`, `fill_percentage`, and `alert` flag (powers TankCard grid) |
| `GET` | `/monitoring/entries` | All level entries (newest first — Entry Log table) |
| `GET` | `/monitoring/entries/{entry_id}` | Single level entry |
| `GET` | `/monitoring/entries/by-tank/{tank_id}` | All entries for a specific tank |
| `POST` | `/monitoring/entries` | Create level entry — **closing_level is auto-computed** server-side: `opening + added − issued`. Tank's `current_level` is updated automatically. |
| `PUT` | `/monitoring/entries/{entry_id}` | Update a draft entry (recalculates closing level) |
| `PATCH` | `/monitoring/entries/{entry_id}/post` | Lock a draft → posted |

### Level entry fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `tank_id` | FK | ✅ | Must exist in `tanks` table |
| `date` | date (ISO) | ✅ | YYYY-MM-DD |
| `opening_level` | float | ✅ | Current level at start (in Liters) |
| `quantity_added` | float | ❌ | Gas added (default 0) |
| `quantity_issued` | float | ❌ | Gas dispensed (default 0) |
| `measurement_method` | enum | ❌ | Manual Dip, Sensor, Flow Meter, Visual Gauge |
| `entry_mode` | enum | ✅ | `draft` / `post` |
| `closing_level` | float | auto | Server computes: `opening + added − issued` |

---

## 📊 Dashboard — `/api/v1/dashboard`

Single aggregated endpoint powering the Dashboard page.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/dashboard/?activity_limit=10` | Aggregated stats + recent activity feed |

### Response shape

```json
{
  "stats": {
    "total_tanks": 12,
    "active_tanks": 10,
    "inactive_tanks": 1,
    "maintenance_tanks": 1,
    "low_level_alerts": 2,
    "today_production_total": 3200.0,
    "today_production_unit": "Liters",
    "today_production_entries": 4
  },
  "recent_activity": [
    {
      "type": "Production",
      "detail": "Oxygen — 500 Liters",
      "tank": "TK-1001",
      "time": "Today",
      "status": "Posted",
      "reference_id": "PROD-2006"
    }
  ]
}
```

---

## 🔒 Draft vs Posted Workflow

| State | Editable | Deletable | Endpoint |
|-------|----------|-----------|----------|
| `draft` | ✅ Yes | — | `PUT /{id}` |
| `post` | ❌ No | — | `PATCH /{id}/post` |

Attempting to `PUT` a posted record returns **HTTP 409 Conflict**.

---

## 🗂️ Folder Structure

```
backend/
├── .env.example                   # Environment variable template
├── requirements.txt               # Python dependencies
└── app/
    ├── __init__.py
    ├── main.py                    # FastAPI app, CORS, router registration
    ├── core/
    │   ├── __init__.py
    │   └── config.py              # Pydantic Settings (reads .env)
    ├── database/
    │   ├── __init__.py
    │   ├── database.py            # Engine + SessionLocal + Base
    │   └── deps.py                # get_db() FastAPI dependency
    └── modules/
        ├── __init__.py
        ├── tanks/                 # Tank Master
        │   ├── __init__.py
        │   ├── models.py          # Tank ORM model
        │   ├── schemas.py         # TankCreate | TankUpdate | TankOut
        │   ├── crud.py            # DB operations
        │   └── router.py          # /api/v1/tanks endpoints
        ├── production/            # Gas Production
        │   ├── __init__.py
        │   ├── models.py
        │   ├── schemas.py
        │   ├── crud.py
        │   └── router.py          # /api/v1/production endpoints
        ├── monitoring/            # Tank Monitoring
        │   ├── __init__.py
        │   ├── models.py
        │   ├── schemas.py
        │   ├── crud.py
        │   └── router.py          # /api/v1/monitoring endpoints
        └── dashboard/             # Dashboard
            ├── __init__.py
            ├── schemas.py
            ├── service.py         # Aggregation logic
            └── router.py          # /api/v1/dashboard endpoint
```
