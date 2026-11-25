"""Build matching, fully fictional StarRocks and DuckDB warehouse fixtures."""

from __future__ import annotations

from datetime import date as Date, timedelta
from pathlib import Path
import copy
import json
import shutil
import subprocess
import yaml
import duckdb

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "warehouse"
MODEL = yaml.safe_load((ROOT / "fitness_analysis.starrocks.yaml").read_text())
DATASETS = MODEL["datasets"]
TABLES = {d["name"]: d for d in DATASETS if d["name"] != "weekly_running_distance" and not str(d.get("source", "")).lstrip().upper().startswith("SELECT")}

# The duplicate source record below must not double count the same training load.
for metric in MODEL["metrics"]:
    if metric["name"] == "coros_training_load":
        metric["expression"]["dialects"][0]["expression"] = "SUM(CASE WHEN activity.source = 'coros' AND activity.dedup_status = 'canonical' THEN activity.training_load END)"
        break
(ROOT / "fitness_analysis.starrocks.yaml").write_text(yaml.safe_dump(MODEL, allow_unicode=True, sort_keys=False, width=110))

DATE_COLS = {"event_date", "activity_date", "observation_date", "local_date", "wake_date", "target_date", "scheduled_date", "review_date", "window_start_date", "window_end_date", "load_date", "sleep_wake_date", "hrv_wake_date", "rhr_date", "source_date", "data_watermark_date", "evidence_date"}
TIME_COLS = {"started_at_local", "observed_at_utc", "valid_from_utc", "valid_to_utc", "measured_at_utc", "effective_from_utc", "main_start_local", "main_end_local", "created_at_utc", "evaluated_at_utc", "approved_at_utc", "match_reviewed_at_utc", "decided_at_utc"}
BOOL_COLS = {"is_official_race", "comparison_conditions_verified", "event_rule_season_verified", "is_canonical", "lower_inclusive", "upper_inclusive"}
INT_COLS = {"goal_version", "plan_version", "target_duration_min", "target_pace_fast_s_per_km", "target_pace_slow_s_per_km", "target_hr_low_bpm", "target_hr_high_bpm", "assessment_version", "valid_prior_days", "sleep_valid_days_7", "rhr_valid_days_7", "sleep_valid_days_42", "baseline_days", "min_valid_days", "analysis_revision", "segment_ordinal", "run_index", "station_index", "lap_ordinal", "zone_index", "watch_elapsed_s", "official_finish_s", "official_penalty_s", "workout_duration_s", "elapsed_duration_s", "distance_m", "duration_s", "measured_distance_m", "planned_distance_m", "pace_time_s", "pace_distance_m", "training_load", "calories_kcal", "short_term_load", "long_term_load", "daily_sleep_min", "main_sleep_min", "main_period_min", "nap_sleep_min", "awake_min", "awake_count", "rhr_bpm", "avg_hr_bpm", "avg_cadence_spm", "avg_power_w", "avg_pace_s_per_km", "reported_pace_s_per_km", "measured_pace_s_per_km", "rule_reference_pace_s_per_km", "reference_distance_m", "watch_station_time_s", "official_station_finish_s", "repetitions", "prescribed_repetitions", "lower_inclusive_bpm", "upper_exclusive_bpm", "fast_boundary_s_per_km", "slow_boundary_s_per_km", "estimated_full_recovery_h", "hr_weight_s", "hr_sample_coverage_s", "cadence_weight_s", "cadence_sample_coverage_s"}


def row(**values):
    return values


