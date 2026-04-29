Migration files for the backend

Files:
- `create_procurement_and_inventory.sql` — creates `gas_procurements` and `inventory_transactions` tables.
- `update_inventory_and_create_gas_issues.sql` — creates `gas_issues` and makes `inventory_transactions.reference_type` generic.
- `update_inventory_and_create_loss_records.sql` — creates `loss_records` for loss / leakage monitoring.

How to apply (from the `backend/` folder):

PowerShell / cmd:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m scripts.apply_migrations
```

Notes:
- The script uses the `engine` defined in `app.database.database`. Ensure your DB connection settings (env) point to the intended database.
- This is a simple SQL-applier for environments without Alembic. Consider migrating to Alembic for production deployments.

Running tests (integration):

```powershell
# ensure test DB is configured in env
pytest -q
```

Tests will attempt to call the running application endpoints via FastAPI TestClient and will modify DB state; run against a disposable/test database.
