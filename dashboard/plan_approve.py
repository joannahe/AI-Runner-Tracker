"""Activate an athlete-reviewed local training plan version.

Only a saved pending version can be approved. This does not send the plan to
COROS or any other service.
"""

import argparse
import json
from decimal import Decimal
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "personal_duckdb" / "joanna_fitness.duckdb"


def comparable_rows(rows):
    """Compare numeric values without treating DuckDB decimal scale as a revision."""
    return sorted(tuple(Decimal(str(value)) if isinstance(value, (float, Decimal)) else value
                        for value in row) for row in rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft", type=Path, help="The reviewed JSON draft")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()
    draft = json.loads(args.draft.read_text(encoding="utf-8"))
    athlete = draft["athlete_id"]
    goal = draft["goal"]
    plan = draft["plan"]
    with duckdb.connect(str(args.db)) as db:
        row = db.execute("""SELECT goal_id,goal_version,approval_status,status
            FROM fitness_demo.action_plan
            WHERE athlete_id=? AND plan_id=? AND plan_version=?""",
            [athlete, plan["plan_id"], plan["version"]]).fetchone()
        if row != (goal["goal_id"], goal["version"], "pending", "draft"):
            raise ValueError("The exact reviewed plan version is not saved and pending")
        stored_actions = db.execute("""SELECT action_id,CAST(scheduled_date AS VARCHAR),
                   action_kind,planned_intensity,title,title_zh,target_duration_min,
                   target_distance_km,target_distance_min_km,target_distance_max_km,distance_basis
            FROM fitness_demo.planned_action
            WHERE athlete_id=? AND plan_id=? AND plan_version=?""",
            [athlete, plan["plan_id"], plan["version"]]).fetchall()
        expected_actions = [
            (a["action_id"], a["date"], a["kind"],
             None if a["kind"] == "rest" else a["intensity"], a["title"], a.get("title_zh"),
             a.get("duration_min"), a.get("distance_km"),
             a.get("distance_min_km", a.get("distance_km")),
             a.get("distance_max_km", a.get("distance_km")), a.get("distance_basis"))
            for a in draft["actions"]
        ]
        if comparable_rows(stored_actions) != comparable_rows(expected_actions):
            raise ValueError("Saved actions differ from the reviewed draft")
        stored_segments = db.execute("""SELECT action_id,segment_ordinal,segment_type,title_en,title_zh,
                   target_duration_min,target_distance_km,target_pace_fast_s_per_km,
                   target_pace_slow_s_per_km,target_hr_low_bpm,target_hr_high_bpm
            FROM fitness_demo.planned_action_segment
            WHERE athlete_id=? AND plan_id=? AND plan_version=?""",
            [athlete, plan["plan_id"], plan["version"]]).fetchall()
        expected_segments = [
            (a["action_id"], ordinal, s["type"], s["title_en"], s["title_zh"],
             s.get("duration_min"), s.get("distance_km"), s.get("pace_fast_s_per_km"),
             s.get("pace_slow_s_per_km"), s.get("hr_low_bpm"), s.get("hr_high_bpm"))
            for a in draft["actions"] for ordinal, s in enumerate(a.get("segments", []), 1)
        ]
        if comparable_rows(stored_segments) != comparable_rows(expected_segments):
            raise ValueError("Saved workout segments differ from the reviewed draft")
        db.begin()
        try:
            db.execute("""UPDATE fitness_demo.athlete_goal SET status='active'
                WHERE athlete_id=? AND goal_id=? AND goal_version=?""",
                [athlete, goal["goal_id"], goal["version"]])
            db.execute("""UPDATE fitness_demo.action_plan
                SET status='superseded'
                WHERE athlete_id=? AND goal_id=? AND goal_version=?
                  AND status='active' AND NOT (plan_id=? AND plan_version=?)""",
                [athlete, goal["goal_id"], goal["version"], plan["plan_id"], plan["version"]])
            db.execute("""UPDATE fitness_demo.action_plan
                SET status='active',approval_status='approved',
                    approved_at_utc=CURRENT_TIMESTAMP AT TIME ZONE 'UTC'
                WHERE athlete_id=? AND plan_id=? AND plan_version=?""",
                [athlete, plan["plan_id"], plan["version"]])
            db.execute("""UPDATE fitness_demo.planned_action
                SET planning_status='approved'
                WHERE athlete_id=? AND plan_id=? AND plan_version=?""",
                [athlete, plan["plan_id"], plan["version"]])
            db.commit()
        except Exception:
            db.rollback()
            raise
    print(json.dumps({"status": "approved_active", "plan_id": plan["plan_id"],
                      "version": plan["version"], "actions": len(stored_actions)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