R = {name: [] for name in TABLES}
R["athlete"] = [row(athlete_id=f"demo_{n:02d}", gender_code=g, timezone_name="UTC") for n, g in [(1, "F"), (2, "M"), (3, "F")]]
R["athlete_goal"] = [
    row(athlete_id="demo_01", goal_id="synthetic_run_consistency", goal_version=1, goal_type="running_consistency", title="Run regularly", status="superseded", created_at_utc="2026-04-01 09:00:00"),
    row(athlete_id="demo_01", goal_id="synthetic_run_consistency", goal_version=2, goal_type="running_consistency", title="Build a consistent running habit", status="active", created_at_utc="2026-04-08 09:00:00"),
    row(athlete_id="demo_01", goal_id="synthetic_sleep", goal_version=1, goal_type="sleep", title="Improve sleep consistency", status="active", created_at_utc="2026-04-10 09:00:00"),
    row(athlete_id="demo_02", goal_id="synthetic_race", goal_version=1, goal_type="race", title="Prepare for a 10K", status="active", created_at_utc="2026-04-05 09:00:00"),
]
R["action_plan"] = [
    row(athlete_id="demo_01", plan_id="synthetic_running_plan", plan_version=1, goal_id="synthetic_run_consistency", goal_version=1, title="Two running days per week", plan_summary="A human-approved plan direction for the initial running-consistency goal; scheduled actions are modeled separately.", status="superseded", approval_status="approved", created_at_utc="2026-04-01 10:00:00", approved_at_utc="2026-04-02 09:00:00", revision_reason="Initial plan"),
    row(athlete_id="demo_01", plan_id="synthetic_running_plan", plan_version=2, goal_id="synthetic_run_consistency", goal_version=2, title="Review three running days per week", plan_summary="Draft revision after the goal target changed; no training schedule is applied until human approval.", status="draft", approval_status="pending", created_at_utc="2026-04-08 10:00:00", revision_reason="Goal target changed from two to three run days"),
    row(athlete_id="demo_01", plan_id="synthetic_sleep_plan", plan_version=1, goal_id="synthetic_sleep", goal_version=1, title="Review sleep routine", plan_summary="Draft sleep-focused plan direction awaiting sufficient evidence and human approval.", status="draft", approval_status="pending", created_at_utc="2026-04-10 10:00:00", revision_reason="Initial plan"),
    row(athlete_id="demo_02", plan_id="synthetic_race_plan", plan_version=1, goal_id="synthetic_race", goal_version=1, title="Review 10K preparation", plan_summary="Draft race preparation direction; specific sessions are not yet scheduled.", status="draft", approval_status="pending", created_at_utc="2026-04-05 10:00:00", revision_reason="Initial plan"),
]
R["coach_review"] = [row(athlete_id="demo_01", review_id="review_20260421", goal_id="synthetic_run_consistency", goal_version=2, plan_id="synthetic_running_plan", plan_version=2, review_date="2026-04-21", window_start_date="2026-04-13", window_end_date="2026-04-19", data_watermark_date="2026-04-20", rule_version="coach_v1", status="completed", summary="Review the updated three-day running goal against the available week; keep plan changes pending human approval.", next_step_text="You kept the sessions that are recorded this week. Let's review the next easy run against your three-day goal before approving a plan change; keep the effort comfortable while we check the missing recovery context.", created_at_utc="2026-04-21 09:00:00")]
R["coach_review_finding"] = [
    row(athlete_id="demo_01", review_id="review_20260421", finding_id="run_days", rule_code="GoalProgressReview", status="below_target", observed_value=2, baseline_value=3, unit="days/week", evidence_date="2026-04-19", source_dataset="goal_progress_assessment", source_record_id="synthetic_run_consistency_v2_weekly_run_days_2026-04-21", evidence_status="sufficient", summary="Two recorded run days against a three-day weekly target."),
    row(athlete_id="demo_01", review_id="review_20260421", finding_id="sleep_context", rule_code="CompromisedRecovery", status="insufficient_evidence", evidence_date="2026-04-21", source_dataset="recovery_state", evidence_status="insufficient_baseline", summary="Sleep and recovery history is too short for a reliable baseline."),
]
R["coach_review_proposal"] = [row(athlete_id="demo_01", review_id="review_20260421", proposal_id="easy_run_review", plan_id="synthetic_running_plan", plan_version=2, action_id="run_20260419", proposed_change="Review the next easy-run duration before approving the revised plan.", decision_status="pending", decided_at_utc=None)]
R["planned_action"] = [
    row(athlete_id="demo_01", plan_id="synthetic_running_plan", plan_version=1, action_id="run_20260406", scheduled_date="2026-04-06", action_kind="run", title="Easy run", target_duration_min=40, planning_status="approved", completion_status="verified_completed", verified_event_id="evt_101", match_method="manual_verified", match_reviewed_at_utc="2026-04-07 09:00:00", source="fictional_manual_plan"),
    row(athlete_id="demo_01", plan_id="synthetic_running_plan", plan_version=1, action_id="run_20260409", scheduled_date="2026-04-09", action_kind="run", title="Steady run", target_duration_min=45, planning_status="approved", completion_status="candidate_only", candidate_event_id="evt_102", match_method="date_sport_candidate", source="fictional_manual_plan"),
    row(athlete_id="demo_01", plan_id="synthetic_running_plan", plan_version=2, action_id="run_20260413", scheduled_date="2026-04-13", action_kind="run", title="Proposed easy run", target_duration_min=35, planning_status="proposed", completion_status="not_assessed", source="fictional_manual_plan"),
    row(athlete_id="demo_01", plan_id="synthetic_running_plan", plan_version=2, action_id="rest_20260416", scheduled_date="2026-04-16", action_kind="rest", title="Proposed rest day", planning_status="proposed", completion_status="not_assessed", source="fictional_manual_plan"),
    row(athlete_id="demo_01", plan_id="synthetic_running_plan", plan_version=2, action_id="run_20260419", scheduled_date="2026-04-19", action_kind="run", title="Proposed longer run", target_duration_min=55, planning_status="proposed", completion_status="not_assessed", source="fictional_manual_plan"),
    row(athlete_id="demo_01", plan_id="synthetic_sleep_plan", plan_version=1, action_id="sleep_20260420", scheduled_date="2026-04-20", action_kind="sleep_routine", title="Proposed consistent bedtime", planning_status="proposed", completion_status="not_assessed", source="fictional_manual_plan"),
    row(athlete_id="demo_02", plan_id="synthetic_race_plan", plan_version=1, action_id="run_20260422", scheduled_date="2026-04-22", action_kind="run", title="Proposed easy 10K preparation run", target_duration_min=30, planning_status="proposed", completion_status="not_assessed", source="fictional_manual_plan"),
]
R["goal_criterion"] = [
    row(athlete_id="demo_01", goal_id="synthetic_run_consistency", goal_version=1, criterion_id="weekly_run_days", criterion_kind="running_frequency", metric_name="run_day_count", comparison_operator=">=", target_value=2, target_unit="days/week", aggregation_window="calendar_week", evidence_policy="standalone_runs_only", created_at_utc="2026-04-01 09:00:00"),
    row(athlete_id="demo_01", goal_id="synthetic_run_consistency", goal_version=2, criterion_id="weekly_run_days", criterion_kind="running_frequency", metric_name="run_day_count", comparison_operator=">=", target_value=3, target_unit="days/week", aggregation_window="calendar_week", evidence_policy="standalone_runs_only", created_at_utc="2026-04-08 09:00:00"),
    row(athlete_id="demo_01", goal_id="synthetic_sleep", goal_version=1, criterion_id="main_sleep", criterion_kind="sleep_duration", metric_name="avg_main_sleep_minutes", comparison_operator=">=", target_value=420, target_unit="minutes", aggregation_window="rolling_7_wake_days", evidence_policy="minimum_5_valid_days", created_at_utc="2026-04-10 09:00:00"),
    row(athlete_id="demo_02", goal_id="synthetic_race", goal_version=1, criterion_id="ten_k_time", criterion_kind="race_time", metric_name="official_10k_net_time_s", comparison_operator="<=", target_value=3000, target_unit="seconds", aggregation_window="official_10k_event", evidence_policy="same_distance_official_net_time", target_date="2026-06-01", created_at_utc="2026-04-05 09:00:00"),
]
COROS_RECOVERY_SOURCE = "https://support.coros.com/hc/en-us/articles/360061452651-COROS-Fitness-Metrics-Explained"
COROS_LOAD_SOURCE = "https://support.coros.com/hc/en-us/articles/26485283220884-EvoLab"
def recovery_rule(code, kind, metric, low, high, low_closed, high_closed, label, meaning, origin, url=None, days=None, min_days=None):
    return row(rule_id=code, rule_kind=kind, metric_code=metric, lower_bound=low, upper_bound=high,
               lower_inclusive=low_closed, upper_inclusive=high_closed, label=label, meaning=meaning,
               rule_origin=origin, source_url=url, baseline_days=days, min_valid_days=min_days)
