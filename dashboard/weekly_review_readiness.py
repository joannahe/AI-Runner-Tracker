"""Check whether last week's watch data is ready for an Agent-written review.

This gate never generates coaching text. A verified coverage row must attest to the
provider window; merely saving an MCP response is not enough.
"""

from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from pathlib import Path

import duckdb


def previous_week(as_of: date) -> tuple[date, date]:
    this_monday = as_of - timedelta(days=as_of.weekday())
    return this_monday - timedelta(days=7), this_monday - timedelta(days=1)


def evaluate(athlete_id: str, as_of: date, coverage: list[dict], sunday_night_sleep: bool) -> dict:
    start, end = previous_week(as_of)
    next_monday = end + timedelta(days=1)
    required = {
        "activities": [start + timedelta(days=i) for i in range(7)],
        # Monday night's sleep wakes Tuesday; Sunday night's wakes next Monday.
        "sleep": [start + timedelta(days=i) for i in range(1, 8)],
    }
    missing = {}
    for category, days in required.items():
        verified = [row for row in coverage if row.get("athlete_id") == athlete_id
                    and row.get("category") == category
                    and row.get("status") == "verified_complete"]
        uncovered = [day.isoformat() for day in days if not any(
            date.fromisoformat(str(row["start"])) <= day <= date.fromisoformat(str(row["end"]))
            for row in verified)]
        if uncovered:
            missing[category] = uncovered
    if not sunday_night_sleep:
        missing.setdefault("sunday_night_sleep", []).append(next_monday.isoformat())
    return {
        "athlete_id": athlete_id, "week_start": start.isoformat(), "week_end": end.isoformat(),
        "sunday_night_wake_date": next_monday.isoformat(),
        "status": "ready_for_agent" if not missing else "waiting_for_data",
        "missing": missing,
    }


def check_database(path: Path, athlete_id: str, as_of: date) -> dict:
    with duckdb.connect(str(path), read_only=True) as conn:
        present = {name for (name,) in conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='fitness_demo'"
        ).fetchall()}
        coverage = []
        if "import_coverage" in present:
            rows = conn.execute("""SELECT athlete_id, category, CAST(window_start AS VARCHAR),
                CAST(window_end AS VARCHAR), coverage_status FROM fitness_demo.import_coverage
                WHERE athlete_id=?""", [athlete_id]).fetchall()
            coverage = [dict(zip(("athlete_id", "category", "start", "end", "status"), row)) for row in rows]
        _, end = previous_week(as_of)
        wake_date = end + timedelta(days=1)
        sleep = "athlete_daily_sleep" in present and bool(conn.execute(
            "SELECT 1 FROM fitness_demo.athlete_daily_sleep WHERE athlete_id=? AND wake_date=? AND main_sleep_min IS NOT NULL LIMIT 1",
            [athlete_id, wake_date],
        ).fetchone())
    return evaluate(athlete_id, as_of, coverage, sleep)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--athlete", required=True)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    if not args.db.is_file():
        parser.error("DuckDB file does not exist")
    print(json.dumps(check_database(args.db, args.athlete, args.as_of), ensure_ascii=False))


if __name__ == "__main__":
    main()
