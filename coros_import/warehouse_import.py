"""Write consented watch data into the same fitness_demo tables as the public model."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from normalize import (
    fingerprint, parse_coros_activities, parse_coros_training_load,
    parse_coros_sleep, parse_coros_resting_hr, parse_coros_hrv, parse_coros_fitness,
)

ROOT = Path(__file__).resolve().parent.parent


def ensure_schema(conn) -> None:
    exists = conn.execute("SELECT 1 FROM information_schema.tables WHERE table_schema='fitness_demo' AND table_name='athlete'").fetchone()
    if not exists:
        conn.execute((ROOT / "warehouse" / "duckdb_schema.sql").read_text())


    # Existing private databases predate HRV; add the new table and review pointers in place.
    conn.execute("""CREATE TABLE IF NOT EXISTS fitness_demo.athlete_daily_hrv (
        athlete_id VARCHAR, source VARCHAR, wake_date DATE, hrv_avg_ms DECIMAL(18,3),
        normal_low_ms DECIMAL(18,3), normal_high_ms DECIMAL(18,3), baseline_ms DECIMAL(18,3),
        provider_evaluation VARCHAR, data_status VARCHAR, observed_at_utc TIMESTAMP,
        source_snapshot_id VARCHAR)""")
    has_review = conn.execute("SELECT 1 FROM information_schema.tables WHERE table_schema='fitness_demo' AND table_name='recovery_state'").fetchone()
    if has_review:
        conn.execute("ALTER TABLE fitness_demo.recovery_state ADD COLUMN IF NOT EXISTS hrv_source VARCHAR")
        conn.execute("ALTER TABLE fitness_demo.recovery_state ADD COLUMN IF NOT EXISTS hrv_wake_date DATE")
    conn.execute("""CREATE TABLE IF NOT EXISTS fitness_demo.import_coverage (
        athlete_id VARCHAR, source VARCHAR, category VARCHAR, window_start DATE,
        window_end DATE, imported_at_utc TIMESTAMP, source_record_count BIGINT,
        imported_record_count BIGINT, coverage_status VARCHAR, notes VARCHAR)""")


def put(conn, table: str, values: dict[str, Any]) -> None:
    columns = list(values)
    conn.execute(
        f"INSERT INTO fitness_demo.{table} ({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)})",
        list(values.values()),
    )


def raw_text(payload: Any) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, list):
        return "\n".join(x for x in payload if isinstance(x, str))
    return ""


def import_activities(conn, athlete_id: str, rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"activities": 0, "runs": 0, "possible_duplicates": 0}
    for item in rows:
        source, source_id = item["source"], item["source_activity_id"]
        if conn.execute("SELECT 1 FROM fitness_demo.activity WHERE athlete_id=? AND source=? AND source_activity_id=?", [athlete_id, source, source_id]).fetchone():
            continue
        aid = "act_" + fingerprint(athlete_id, source, source_id)
        eid = "evt_" + fingerprint(athlete_id, source, source_id)
        day, duration, distance = item["event_date"], item["duration_s"], item["distance_m"]
        # A close match across watch platforms needs human review; it is not treated as a second run.
        similar = conn.execute("""
            SELECT workout_event_id FROM fitness_demo.activity
            WHERE athlete_id=? AND source<>? AND activity_date=? AND sport_code=?
              AND ABS(workout_duration_s-?)<=90 AND ABS(distance_m-?)<=GREATEST(100, ? * 0.01)
            LIMIT 1
        """, [athlete_id, source, day, item["sport_code"], duration, distance, distance]).fetchone()
        status = "possible_duplicate" if similar else "canonical"
        if similar:
            counts["possible_duplicates"] += 1
            eid = similar[0]
        else:
            put(conn, "workout_event", {"athlete_id": athlete_id, "workout_event_id": eid,
                "event_date": day, "started_at_local": item.get("started_at_local"),
                "sport_code": item["sport_code"], "is_official_race": False,
                "participation_mode": "solo", "watch_elapsed_s": duration})
        put(conn, "activity", {"athlete_id": athlete_id, "activity_id": aid,
            "activity_date": day, "sport_code": item["sport_code"], "workout_event_id": eid,
            "source": source, "source_activity_id": source_id, "workout_duration_s": duration,
            "elapsed_duration_s": duration, "distance_m": distance,
            "avg_hr_bpm": item.get("avg_hr_bpm"), "avg_cadence_spm": item.get("avg_cadence_spm"),
            "avg_power_w": item.get("avg_power_w"), "calories_kcal": item.get("calories_kcal"),
            "dedup_status": status})
        counts["activities"] += 1
        if item["sport_code"] != "running" or similar:
            continue
        hr, cadence = item.get("avg_hr_bpm"), item.get("avg_cadence_spm")
        # Summary average is an estimate of sample-weighted mean, not an HR-zone duration.
        put(conn, "running_observation_fact", {
            "athlete_id": athlete_id, "workout_event_id": eid, "analysis_revision": 1,
            "segment_ordinal": 1, "segment_kind": "run", "run_context": "standalone",
            "phase_kind": "main", "run_environment": None, "event_date": day,
            "observation_date": day, "duration_basis": "watch_summary",
            "distance_status": "measured", "pace_basis": "measured", "duration_s": duration,
            "measured_distance_m": distance, "measured_pace_s_per_km": round(duration * 1000 / distance) if distance else None,
            "pace_time_s": duration if distance else None, "pace_distance_m": distance if distance else None,
            "avg_hr_bpm": hr, "hr_weighted_sum_bpm_s": hr * duration if hr is not None else None,
            "hr_weight_s": duration if hr is not None else None,
            "hr_sample_coverage_s": None,
            "avg_cadence_spm": cadence,
            "cadence_weighted_sum_spm_s": cadence * duration if cadence is not None else None,
            "cadence_weight_s": duration if cadence is not None else None,
            "cadence_sample_coverage_s": None,
            "sport_code": "running", "is_official_race": False, "participation_mode": "solo",
        })
        counts["runs"] += 1
    return counts


def import_payloads(conn, athlete_id: str, source: str, payloads: dict[str, Any], observed_at: datetime) -> dict[str, int]:
    ensure_schema(conn)
    if not conn.execute("SELECT 1 FROM fitness_demo.athlete WHERE athlete_id=?", [athlete_id]).fetchone():
        put(conn, "athlete", {"athlete_id": athlete_id, "timezone_name": None})
    if source == "garmin":
        activities = payloads.get("activities", {}).get("rows", [])
    elif source == "coros":
        activities = parse_coros_activities(raw_text(payloads.get("activities", "")))
    else:
        raise ValueError("Unsupported watch source")
    counts = import_activities(conn, athlete_id, activities)
    if source != "coros":
        return counts
    for category, parser, table, date_key in [
        ("training_load", parse_coros_training_load, "athlete_daily_training_load", "local_date"),
        ("sleep", parse_coros_sleep, "athlete_daily_sleep", "wake_date"),
        ("resting_hr", parse_coros_resting_hr, "athlete_daily_resting_hr", "local_date"),
    ]:
        rows = parser(raw_text(payloads.get(category, "")))
        counts[category] = 0
        for row in rows:
            day = row[date_key]
            conn.execute(f"DELETE FROM fitness_demo.{table} WHERE athlete_id=? AND source=? AND {date_key}=?", [athlete_id, source, day])
            put(conn, table, {"athlete_id": athlete_id, "source": source, **row,
                "observed_at_utc": observed_at,
                "source_snapshot_id": fingerprint(athlete_id, source, category, day)})
            counts[category] += 1
    counts["hrv"] = 0
    hrv_payload = payloads.get("hrv")
    if hrv_payload is not None:
        for row in parse_coros_hrv(hrv_payload):
            day = row["wake_date"]
            conn.execute("DELETE FROM fitness_demo.athlete_daily_hrv WHERE athlete_id=? AND source=? AND wake_date=?", [athlete_id, source, day])
            put(conn, "athlete_daily_hrv", {"athlete_id": athlete_id, "source": source, **row,
                "observed_at_utc": observed_at,
                "source_snapshot_id": fingerprint(athlete_id, source, "hrv", day)})
            counts["hrv"] += 1
    counts["fitness"] = 0
    for row in parse_coros_fitness(raw_text(payloads.get("fitness", ""))):
        code = row["metric_code"]
        mid = "meas_" + fingerprint(athlete_id, source, code, observed_at.isoformat())
        if conn.execute("SELECT 1 FROM fitness_demo.fitness_measurement WHERE measurement_id=?", [mid]).fetchone():
            continue
        put(conn, "fitness_measurement", {"athlete_id": athlete_id, "measurement_id": mid,
            **row, "observed_at_utc": observed_at, "time_quality": "import_observed",
            "source": source})
        counts["fitness"] += 1
    return counts