R["recovery_rule"] = [
    recovery_rule("coros_recovery_exhausted", "provider_band", "recovery_pct", 0, 20, True, False, "Exhausted", "Rest is recommended by COROS.", "coros", COROS_RECOVERY_SOURCE),
    recovery_rule("coros_recovery_fatigued", "provider_band", "recovery_pct", 20, 70, True, False, "Fatigued", "Provider-estimated recovery is low.", "coros", COROS_RECOVERY_SOURCE),
    recovery_rule("coros_recovery_normal", "provider_band", "recovery_pct", 70, 90, True, False, "Normal", "Provider-estimated recovery is normal.", "coros", COROS_RECOVERY_SOURCE),
    recovery_rule("coros_recovery_fresh", "provider_band", "recovery_pct", 90, 100, True, True, "Fresh", "Provider labels this range fresh.", "coros", COROS_RECOVERY_SOURCE),
    recovery_rule("coros_load_decreasing", "provider_band", "load_ratio", 0, 0.5, True, False, "Decreasing", "Low recent load relative to base fitness.", "coros", COROS_LOAD_SOURCE),
    recovery_rule("coros_load_performance", "provider_band", "load_ratio", 0.5, 0.8, True, False, "Resuming or Performance", "May be appropriate during a taper; context matters.", "coros", COROS_LOAD_SOURCE),
    recovery_rule("coros_load_maintaining", "provider_band", "load_ratio", 0.8, 1.0, True, False, "Maintaining", "Moderate recent load relative to base fitness.", "coros", COROS_LOAD_SOURCE),
    recovery_rule("coros_load_optimized", "provider_band", "load_ratio", 1.0, 1.5, True, False, "Optimized", "Provider describes productive training in this range.", "coros", COROS_LOAD_SOURCE),
    recovery_rule("coros_load_excessive", "provider_band", "load_ratio", 1.5, None, True, False, "Excessive", "Recent load may be excessive; review recovery.", "coros", COROS_LOAD_SOURCE),
    recovery_rule("personal_load_high", "personal_signal", "load_ratio", 1.5, None, False, False, "High load review", "Review the next session; not an overtraining diagnosis.", "user_configured"),
    recovery_rule("personal_load_low", "personal_signal", "load_ratio", None, 0.8, False, False, "Low load review", "Review goal and taper context; not automatically ineffective training.", "user_configured"),
    recovery_rule("personal_sleep_42d_low", "personal_signal", "sleep_42d_delta_pct", None, -10, False, False, "Long-term sleep decrease", "Sleep duration differs from the prior 42-day mean; quality is not inferred.", "user_configured", days=42, min_days=28),
    recovery_rule("personal_sleep_42d_high", "personal_signal", "sleep_42d_delta_pct", 10, None, False, False, "Long-term sleep increase", "Sleep duration differs from the prior 42-day mean; quality is not inferred.", "user_configured", days=42, min_days=28),
    recovery_rule("personal_sleep_7d_drop", "personal_signal", "sleep_7d_delta_pct", None, -10, False, False, "Recent sleep decrease", "A recent sleep-shortening signal for fatigue review.", "user_configured", days=7, min_days=5),
    recovery_rule("personal_rhr_7d_rise", "personal_signal", "rhr_7d_delta_pct", 10, None, False, False, "Recent resting-HR rise", "A possible fatigue-related signal requiring context.", "user_configured", days=7, min_days=5),
]

EVENTS = [
    ("demo_01", "evt_101", "2026-04-06", "running", "easy", False, None, None, 2380, None),
    ("demo_01", "evt_102", "2026-04-09", "running", "tempo", False, None, None, 2640, None),
    ("demo_01", "evt_103", "2026-04-13", "running", "long", False, None, None, 3900, None),
    ("demo_01", "evt_104", "2026-04-19", "running", "race", True, "Fictional Harbor 10K", "10km", 3210, 3190),
    ("demo_02", "evt_201", "2026-04-10", "running", "easy", False, None, None, 2700, None),
    ("demo_03", "evt_301", "2026-04-11", "hyrox", "race", True, "Fictional Indoor Team Race", "hyrox_doubles", 7200, 7100),
]
for athlete, event, date, sport, intent, official, title, fmt, watch, finish in EVENTS:
    R["workout_event"].append(row(athlete_id=athlete, workout_event_id=event, event_date=date, started_at_local=date+" 07:00:00", sport_code=sport, session_intent=intent, is_official_race=official, event_name=title, race_format_code=fmt, participation_mode="team" if sport == "hyrox" else "solo", watch_elapsed_s=watch, official_finish_s=finish, official_penalty_s=0))

