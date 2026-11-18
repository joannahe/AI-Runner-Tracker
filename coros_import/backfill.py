"""One-time migration of already consented COROS responses to fitness_demo."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

import duckdb

from warehouse_import import import_payloads

DB = Path(__file__).resolve().parent / "private_data" / "coros_import.duckdb"


def main() -> None:
    if not DB.exists():
        raise SystemExit("No private COROS database was found")
    backup = DB.with_suffix(".before-semantic-import.duckdb")
    if not backup.exists():
        shutil.copy2(DB, backup)
    with duckdb.connect(str(DB)) as conn:
        rows = conn.execute("SELECT participant_id, category, imported_at, payload_json FROM coros_observations").fetchall()
        by_person = {}
        for pid, category, imported_at, raw in rows:
            by_person.setdefault(pid, {})[category] = (json.loads(raw), imported_at)
        for pid, categories in by_person.items():
            payloads = {k: v[0] for k, v in categories.items()}
            when = max(v[1] for v in categories.values())
            conn.execute("BEGIN TRANSACTION")
            try:
                result = import_payloads(conn, pid, "coros", payloads, when)
                conn.execute("COMMIT")
            except Exception:
                conn.execute("ROLLBACK")
                raise
            print("Participant", pid, result)
    print("Private backup:", backup)


if __name__ == "__main__":
    main()
