"""Apply SQL migrations placed in the `migrations/` folder.

Usage (from backend/):

    python -m scripts.apply_migrations

This script executes files ending with .sql in alphabetical order.

It uses the application's SQLAlchemy `engine`.
"""

import os
from sqlalchemy import text

from app.database.database import engine

MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "..", "migrations")


def apply_sql_file(conn, path: str):
    print(f"Applying: {os.path.basename(path)}")
    with open(path, "r", encoding="utf-8") as fh:
        sql = fh.read()

    # Split into individual statements and execute sequentially to avoid
    # driver / server restrictions on multi-statement execution.
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    for stmt in statements:
        conn.execute(text(stmt))


def main():
    if not os.path.isdir(MIGRATIONS_DIR):
        print("Migrations directory not found:", MIGRATIONS_DIR)
        return

    files = sorted(
        f for f in os.listdir(MIGRATIONS_DIR) if f.endswith(".sql")
    )
    if not files:
        print("No .sql migration files found in", MIGRATIONS_DIR)
        return

    with engine.begin() as conn:
        for fname in files:
            path = os.path.join(MIGRATIONS_DIR, fname)
            try:
                apply_sql_file(conn, path)
            except Exception as exc:
                print(f"Error applying {fname}:", exc)
                raise

    print("Migrations applied successfully.")


if __name__ == "__main__":
    main()