RUNS = [
    ("demo_01", "evt_101", "2026-04-06", 6000, 2380, 143, 166, 178, 90),
    ("demo_01", "evt_102", "2026-04-09", 7000, 2640, 158, 172, 214, 124),
    ("demo_01", "evt_103", "2026-04-13", 10000, 3900, 147, 168, 192, 150),
    ("demo_01", "evt_104", "2026-04-19", 10000, 3210, 164, 176, 235, 202),
    ("demo_02", "evt_201", "2026-04-10", 8000, 2700, 152, 174, 228, 112),
]
FOCUS_BY_EVENT = {
    "evt_101": "Base",
    "evt_102": "Tempo",
    "evt_103": "Base",
    "evt_104": "Threshold",
    "evt_201": "Easy",
}
for i, (athlete, event, date, metres, seconds, hr, cadence, power, load) in enumerate(RUNS, 1):
    R["activity"].append(row(athlete_id=athlete, activity_id=f"act_{i:03d}", activity_date=date, sport_code="running", workout_event_id=event, source="coros", source_activity_id=f"synthetic_{i}", workout_duration_s=seconds, elapsed_duration_s=seconds, distance_m=metres, avg_hr_bpm=hr, avg_cadence_spm=cadence, avg_power_w=power, training_load=load, training_focus=FOCUS_BY_EVENT[event], dedup_status="canonical"))
    R["running_observation"].append(row(athlete_id=athlete, workout_event_id=event, analysis_revision=1, segment_ordinal=1, segment_kind="run", run_context="standalone", phase_kind="main", run_environment="outdoor", event_date=date, observation_date=date, duration_basis="watch_moving", distance_status="measured", pace_basis="measured", duration_s=seconds, measured_distance_m=metres, pace_time_s=seconds, pace_distance_m=metres, avg_hr_bpm=hr, hr_weighted_sum_bpm_s=hr*seconds, hr_weight_s=seconds, hr_sample_coverage_s=seconds, avg_cadence_spm=cadence, cadence_weighted_sum_spm_s=cadence*seconds, cadence_weight_s=seconds, cadence_sample_coverage_s=seconds, sport_code="running", session_intent=next(e[4] for e in EVENTS if e[1]==event), is_official_race=(event=="evt_104"), event_name="Fictional Harbor 10K" if event=="evt_104" else None, race_format_code="10km" if event=="evt_104" else None, participation_mode="solo"))
    R["activity_segment"].append(row(athlete_id=athlete, activity_id=f"act_{i:03d}", lap_ordinal=1, segment_kind="run", is_canonical=True, duration_s=seconds, distance_m=metres, avg_pace_s_per_km=seconds*1000//metres, avg_hr_bpm=hr, avg_cadence_spm=cadence, avg_power_w=power))

# A second platform copy exists so deduplication can be demonstrated. It is not a canonical run.
R["activity"].append(row(athlete_id="demo_01", activity_id="act_copy", activity_date="2026-04-06", sport_code="running", workout_event_id="evt_101", source="fictional_import", source_activity_id="synthetic_copy", workout_duration_s=2380, elapsed_duration_s=2380, distance_m=6000, avg_hr_bpm=143, avg_cadence_spm=166, avg_power_w=178, training_load=90, dedup_status="duplicate"))
R["activity"].append(row(athlete_id="demo_03", activity_id="act_301", activity_date="2026-04-11", sport_code="hyrox", workout_event_id="evt_301", source="coros", source_activity_id="synthetic_hyrox", workout_duration_s=7200, elapsed_duration_s=7200, training_load=190, dedup_status="canonical"))

for i, sec in enumerate([344, 350, 356, 361, 369, 373, 381, 386], 1):
    R["running_rule_reference"].append(row(athlete_id="demo_03", workout_event_id="evt_301", analysis_revision=1, segment_ordinal=i*2-1, run_index=i, segment_kind="run", event_date="2026-04-11", duration_s=sec, reference_distance_m=1000, reference_distance_basis="fictional_rule", rule_reference_pace_s_per_km=sec, rule_id="example_v1", rule_match_status="matched", event_rule_season_verified=True, event_name="Fictional Indoor Team Race", race_format_code="hyrox_doubles", participation_mode="team", is_official_race=True, sport_code="hyrox", session_intent="race"))
for i, (code, seconds) in enumerate([("ski", 320), ("sled", 480)], 1):
    R["hyrox_station"].append(row(athlete_id="demo_03", workout_event_id="evt_301", analysis_revision=1, segment_ordinal=i*2, station_index=i, segment_kind="station", exercise_code=code, exercise_name_zh=code, event_date="2026-04-11", duration_s=seconds, watch_station_time_s=seconds, comparison_conditions_verified=False, sport_code="hyrox", session_intent="race", is_official_race=True, event_name="Fictional Indoor Team Race", race_format_code="hyrox_doubles", participation_mode="team"))

for n, date in enumerate(["2026-04-19", "2026-04-20", "2026-04-21"], 1):
    R["daily_training_load"].append(row(athlete_id="demo_01", source="fictional_watch", local_date=date, short_term_load=370-25*n, long_term_load=300, load_ratio=round((370-25*n)/300, 3), provider_status="Balanced", observed_at_utc=date+" 06:00:00", source_snapshot_id=f"load_{n}"))
    R["daily_sleep"].append(row(athlete_id="demo_01", source="fictional_watch", wake_date=date, data_status="present", sleep_score=78+2*n, daily_sleep_min=420+10*n, main_sleep_min=410+10*n, observed_at_utc=date+" 06:00:00", source_snapshot_id=f"sleep_{n}"))
    R["daily_resting_hr"].append(row(athlete_id="demo_01", source="fictional_watch", local_date=date, rhr_bpm=57-n, data_status="present", observed_at_utc=date+" 06:00:00", source_snapshot_id=f"rhr_{n}"))
    R["daily_hrv"].append(row(athlete_id="demo_01", source="fictional_watch", wake_date=date, hrv_avg_ms=[48, 39, 47][n-1], normal_low_ms=42, normal_high_ms=55, baseline_ms=48, provider_evaluation="below_normal" if n == 2 else "normal", data_status="present", observed_at_utc=date+" 06:00:00", source_snapshot_id=f"hrv_{n}"))
R["recovery_observation"] = [row(athlete_id="demo_01", observation_id="recovery_1", source="fictional_watch", observed_at_utc="2026-04-21 07:00:00", recovery_pct=76, recovery_level="normal", estimated_full_recovery_h=8, source_snapshot_id="recovery_fixture")]

# A review is a saved interpretation of dated source records, never a replacement for
# the provider's recovery percentage. The three-day fixture cannot satisfy the
# five-prior-day and 28-prior-day coverage gates, so every composite review is
# explicitly marked insufficient_evidence.
for load in R["daily_training_load"]:
    athlete, source, date = load["athlete_id"], load["source"], load["local_date"]
    assessment_id = f"recovery_review_{athlete}_{date}"
    sleep = next((x for x in R["daily_sleep"] if (x["athlete_id"], x["source"], x["wake_date"]) == (athlete, source, date)), None)
    rhr = next((x for x in R["daily_resting_hr"] if (x["athlete_id"], x["source"], x["local_date"]) == (athlete, source, date)), None)
    provider = next((x for x in R["recovery_observation"] if x["athlete_id"] == athlete and x["source"] == source and x["observed_at_utc"][:10] == date), None)
    week_start = (Date.fromisoformat(date) - timedelta(days=7)).isoformat()
    long_start = (Date.fromisoformat(date) - timedelta(days=42)).isoformat()
    prior_sleep_7 = [x for x in R["daily_sleep"] if x["athlete_id"] == athlete and x["source"] == source and week_start <= x["wake_date"] < date and x.get("main_sleep_min") is not None]
    prior_sleep_42 = [x for x in R["daily_sleep"] if x["athlete_id"] == athlete and x["source"] == source and long_start <= x["wake_date"] < date and x.get("main_sleep_min") is not None]
    prior_rhr_7 = [x for x in R["daily_resting_hr"] if x["athlete_id"] == athlete and x["source"] == source and week_start <= x["local_date"] < date and x.get("rhr_bpm") is not None]
    R["recovery_state"].append(row(athlete_id=athlete, assessment_id=assessment_id, assessment_version=1, review_date=date, source=source, status="insufficient_evidence", method_version="recovery_review_v1", evaluated_at_utc=date + " 08:00:00", sleep_valid_days_7=len(prior_sleep_7), rhr_valid_days_7=len(prior_rhr_7), sleep_valid_days_42=len(prior_sleep_42), load_source=source, load_date=date, sleep_source=source if sleep else None, sleep_wake_date=date if sleep else None, rhr_source=source if rhr else None, rhr_date=date if rhr else None, provider_observation_id=provider["observation_id"] if provider else None))
    load_band = next(x for x in R["recovery_rule"] if x["rule_kind"] == "provider_band" and x["metric_code"] == "load_ratio" and (x["lower_bound"] is None or load["load_ratio"] >= x["lower_bound"]) and (x["upper_bound"] is None or load["load_ratio"] < x["upper_bound"]))
    evidence = [row(athlete_id=athlete, assessment_id=assessment_id, assessment_version=1, evidence_id="load_ratio", source_dataset="daily_training_load", source_record_id=f"{source}:{date}", source_date=date, metric_code="load_ratio", observed_value=load["load_ratio"], unit="ratio", rule_id=load_band["rule_id"], evaluation_status="provider_band_only", valid_prior_days=None, baseline_days=None)]
    if sleep:
        evidence.append(row(athlete_id=athlete, assessment_id=assessment_id, assessment_version=1, evidence_id="sleep_7d", source_dataset="daily_sleep", source_record_id=f"{source}:{date}", source_date=date, metric_code="main_sleep_min", observed_value=sleep["main_sleep_min"], unit="minutes", rule_id="personal_sleep_7d_drop", evaluation_status="insufficient_baseline", valid_prior_days=len(prior_sleep_7), baseline_days=7))
        evidence.append(row(athlete_id=athlete, assessment_id=assessment_id, assessment_version=1, evidence_id="sleep_42d", source_dataset="daily_sleep", source_record_id=f"{source}:{date}", source_date=date, metric_code="main_sleep_min", observed_value=sleep["main_sleep_min"], unit="minutes", rule_id="personal_sleep_42d_low", evaluation_status="insufficient_baseline", valid_prior_days=len(prior_sleep_42), baseline_days=42))
    if rhr:
        evidence.append(row(athlete_id=athlete, assessment_id=assessment_id, assessment_version=1, evidence_id="rhr_7d", source_dataset="daily_resting_hr", source_record_id=f"{source}:{date}", source_date=date, metric_code="rhr_bpm", observed_value=rhr["rhr_bpm"], unit="bpm", rule_id="personal_rhr_7d_rise", evaluation_status="insufficient_baseline", valid_prior_days=len(prior_rhr_7), baseline_days=7))
    if provider:
        recovery_band = next(x for x in R["recovery_rule"] if x["rule_kind"] == "provider_band" and x["metric_code"] == "recovery_pct" and provider["recovery_pct"] >= x["lower_bound"] and (x["upper_bound"] is None or provider["recovery_pct"] < x["upper_bound"] or (provider["recovery_pct"] == x["upper_bound"] and x["upper_inclusive"])))
        evidence.append(row(athlete_id=athlete, assessment_id=assessment_id, assessment_version=1, evidence_id="provider_recovery", source_dataset="recovery_observation", source_record_id=provider["observation_id"], source_date=date, metric_code="recovery_pct", observed_value=provider["recovery_pct"], unit="percent", rule_id=recovery_band["rule_id"], evaluation_status="provider_band_only", valid_prior_days=None, baseline_days=None))
    R["recovery_evidence"].extend(evidence)
for i, lo, hi in [(1, 0, 121), (2, 121, 141), (3, 141, 158), (4, 158, 174), (5, 174, 230)]:
    R["running_hr_zone"].append(row(athlete_id="demo_01", zone_scheme_id="fictional_hr_v1", zone_index=i, sport_code="running", scheme_method="fictional", valid_from_utc="2026-01-01 00:00:00", lower_inclusive_bpm=lo, upper_exclusive_bpm=hi))
for i, fast, slow in [(1, 430, 600), (2, 380, 430), (3, 350, 380), (4, 320, 350), (5, 250, 320)]:
    R["running_pace_zone"].append(row(athlete_id="demo_01", zone_scheme_id="fictional_pace_v1", zone_index=i, sport_code="running", scheme_method="fictional", valid_from_utc="2026-01-01 00:00:00", fast_boundary_s_per_km=fast, slow_boundary_s_per_km=slow))
for code, value, unit in [("vo2max_running", 47, "ml/kg/min"), ("threshold_pace_s_per_km", 350, "s/km"), ("threshold_hr_bpm", 169, "bpm")]:
    R["latest_fitness_measurement"].append(row(athlete_id="demo_01", measurement_id="fictional_"+code, metric_code=code, metric_value=value, unit=unit, measured_at_utc="2026-04-15 10:00:00", effective_from_utc="2026-04-15 10:00:00", observed_at_utc="2026-04-15 10:00:00", time_quality="exact", source="fictional_watch"))

# Saved capability reviews cite the exact fictional source records used. A single
# device/profile snapshot is a baseline, and mixed workouts do not prove a trend.
CAPABILITY_REVIEWS = [
    ("aerobic_capacity", "baseline_only", "contextual", "One device VO2max estimate; no comparable history."),
    ("threshold_endurance", "baseline_only", "contextual", "One dated threshold estimate; no comparable history."),
    ("running_pace_capacity", "baseline_only", "contextual", "One pace-zone scheme; faster future boundaries require the same method and observed-run corroboration."),
    ("aerobic_endurance", "descriptive_only", "exploratory", "Runs have different intents; pace and heart rate cannot establish a controlled trend."),
    ("running_mechanics", "descriptive_only", "descriptive", "Cadence differs by pace and workout purpose; no economy score is inferred."),
    ("race_performance", "observed_outcome", "observed", "One official 10K net result; no same-distance comparison yet."),
]
for kind, status, confidence, rationale in CAPABILITY_REVIEWS:
    R["capability_assessment"].append(row(athlete_id="demo_01", assessment_id=f"capability_{kind}_20260421", assessment_version=1, capability_type=kind, review_date="2026-04-21", status=status, confidence=confidence, method_version="capability_review_v1", rationale=rationale, created_at_utc="2026-04-21 09:00:00"))

def capability_evidence(kind, evidence_id, evidence_kind, metric_name, source_dataset, source_record_id, source_date, value, unit, comparability_status):
    confidence = next(x[2] for x in CAPABILITY_REVIEWS if x[0] == kind)
    R["capability_evidence"].append(row(athlete_id="demo_01", assessment_id=f"capability_{kind}_20260421", assessment_version=1, evidence_id=evidence_id, evidence_kind=evidence_kind, metric_name=metric_name, source_dataset=source_dataset, source_record_id=source_record_id, source_date=source_date, observed_value=value, unit=unit, comparability_status=comparability_status, confidence=confidence))

for code, kind, metric_name in [("vo2max_running", "aerobic_capacity", "latest_vo2max_running"), ("threshold_pace_s_per_km", "threshold_endurance", "latest_threshold_pace_s_per_km"), ("threshold_hr_bpm", "threshold_endurance", "latest_threshold_hr_bpm")]:
    measurement = next(x for x in R["latest_fitness_measurement"] if x["metric_code"] == code)
    capability_evidence(kind, code, "provider_estimate", metric_name, "latest_fitness_measurement", measurement["measurement_id"], measurement["measured_at_utc"][:10], measurement["metric_value"], measurement["unit"], "single_snapshot")
for zone in R["running_pace_zone"]:
    for edge, column in [("fast", "fast_boundary_s_per_km"), ("slow", "slow_boundary_s_per_km")]:
        capability_evidence("running_pace_capacity", f"zone_{zone['zone_index']}_{edge}", "pace_zone_boundary", None, "running_pace_zone", f"{zone['zone_scheme_id']}:{zone['zone_index']}:{edge}", zone["valid_from_utc"][:10], zone[column], "s/km", "single_scheme_version")
for run in R["running_observation"]:
    if run["athlete_id"] != "demo_01" or run["run_context"] != "standalone": continue
    event, day = run["workout_event_id"], run["event_date"]
    pace = 1000.0 * run["pace_time_s"] / run["pace_distance_m"]
    capability_evidence("aerobic_endurance", f"{event}_pace", "observed_run", "measured_pace_s_per_km", "running_observation", f"{event}:1:1", day, pace, "s/km", "mixed_session_intents")
    capability_evidence("aerobic_endurance", f"{event}_heart_rate", "observed_run", "weighted_avg_hr_bpm", "running_observation", f"{event}:1:1", day, run["avg_hr_bpm"], "bpm", "mixed_session_intents")
    capability_evidence("running_mechanics", f"{event}_cadence", "observed_run", "weighted_avg_cadence_spm", "running_observation", f"{event}:1:1", day, run["avg_cadence_spm"], "spm", "mixed_pace_and_intent")
race = next(x for x in R["workout_event"] if x["athlete_id"] == "demo_01" and x["race_format_code"] == "10km")
capability_evidence("race_performance", "official_10k_net_time", "official_race", "official_10k_net_time_s", "workout_event", race["workout_event_id"], race["event_date"], race["official_finish_s"], "seconds", "single_race")


# Persist one review per criterion and version. The 10K and sleep examples
# deliberately retain insufficient evidence instead of inventing a result.
GOAL_PROGRESS = [
    ("demo_01", "synthetic_run_consistency", 1, "weekly_run_days", "2026-04-12", "2026-04-06", "2026-04-12", "achieved", 2, 0, "Two distinct standalone run days in the completed calendar week."),
    ("demo_01", "synthetic_run_consistency", 2, "weekly_run_days", "2026-04-21", "2026-04-13", "2026-04-19", "needs_review", 2, -1, "Two distinct standalone run days in the completed calendar week; target is three."),
    ("demo_01", "synthetic_sleep", 1, "main_sleep", "2026-04-21", "2026-04-15", "2026-04-21", "insufficient_evidence", None, None, "Only three valid wake days; policy requires five before evaluating the seven-day mean."),
    ("demo_02", "synthetic_race", 1, "ten_k_time", "2026-04-21", None, "2026-04-21", "insufficient_evidence", None, None, "No same-athlete official 10K net result; another athlete's race is not evidence."),
]
for athlete, goal, version, criterion, review, start, end, status, observed, difference, rationale in GOAL_PROGRESS:
    aid = f"{goal}_v{version}_{criterion}_{review}"
    R["goal_progress_assessment"].append(row(athlete_id=athlete, assessment_id=aid, assessment_version=1, goal_id=goal, goal_version=version, criterion_id=criterion, review_date=review, window_start_date=start, window_end_date=end, status=status, observed_value=observed, difference_value=difference, difference_unit="days/week" if criterion == "weekly_run_days" else None, comparison_basis="distinct_standalone_run_days_in_completed_calendar_week" if criterion == "weekly_run_days" else ("rolling_7_wake_days_minimum_5" if criterion == "main_sleep" else "same_athlete_official_10k_net_time"), method_version="goal_progress_v1", rationale=rationale, evaluated_at_utc=review+" 09:00:00"))
    if criterion == "weekly_run_days":
        for event in [x for x in R["workout_event"] if x["athlete_id"] == athlete and x["sport_code"] == "running" and start <= x["event_date"] <= end]:
            R["goal_progress_evidence"].append(row(athlete_id=athlete, assessment_id=aid, assessment_version=1, evidence_id=event["workout_event_id"], source_dataset="workout_event", source_record_id=event["workout_event_id"], source_date=event["event_date"], metric_name="run_day_count", observed_value=1, unit="run_day", quality_status="canonical_standalone", comparison_basis="calendar_week"))
    elif criterion == "main_sleep":
        for sleep in [x for x in R["daily_sleep"] if x["athlete_id"] == athlete and start <= x["wake_date"] <= end]:
            R["goal_progress_evidence"].append(row(athlete_id=athlete, assessment_id=aid, assessment_version=1, evidence_id=sleep["wake_date"], source_dataset="daily_sleep", source_record_id=f"{sleep['source']}:{sleep['wake_date']}", source_date=sleep["wake_date"], metric_name="avg_main_sleep_minutes", observed_value=sleep["main_sleep_min"], unit="minutes", quality_status="present_but_incomplete_window", comparison_basis="wake_date"))

def sqltype(name: str, dialect: str) -> str:
    if name in {"summary", "next_step_text", "proposed_change"}: return "VARCHAR(2048)"
    if name in BOOL_COLS: return "BOOLEAN"
    if name in DATE_COLS: return "DATE"
    if name in TIME_COLS: return "DATETIME" if dialect == "starrocks" else "TIMESTAMP"
    if name in INT_COLS or name.endswith("_sum_bpm_s") or name.endswith("_sum_spm_s"): return "BIGINT"
    if name in {"hrv_avg_ms", "normal_low_ms", "normal_high_ms", "baseline_ms", "load_ratio", "lower_bound", "upper_bound", "sleep_score", "data_source_raw", "deep_pct", "light_pct", "rem_pct", "awake_pct", "recovery_pct", "metric_value", "target_value", "observed_value", "difference_value", "baseline_value", "load_total_kg", "load_per_hand_kg", "target_distance_km", "target_distance_min_km", "target_distance_max_km"}: return "DECIMAL(18,3)"
    return "VARCHAR(255)"


def literal(value):
    if value is None: return "NULL"
    if isinstance(value, bool): return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)): return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def physical(name):
    source_name = TABLES[name]["source"].split(".")[-1]
    return {
        "running_observation": "running_observation_fact",
        "hyrox_station": "hyrox_station_fact",
        "running_rule_reference": "running_rule_reference_fact",
        "latest_fitness_measurement": "fitness_measurement",
    }.get(name, source_name)


