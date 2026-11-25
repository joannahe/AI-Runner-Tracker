"""Exercise the weekly import gate without private watch data."""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dashboard"))
from weekly_review_readiness import evaluate


def window(category, start, end, status="verified_complete"):
    return {"athlete_id": "demo_01", "category": category,
            "start": start, "end": end, "status": status}


as_of = date(2026, 4, 20)  # Monday, after the Sunday night sleep wakes.
rows = [window("activities", "2026-04-13", "2026-04-19"),
        window("sleep", "2026-04-14", "2026-04-20")]
ready = evaluate("demo_01", as_of, rows, True)
assert ready["status"] == "ready_for_agent" and ready["week_end"] == "2026-04-19"
assert evaluate("demo_01", as_of, rows, False)["missing"]["sunday_night_sleep"] == ["2026-04-20"]
unverified = rows[:1] + [window("sleep", "2026-04-14", "2026-04-20", "saved_unverified")]
assert evaluate("demo_01", as_of, unverified, True)["status"] == "waiting_for_data"
split = [window("activities", "2026-04-13", "2026-04-15"),
         window("activities", "2026-04-16", "2026-04-19"), rows[1]]
assert evaluate("demo_01", as_of, split, True)["status"] == "ready_for_agent"
print("Weekly gate: complete, missing sleep, unverified import, and split windows passed.")
