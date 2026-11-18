"""Build an offline running capability dashboard from a local DuckDB dataset."""

from datetime import date, datetime
from decimal import Decimal
import argparse
import json
from pathlib import Path
import duckdb
import yaml

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "warehouse" / "running_demo.duckdb"
PERSONAL_DB = ROOT / "personal_duckdb" / "joanna_fitness.duckdb"
TEMPLATE = Path(__file__).with_name("index.template.html")
OUTPUT = Path(__file__).with_name("index.html")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--personal", action="store_true", help="Read the bundled personal dataset and write personal-preview.html")
parser.add_argument("--db", type=Path, help="Primary local DuckDB source (used with --personal for a separate preview)")
parser.add_argument("--additional-db", type=Path, action="append", default=[], help="Additional athlete DuckDB source; repeat for multiple imports")
args = parser.parse_args()
if args.personal:
    DB = PERSONAL_DB
    OUTPUT = Path(__file__).with_name("personal-preview.html")
if args.db:
    DB = args.db.expanduser().resolve()


def normal(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def rows(connection, sql):
    cursor = connection.execute(sql)
    names = [item[0] for item in cursor.description]
    return [dict(zip(names, map(normal, record))) for record in cursor.fetchall()]


def collect_database(path):
    with duckdb.connect(str(path), read_only=True) as conn:
        present = {name for (name,) in conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='fitness_demo'").fetchall()}
        athlete_columns = {column for (column,) in conn.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='fitness_demo' AND table_name='athlete'").fetchall()}
        display_name = "display_name" if "display_name" in athlete_columns else "NULL AS display_name"
        def optional(table, sql):
            return rows(conn, sql) if table in present else []
        lap_rows = optional("activity_segment", """
            SELECT a.athlete_id, CAST(a.activity_date AS VARCHAR) AS date,
                a.workout_event_id AS id, s.lap_ordinal,
                s.avg_cadence_spm AS cadence, s.avg_power_w AS power,
                s.avg_pace_s_per_km AS pace
            FROM fitness_demo.activity a JOIN fitness_demo.activity_segment s
              ON s.athlete_id = a.athlete_id AND s.activity_id = a.activity_id
            WHERE a.sport_code = 'running' AND a.dedup_status IN ('canonical', 'unique')
              AND s.segment_kind = 'run' AND s.is_canonical = TRUE
            ORDER BY a.activity_date, s.lap_ordinal
        """)
        lap_athletes = {row["athlete_id"] for row in lap_rows}
        summary_rows = rows(conn, """
                SELECT athlete_id, CAST(activity_date AS VARCHAR) AS date, workout_event_id AS id,
                    1 AS lap_ordinal, avg_cadence_spm AS cadence, avg_power_w AS power,
                    CASE WHEN distance_m > 0 THEN workout_duration_s * 1000.0 / distance_m END AS pace
                FROM fitness_demo.activity
                WHERE sport_code='running' AND dedup_status IN ('canonical', 'unique')
                ORDER BY activity_date
            """)
        lap_rows.extend(row for row in summary_rows if row["athlete_id"] not in lap_athletes)
        gait_source_by_athlete = {
            athlete_id: ("canonical_laps" if athlete_id in lap_athletes else "activity_summary")
            for (athlete_id,) in conn.execute("SELECT athlete_id FROM fitness_demo.athlete").fetchall()
        }
        payload = {
            "meta": {"personal": args.personal, "gait_source_by_athlete": gait_source_by_athlete},
            "athletes": rows(conn, f"SELECT athlete_id, {display_name}, gender_code FROM fitness_demo.athlete ORDER BY athlete_id"),
            "runs": rows(conn, """
                SELECT r.athlete_id, CAST(r.event_date AS VARCHAR) AS date, r.workout_event_id AS id,
                    MAX(r.run_context) AS run_context, SUM(r.duration_s) AS duration_s,
                    SUM(r.measured_distance_m) AS measured_distance_m,
                    SUM(r.pace_time_s) AS pace_time_s, SUM(r.pace_distance_m) AS pace_distance_m,
                    SUM(r.hr_weighted_sum_bpm_s) AS hr_weighted_sum_bpm_s, SUM(r.hr_weight_s) AS hr_weight_s,
                    SUM(r.cadence_weighted_sum_spm_s) AS cadence_weighted_sum_spm_s,
                    SUM(r.cadence_weight_s) AS cadence_weight_s,
                    MAX(e.is_official_race) AS is_official_race,
                    MAX(e.event_name) AS event_name, MAX(e.official_finish_s) AS official_finish_s
                FROM fitness_demo.v_running_observation r
                LEFT JOIN fitness_demo.workout_event e
                  ON e.athlete_id = r.athlete_id AND e.workout_event_id = r.workout_event_id
                GROUP BY r.athlete_id, r.event_date, r.workout_event_id
                ORDER BY r.event_date, r.workout_event_id
            """),
            "laps": lap_rows,
            "load": rows(conn, "SELECT athlete_id, CAST(local_date AS VARCHAR) AS date, short_term_load AS short_load, long_term_load AS long_load, load_ratio AS ratio, provider_status AS status FROM fitness_demo.athlete_daily_training_load ORDER BY local_date"),
            "sleep": rows(conn, "SELECT athlete_id, CAST(wake_date AS VARCHAR) AS date, main_sleep_min AS main_min, daily_sleep_min AS daily_min, sleep_score FROM fitness_demo.athlete_daily_sleep ORDER BY wake_date"),
            "rhr": rows(conn, "SELECT athlete_id, CAST(local_date AS VARCHAR) AS date, rhr_bpm AS bpm FROM fitness_demo.athlete_daily_resting_hr ORDER BY local_date"),
            "activity_focus": optional("activity", "SELECT athlete_id, workout_event_id AS id, CAST(activity_date AS VARCHAR) AS date, training_focus AS focus FROM fitness_demo.activity WHERE sport_code='running' AND dedup_status IN ('canonical','unique') ORDER BY activity_date"),
            "hrv": optional("athlete_daily_hrv", "SELECT athlete_id, CAST(wake_date AS VARCHAR) AS date, hrv_avg_ms AS avg_ms, normal_low_ms AS normal_low, normal_high_ms AS normal_high, provider_evaluation AS evaluation, data_status AS status FROM fitness_demo.athlete_daily_hrv ORDER BY wake_date"),
            "recovery": optional("athlete_recovery_observation", "SELECT athlete_id, CAST(observed_at_utc AS VARCHAR) AS observed, recovery_pct AS pct, recovery_level AS level FROM fitness_demo.athlete_recovery_observation ORDER BY observed_at_utc"),
            "fitness": optional("v_latest_body_measurement", "SELECT athlete_id, metric_code AS code, metric_value AS value, unit, CAST(effective_from_utc AS VARCHAR) AS effective, CAST(observed_at_utc AS VARCHAR) AS observed FROM fitness_demo.v_latest_body_measurement ORDER BY observed_at_utc"),
            "hr_zones": optional("athlete_hr_zone", "SELECT athlete_id, zone_index AS zone, lower_inclusive_bpm AS low, upper_exclusive_bpm AS high FROM fitness_demo.athlete_hr_zone ORDER BY zone_index"),
            "pace_zones": optional("athlete_pace_zone", "SELECT athlete_id, zone_index AS zone, fast_boundary_s_per_km AS fast, slow_boundary_s_per_km AS slow FROM fitness_demo.athlete_pace_zone ORDER BY zone_index"),
        }
    return payload

DATA_KEYS = ("athletes", "runs", "laps", "load", "sleep", "rhr", "hrv", "activity_focus", "recovery", "fitness", "hr_zones", "pace_zones")


def merge_databases(paths):
    merged = {key: [] for key in DATA_KEYS}
    merged["meta"] = {"personal": args.personal, "gait_source_by_athlete": {}}
    multi = len(paths) > 1
    for source_index, path in enumerate(paths):
        source = collect_database(path)
        if args.personal and source_index == 0:
            owner_id = source["athletes"][0]["athlete_id"] if source["athletes"] else None
            merged["meta"]["goal"] = {"athlete_id": f"0:{owner_id}" if multi else owner_id,
                "type": "half_marathon", "target_date": "2027-03-21",
                "target_time_s": 7800, "distance_km": 21.0975, "status": "demo_goal"}
        athlete_ids = {row["athlete_id"] for row in source["athletes"]}
        for key in DATA_KEYS:
            for row in source[key]:
                if row["athlete_id"] not in athlete_ids:
                    raise ValueError(f"{path}: {key} has an athlete_id absent from athlete table")
                row["athlete_id"] = f"{source_index}:{row['athlete_id']}" if multi else row["athlete_id"]
                merged[key].append(row)
        for athlete_id, gait_source in source["meta"]["gait_source_by_athlete"].items():
            key = f"{source_index}:{athlete_id}" if multi else athlete_id
            merged["meta"]["gait_source_by_athlete"][key] = gait_source
    return merged


payload = merge_databases([DB, *[path.expanduser().resolve() for path in args.additional_db]])

encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
ontology = yaml.safe_load((ROOT / "fitness_ontology.yaml").read_text(encoding="utf-8"))
rules = ontology["x_coaching_knowledge"]
rule_codes = {item["code"] for item in rules["rule_bindings"]}
required = {"OvertrainingRisk", "WeeklyMileageIncreaseReview", "PolarizedHighIntensityReview", "CompromisedRecovery", "PossibleExerciseRelatedFatigueReview", "PostRaceRecoveryReview", "HardEasySequenceReview"}
if not required <= rule_codes:
    raise ValueError(f"Ontology coaching bindings missing: {required - rule_codes}")
encoded_rules = json.dumps(rules, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
OUTPUT.write_text(TEMPLATE.read_text().replace("/* __DATA__ */", encoded).replace("/* __RULES__ */", encoded_rules), encoding="utf-8")
print(f"Built {OUTPUT} from {1 + len(args.additional_db)} DuckDB source(s); {len(payload['athletes'])} athletes, {len(payload['runs'])} running sessions")