def emit(dialect):
    ddl = ["-- Completely fictional athletes and workouts; safe for public demos."]
    if dialect == "starrocks": ddl += ["CREATE DATABASE IF NOT EXISTS fitness_demo;", "USE fitness_demo;"]
    else: ddl += ["CREATE SCHEMA IF NOT EXISTS fitness_demo;", "SET schema 'fitness_demo';"]
    inserts = ["-- Generated from the same fixture definitions as the other engine."]
    if dialect == "starrocks": inserts.append("USE fitness_demo;")
    else: inserts.append("SET schema 'fitness_demo';")
    for name, d in TABLES.items():
        cols = [f["name"] for f in d["fields"]]
        table = physical(name)
        definitions = ",\n  ".join(f"{col} {sqltype(col, dialect)}" for col in cols)
        if dialect == "starrocks":
            key = "athlete_id" if "athlete_id" in cols else cols[0]
            ddl.append(f"CREATE TABLE IF NOT EXISTS {table} (\n  {definitions}\n) ENGINE=OLAP DUPLICATE KEY({key}) DISTRIBUTED BY HASH({key}) BUCKETS 1 PROPERTIES ('replication_num'='1');")
        else:
            ddl.append(f"CREATE TABLE IF NOT EXISTS {table} (\n  {definitions}\n);")
        if d["source"].split(".")[-1].startswith("v_"):
            view = d["source"].split(".")[-1]
            if view == "v_latest_body_measurement":
                projection = ", ".join(cols)
                ddl.append(f"CREATE VIEW {view} AS SELECT {projection} FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY athlete_id, metric_code ORDER BY COALESCE(measured_at_utc, observed_at_utc) DESC, measurement_id DESC) AS recency_rank FROM {table}) ranked WHERE recency_rank = 1;")
            else:
                ddl.append(f"CREATE VIEW {view} AS SELECT * FROM {table};")
        rows = R[name]
        if rows:
            insert_cols = [c for c in cols if any(c in r for r in rows)]
            vals = ",\n  ".join("(" + ", ".join(literal(r.get(c)) for c in insert_cols) + ")" for r in rows)
            inserts.append(f"INSERT INTO {table} ({', '.join(insert_cols)}) VALUES\n  {vals};")
    if dialect == "starrocks":
        ddl.append("CREATE TABLE IF NOT EXISTS activity_import_coverage (athlete_id VARCHAR(255), local_date DATE, status VARCHAR(32)) ENGINE=OLAP DUPLICATE KEY(athlete_id, local_date) DISTRIBUTED BY HASH(athlete_id) BUCKETS 1 PROPERTIES ('replication_num'='1');")
        prior_date = "DATE_SUB(cur.week_start, INTERVAL 7 DAY)"
    else:
        ddl.append("CREATE TABLE IF NOT EXISTS activity_import_coverage (athlete_id VARCHAR(255), local_date DATE, status VARCHAR(32));")
        prior_date = "cur.week_start - INTERVAL 7 DAY"
    ddl.append(f"""CREATE VIEW v_weekly_running_distance AS
WITH complete_weeks AS (
  SELECT athlete_id, DATE_TRUNC('week', local_date) AS week_start
  FROM activity_import_coverage WHERE status = 'verified_complete'
  GROUP BY athlete_id, DATE_TRUNC('week', local_date)
  HAVING COUNT(DISTINCT local_date) = 7
), current_segments AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY athlete_id, workout_event_id, segment_ordinal ORDER BY analysis_revision DESC) AS revision_rank
  FROM v_running_observation
), weekly_runs AS (
  SELECT athlete_id, DATE_TRUNC('week', event_date) AS week_start,
    SUM(measured_distance_m) / 1000.0 AS distance_km
  FROM current_segments
  WHERE revision_rank = 1 AND segment_kind = 'run' AND distance_status = 'measured' AND measured_distance_m > 0
  GROUP BY athlete_id, DATE_TRUNC('week', event_date)
), complete_distance AS (
  SELECT w.athlete_id, w.week_start, COALESCE(r.distance_km, 0) AS distance_km
  FROM complete_weeks w LEFT JOIN weekly_runs r ON w.athlete_id = r.athlete_id AND w.week_start = r.week_start
)
SELECT cur.athlete_id, cur.week_start, cur.distance_km, prior.distance_km AS prior_distance_km,
  cur.distance_km / NULLIF(prior.distance_km, 0) - 1 AS growth_ratio
FROM complete_distance cur JOIN complete_distance prior
  ON cur.athlete_id = prior.athlete_id AND prior.week_start = {prior_date}
WHERE prior.distance_km > 0;""")
    # Fictional seed explicitly covers two complete weeks; real imports must supply their own verified dates.
    inserts.append("INSERT INTO activity_import_coverage (athlete_id, local_date, status) VALUES " + ", ".join(
        f"('demo_01', '{(Date(2026, 4, 6) + timedelta(days=i)).isoformat()}', 'verified_complete')" for i in range(14)) + ";")
    (OUT / f"{dialect}_schema.sql").write_text("\n\n".join(ddl)+"\n")
    (OUT / f"{dialect}_seed.sql").write_text("\n\n".join(inserts)+"\n")


