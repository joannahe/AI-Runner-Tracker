"""Validate an Agent-proposed plan and optionally save it as a pending DuckDB plan.

The athlete's approval is a separate step. This command never changes an
approved plan and refuses an existing plan version.
"""

import argparse
import json
from datetime import date
from pathlib import Path

import duckdb
from plan_schema import ensure_plan_detail_schema

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "personal_duckdb" / "joanna_fitness.duckdb"
INTENSITIES = {"low", "moderate", "high"}
KINDS = {"run", "race", "rest", "cross_training"}


def validate(document, connection):
    athlete = document["athlete_id"]
    goal, plan, actions = document["goal"], document["plan"], document["actions"]
    if not isinstance(athlete, str) or not athlete:
        raise ValueError("athlete_id is required")
    if connection.execute("SELECT COUNT(*) FROM fitness_demo.athlete WHERE athlete_id=?", [athlete]).fetchone()[0] != 1:
        raise ValueError("athlete_id is absent from the selected database")
    if not isinstance(actions, list) or not actions:
        raise ValueError("At least one dated action is required")
    for key in ("goal_id", "goal_type", "title"):
        if not goal.get(key):
            raise ValueError(f"goal.{key} is required")
    for key in ("plan_id", "title", "summary"):
        if not plan.get(key):
            raise ValueError(f"plan.{key} is required")
    goal_version, plan_version = goal.get("version"), plan.get("version")
    if not isinstance(goal_version, int) or goal_version < 1 or not isinstance(plan_version, int) or plan_version < 1:
        raise ValueError("Goal and plan versions must be positive integers")
    criterion = goal["criterion"]
    for key in ("criterion_id", "metric_name", "comparison_operator", "target_unit", "target_date"):
        if not criterion.get(key):
            raise ValueError(f"goal.criterion.{key} is required")
    if criterion["comparison_operator"] not in {"<", "<=", ">", ">=", "="}:
        raise ValueError("Invalid criterion comparator")
    date.fromisoformat(criterion["target_date"])
    target = criterion.get("target_value")
    if not isinstance(target, (int, float)) or target <= 0:
        raise ValueError("Target value must be positive")
    seen = set()
    for action in actions:
        when = date.fromisoformat(action["date"])
        identifier = action.get("action_id")
        if not identifier or identifier in seen:
            raise ValueError("Each action needs a unique action_id")
        seen.add(identifier)
        if action.get("kind") not in KINDS:
            raise ValueError(f"Invalid kind on {identifier}")
        intensity = action.get("intensity")
        if action["kind"] == "rest":
            if intensity not in (None, "none"):
                raise ValueError("Rest actions cannot have training intensity")
        elif intensity not in INTENSITIES:
            raise ValueError(f"Action {identifier} needs low, moderate or high intensity")
        minutes = action.get("duration_min")
        if minutes is not None and (not isinstance(minutes, int) or minutes <= 0):
            raise ValueError(f"Invalid duration on {identifier}")
        if not action.get("title"):
            raise ValueError(f"Action {identifier} needs a title")
        distance = action.get("distance_km")
        distance_min = action.get("distance_min_km", distance)
        distance_max = action.get("distance_max_km", distance)
        if distance_min is not None and distance_max is not None and not (0 <= distance_min <= distance_max):
            raise ValueError(f"Invalid distance range on {identifier}")
        if distance is not None and (distance < 0 or distance_min is not None and distance < distance_min or distance_max is not None and distance > distance_max):
            raise ValueError(f"Invalid planned distance on {identifier}")
        if action["kind"] == "rest" and any(v not in (None, 0) for v in (distance, distance_min, distance_max)):
            raise ValueError(f"Rest action {identifier} cannot include running distance")
        segments = action.get("segments", [])
        if segments and [s.get("type") for s in segments] != [s.get("type") for s in segments if s.get("type") in {"warmup", "main", "cooldown"}]:
            raise ValueError(f"Invalid segment type on {identifier}")
        for segment in segments:
            if not segment.get("title_en") or not segment.get("title_zh"):
                raise ValueError(f"Segment on {identifier} needs both language titles")
            for key in ("pace_fast_s_per_km", "pace_slow_s_per_km", "hr_low_bpm", "hr_high_bpm"):
                value = segment.get(key)
                if value is not None and (not isinstance(value, int) or value <= 0):
                    raise ValueError(f"Invalid {key} on {identifier}")
            lo, hi = segment.get("pace_fast_s_per_km"), segment.get("pace_slow_s_per_km")
            if lo is not None and hi is not None and lo > hi:
                raise ValueError(f"Pace range is reversed on {identifier}")
            lo, hi = segment.get("hr_low_bpm"), segment.get("hr_high_bpm")
            if lo is not None and hi is not None and lo > hi:
                raise ValueError(f"Heart-rate range is reversed on {identifier}")
        if segments and minutes is not None and sum(s.get("duration_min") or 0 for s in segments) != minutes:
            raise ValueError(f"Segment durations do not add to action duration on {identifier}")
        if segments and distance is not None and all(s.get("distance_km") is not None for s in segments):
            if abs(sum(s["distance_km"] for s in segments) - distance) > 0.02:
                raise ValueError(f"Segment distances do not add to action distance on {identifier}")
        if when > date.fromisoformat(criterion["target_date"]):
            raise ValueError("An action is scheduled after the goal date")
    existing = connection.execute(
        "SELECT COUNT(*) FROM fitness_demo.action_plan WHERE athlete_id=? AND plan_id=? AND plan_version=?",
        [athlete, plan["plan_id"], plan_version],
    ).fetchone()[0]
    if existing:
        raise ValueError("This plan version already exists; create a new version")
    saved_goal = connection.execute(
        "SELECT goal_type,title FROM fitness_demo.athlete_goal WHERE athlete_id=? AND goal_id=? AND goal_version=?",
        [athlete, goal["goal_id"], goal_version],
    ).fetchone()
    if saved_goal and saved_goal != (goal["goal_type"], goal["title"]):
        raise ValueError("Existing goal version has different details")
    saved_criterion = connection.execute(
        """SELECT metric_name,comparison_operator,target_value,target_unit,target_date
           FROM fitness_demo.goal_criterion
           WHERE athlete_id=? AND goal_id=? AND goal_version=? AND criterion_id=?""",
        [athlete, goal["goal_id"], goal_version, criterion["criterion_id"]],
    ).fetchone()
    if saved_criterion and (
        saved_criterion[0] != criterion["metric_name"]
        or saved_criterion[1] != criterion["comparison_operator"]
        or float(saved_criterion[2]) != float(target)
        or saved_criterion[3] != criterion["target_unit"]
        or saved_criterion[4] != date.fromisoformat(criterion["target_date"])
    ):
        raise ValueError("Existing goal criterion has different details")
    return athlete, goal, criterion, plan, actions, bool(saved_goal), bool(saved_criterion)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft", type=Path)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--apply", action="store_true", help="Write a pending plan after validation")
    args = parser.parse_args()
    document = json.loads(args.draft.read_text(encoding="utf-8"))
    if not args.db.is_file():
        parser.error("Database file does not exist")
    with duckdb.connect(str(args.db), read_only=not args.apply) as db:
        if args.apply:
            ensure_plan_detail_schema(db)
        athlete, goal, criterion, plan, actions, goal_exists, criterion_exists = validate(document, db)
        columns = {row[0] for row in db.execute("DESCRIBE fitness_demo.planned_action").fetchall()}
        if "planned_intensity" not in columns:
            raise ValueError("planned_action.planned_intensity is required for schedule checks")
        if args.apply:
            db.begin()
            try:
                if not goal_exists:
                    db.execute("INSERT INTO fitness_demo.athlete_goal VALUES (?,?,?,?,?,?,?)", [
                        athlete, goal["goal_id"], goal["version"], goal["goal_type"], goal["title"], "draft", None])
                if not criterion_exists:
                    db.execute("INSERT INTO fitness_demo.goal_criterion VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", [
                        athlete, goal["goal_id"], goal["version"], criterion["criterion_id"],
                        criterion.get("criterion_kind", "race_time"), criterion["metric_name"],
                        criterion["comparison_operator"], criterion["target_value"], criterion["target_unit"],
                        criterion.get("aggregation_window", "event"), criterion["target_date"],
                        criterion.get("evidence_policy", "same_distance_official_result"), None])
                db.execute("INSERT INTO fitness_demo.action_plan VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", [
                    athlete, plan["plan_id"], plan["version"], goal["goal_id"], goal["version"],
                    plan["title"], plan["summary"], "draft", "pending", None, None,
                    plan.get("revision_reason", "initial_agent_draft")])
                for action in actions:
                    db.execute("""INSERT INTO fitness_demo.planned_action
                        (athlete_id,plan_id,plan_version,action_id,scheduled_date,action_kind,
                         planned_intensity,title,title_zh,target_duration_min,target_distance_km,
                         target_distance_min_km,target_distance_max_km,distance_basis,planning_status,
                         completion_status,candidate_event_id,verified_event_id,match_method,
                         match_reviewed_at_utc,source)
                         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", [
                        athlete, plan["plan_id"], plan["version"], action["action_id"],
                        action["date"], action["kind"], None if action["kind"] == "rest" else action["intensity"],
                        action["title"], action.get("title_zh"), action.get("duration_min"), action.get("distance_km"),
                        action.get("distance_min_km", action.get("distance_km")),
                        action.get("distance_max_km", action.get("distance_km")),
                        action.get("distance_basis"), "proposed", "not_assessed",
                        None, None, None, None, "agent_draft"])
                    for ordinal, segment in enumerate(action.get("segments", []), 1):
                        db.execute("""INSERT INTO fitness_demo.planned_action_segment
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", [
                            athlete, plan["plan_id"], plan["version"], action["action_id"],
                            ordinal, segment["type"], segment["title_en"], segment["title_zh"],
                            segment.get("duration_min"), segment.get("distance_km"),
                            segment.get("pace_fast_s_per_km"), segment.get("pace_slow_s_per_km"),
                            segment.get("hr_low_bpm"), segment.get("hr_high_bpm")])
                db.commit()
            except Exception:
                db.rollback()
                raise
    print(json.dumps({"status": "saved_pending" if args.apply else "valid_draft",
                      "plan_id": plan["plan_id"], "version": plan["version"],
                      "actions": len(actions), "database": str(args.db)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