emit("starrocks")
emit("duckdb")
duck = copy.deepcopy(MODEL)
for d in duck["datasets"]:
    for f in d.get("fields", []):
        for x in f.get("expression", {}).get("dialects", []): x["dialect"] = "DUCKDB"
for m in duck["metrics"]:
    for x in m.get("expression", {}).get("dialects", []): x["dialect"] = "DUCKDB"
(ROOT / "fitness_analysis.yaml").write_text(yaml.safe_dump(duck, allow_unicode=True, sort_keys=False, width=110))
# Keep the standalone DOSI projects synchronized with the generated models and
# the editable root ontology. Mappings remain separate, hand-reviewed files.
shutil.copyfile(ROOT / "fitness_analysis.yaml", ROOT / "subject/semantic_models/duckdb/fitness_analysis.yaml")
shutil.copyfile(ROOT / "fitness_analysis.starrocks.yaml", ROOT / "starrocks_project/subject/semantic_models/starrocks/fitness_analysis.yaml")
shutil.copyfile(ROOT / "fitness_ontology.yaml", ROOT / "subject/ontology/fitness.ontology.yaml")
shutil.copyfile(ROOT / "fitness_ontology.starrocks.yaml", ROOT / "starrocks_project/subject/ontology/fitness.ontology.yaml")
lineage_page = ROOT / "lineage.html"
if lineage_page.exists() and shutil.which("dosi"):
    result = subprocess.run(
        ["dosi", "lineage", "dump", "--mapping", str(ROOT / "subject/ontology/fitness.mapping.yaml"), "--format", "json"],
        capture_output=True, text=True, check=True,
    )
    graph = json.dumps(json.loads(result.stdout), ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    page = lineage_page.read_text()
    opening = '<script type="application/json" id="graph">'
    start = page.index(opening) + len(opening)
    end = page.index("</script>", start)
    lineage_page.write_text(page[:start] + graph + page[end:])
db_path = OUT / "running_demo.duckdb"
db_path.unlink(missing_ok=True)
with duckdb.connect(str(db_path), config={"storage_compatibility_version": "v1.5.0"}) as connection:
    connection.execute((OUT / "duckdb_schema.sql").read_text())
    connection.execute((OUT / "duckdb_seed.sql").read_text())
print("Generated two warehouse schemas, identical synthetic rows, a DuckDB model, and the local DuckDB database.")
