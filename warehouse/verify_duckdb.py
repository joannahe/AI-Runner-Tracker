"""Check the synthetic warehouse and execute DOSI-generated SQL in DuckDB."""

from pathlib import Path
import subprocess
import duckdb

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "warehouse" / "running_demo.duckdb"
CONN = duckdb.connect(str(DB), read_only=True)
MAPPING = ROOT / "subject" / "ontology" / "fitness.mapping.yaml"


def one(sql):
    return CONN.execute(sql).fetchone()[0]


def model_metric(name):
    result = subprocess.run(
        ["dosi", "query", "--mapping", str(MAPPING), "--metrics", name, "--dialect", "duckdb"],
        capture_output=True, text=True, check=True,
    )
    return one(result.stdout.strip().splitlines()[-1])


checks = {
    "athletes": ("SELECT COUNT(*) FROM fitness_demo.athlete", 3),
    "saved_coach_reviews": ("SELECT COUNT(*) FROM fitness_demo.coach_review", 1),
    "coach_review_findings": ("SELECT COUNT(*) FROM fitness_demo.coach_review_finding", 2),
    "coach_review_proposals_pending": ("SELECT COUNT(*) FROM fitness_demo.coach_review_proposal WHERE decision_status='pending'", 1),
    "coach_review_goal_version": ("SELECT COUNT(*) FROM fitness_demo.coach_review r JOIN fitness_demo.athlete_goal g ON r.athlete_id=g.athlete_id AND r.goal_id=g.goal_id AND r.goal_version=g.goal_version", 1),
    "coach_review_plan_version": ("SELECT COUNT(*) FROM fitness_demo.coach_review r JOIN fitness_demo.action_plan p ON r.athlete_id=p.athlete_id AND r.plan_id=p.plan_id AND r.plan_version=p.plan_version AND r.goal_id=p.goal_id AND r.goal_version=p.goal_version", 1),
    "coach_finding_evidence": ("SELECT COUNT(*) FROM fitness_demo.coach_review_finding WHERE finding_id='run_days' AND observed_value=2 AND baseline_value=3 AND evidence_status='sufficient'", 1),
    "goal_versions": ("SELECT COUNT(*) FROM fitness_demo.athlete_goal", 4),
    "saved_action_plan_versions": ("SELECT COUNT(*) FROM fitness_demo.action_plan", 4),
    "action_plans_match_goal_versions": ("SELECT COUNT(*) FROM fitness_demo.action_plan p LEFT JOIN fitness_demo.athlete_goal g ON p.athlete_id=g.athlete_id AND p.goal_id=g.goal_id AND p.goal_version=g.goal_version WHERE g.goal_id IS NULL", 0),
    "running_plan_revisions": ("SELECT COUNT(DISTINCT plan_version) FROM fitness_demo.action_plan WHERE athlete_id='demo_01' AND plan_id='synthetic_running_plan'", 2),
    "draft_plans_not_approved": ("SELECT COUNT(*) FROM fitness_demo.action_plan WHERE approval_status='pending' AND approved_at_utc IS NOT NULL", 0),
    "approved_plan_has_timestamp": ("SELECT COUNT(*) FROM fitness_demo.action_plan WHERE approval_status='approved' AND approved_at_utc IS NOT NULL", 1),
    "planned_actions": ("SELECT COUNT(*) FROM fitness_demo.planned_action", 7),
    "actions_match_plan_versions": ("SELECT COUNT(*) FROM fitness_demo.planned_action a LEFT JOIN fitness_demo.action_plan p ON a.athlete_id=p.athlete_id AND a.plan_id=p.plan_id AND a.plan_version=p.plan_version WHERE p.plan_id IS NULL", 0),
    "verified_action_has_actual_session": ("SELECT COUNT(*) FROM fitness_demo.planned_action a JOIN fitness_demo.workout_event e ON a.athlete_id=e.athlete_id AND a.verified_event_id=e.workout_event_id WHERE a.completion_status='verified_completed' AND a.match_method='manual_verified'", 1),
    "candidate_not_claimed_completed": ("SELECT COUNT(*) FROM fitness_demo.planned_action WHERE completion_status='candidate_only' AND candidate_event_id IS NOT NULL AND verified_event_id IS NULL", 1),
    "candidate_points_to_same_athlete": ("SELECT COUNT(*) FROM fitness_demo.planned_action a LEFT JOIN fitness_demo.workout_event e ON a.athlete_id=e.athlete_id AND a.candidate_event_id=e.workout_event_id WHERE a.candidate_event_id IS NOT NULL AND e.workout_event_id IS NULL", 0),
    "no_unverified_fulfillment": ("SELECT COUNT(*) FROM fitness_demo.planned_action WHERE completion_status<>'verified_completed' AND verified_event_id IS NOT NULL", 0),
    "draft_actions_not_marked_done": ("SELECT COUNT(*) FROM fitness_demo.planned_action a JOIN fitness_demo.action_plan p ON a.athlete_id=p.athlete_id AND a.plan_id=p.plan_id AND a.plan_version=p.plan_version WHERE p.approval_status='pending' AND a.completion_status='verified_completed'", 0),
    "goal_criteria": ("SELECT COUNT(*) FROM fitness_demo.goal_criterion", 4),
    "criteria_match_goal_versions": ("SELECT COUNT(*) FROM fitness_demo.goal_criterion c LEFT JOIN fitness_demo.athlete_goal g ON c.athlete_id=g.athlete_id AND c.goal_id=g.goal_id AND c.goal_version=g.goal_version WHERE g.goal_id IS NULL", 0),
    "revised_target_preserved": ("SELECT COUNT(DISTINCT target_value) FROM fitness_demo.goal_criterion WHERE goal_id='synthetic_run_consistency'", 2),
    "concurrent_active_goals": ("SELECT COUNT(*) FROM fitness_demo.athlete_goal WHERE athlete_id = 'demo_01' AND status = 'active'", 2),
    "preserved_goal_revision": ("SELECT COUNT(DISTINCT goal_version) FROM fitness_demo.athlete_goal WHERE athlete_id = 'demo_01' AND goal_id = 'synthetic_run_consistency'", 2),
    "goal_progress_reviews": ("SELECT COUNT(*) FROM fitness_demo.goal_progress_assessment", 4),
    "goal_progress_evidence": ("SELECT COUNT(*) FROM fitness_demo.goal_progress_evidence", 7),
    "goal_progress_criterion_join": ("SELECT COUNT(*) FROM fitness_demo.goal_progress_assessment a LEFT JOIN fitness_demo.goal_criterion c ON a.athlete_id=c.athlete_id AND a.goal_id=c.goal_id AND a.goal_version=c.goal_version AND a.criterion_id=c.criterion_id WHERE c.criterion_id IS NULL", 0),
    "goal_progress_evidence_join": ("SELECT COUNT(*) FROM fitness_demo.goal_progress_evidence e LEFT JOIN fitness_demo.goal_progress_assessment a ON e.athlete_id=a.athlete_id AND e.assessment_id=a.assessment_id AND e.assessment_version=a.assessment_version WHERE a.assessment_id IS NULL", 0),
    "old_weekly_goal_achieved": ("SELECT COUNT(*) FROM fitness_demo.goal_progress_assessment WHERE goal_id='synthetic_run_consistency' AND goal_version=1 AND status='achieved' AND observed_value=2 AND difference_value=0", 1),
    "revised_weekly_goal_gap": ("SELECT COUNT(*) FROM fitness_demo.goal_progress_assessment WHERE goal_id='synthetic_run_consistency' AND goal_version=2 AND status='needs_review' AND observed_value=2 AND difference_value=-1", 1),
    "missing_data_not_scored": ("SELECT COUNT(*) FROM fitness_demo.goal_progress_assessment WHERE status='insufficient_evidence' AND observed_value IS NULL AND difference_value IS NULL", 2),
    "workout_events": ("SELECT COUNT(*) FROM fitness_demo.workout_event", 6),
    "source_activities": ("SELECT COUNT(*) FROM fitness_demo.activity", 7),
    "duplicate_source_records": ("SELECT COUNT(*) FROM fitness_demo.activity WHERE dedup_status = 'duplicate'", 1),
    "running_observations": ("SELECT COUNT(*) FROM fitness_demo.v_running_observation", 5),
    "official_10k_seconds": ("SELECT official_finish_s FROM fitness_demo.workout_event WHERE race_format_code = '10km'", 3190),
    "hyrox_reference_segments": ("SELECT COUNT(*) FROM fitness_demo.v_running_rule_reference", 8),
    "heart_rate_zones": ("SELECT COUNT(*) FROM fitness_demo.athlete_hr_zone", 5),
    "pace_zones": ("SELECT COUNT(*) FROM fitness_demo.athlete_pace_zone", 5),
    "recovery_rules": ("SELECT COUNT(*) FROM fitness_demo.recovery_rule", 15),
    "daily_recovery_reviews": ("SELECT COUNT(*) FROM fitness_demo.recovery_state", 3),
    "saved_recovery_evidence": ("SELECT COUNT(*) FROM fitness_demo.recovery_evidence", 13),
    "recovery_reviews_wait_for_baselines": ("SELECT COUNT(*) FROM fitness_demo.recovery_state WHERE status='insufficient_evidence' AND sleep_valid_days_7<5 AND rhr_valid_days_7<5 AND sleep_valid_days_42<28", 3),
    "recovery_evidence_has_valid_review": ("SELECT COUNT(*) FROM fitness_demo.recovery_evidence e LEFT JOIN fitness_demo.recovery_state s ON e.athlete_id=s.athlete_id AND e.assessment_id=s.assessment_id AND e.assessment_version=s.assessment_version WHERE s.assessment_id IS NULL", 0),
    "recovery_evidence_has_valid_rule": ("SELECT COUNT(*) FROM fitness_demo.recovery_evidence e LEFT JOIN fitness_demo.recovery_rule r ON e.rule_id=r.rule_id WHERE r.rule_id IS NULL", 0),
    "typed_capability_reviews": ("SELECT COUNT(*) FROM fitness_demo.capability_assessment", 6),
    "capability_evidence_rows": ("SELECT COUNT(*) FROM fitness_demo.capability_evidence", 26),
    "capability_evidence_has_review": ("SELECT COUNT(*) FROM fitness_demo.capability_evidence e LEFT JOIN fitness_demo.capability_assessment a ON e.athlete_id=a.athlete_id AND e.assessment_id=a.assessment_id AND e.assessment_version=a.assessment_version WHERE a.assessment_id IS NULL", 0),
    "single_pace_profile_is_baseline": ("SELECT COUNT(*) FROM fitness_demo.capability_assessment WHERE capability_type='running_pace_capacity' AND status='baseline_only'", 1),
    "verified_weekly_mileage_growth": ("SELECT COUNT(*) FROM fitness_demo.v_weekly_running_distance WHERE athlete_id='demo_01' AND distance_km=20 AND prior_distance_km=13 AND growth_ratio>0.1", 1),
}
for label, (sql, expected) in checks.items():
    actual = one(sql)
    assert actual == expected, f"{label}: expected {expected}, got {actual}"
    print(f"PASS {label}: {actual}")

# Official bands must classify every supported boundary exactly once.
for metric_code, values in {
    "recovery_pct": [0, 19, 20, 69, 70, 89, 90, 100],
    "load_ratio": [0, 0.49, 0.5, 0.79, 0.8, 0.99, 1.0, 1.49, 1.5],
}.items():
    for value in values:
        matches = one(f"""SELECT COUNT(*) FROM fitness_demo.recovery_rule
            WHERE rule_kind = 'provider_band' AND metric_code = '{metric_code}'
              AND (lower_bound IS NULL OR {value} > lower_bound OR ({value} = lower_bound AND lower_inclusive))
              AND (upper_bound IS NULL OR {value} < upper_bound OR ({value} = upper_bound AND upper_inclusive))""")
        assert matches == 1, f"{metric_code}={value}: expected one band, got {matches}"
    print(f"PASS {metric_code} provider band boundaries")

metrics = {
    "measured_run_distance_km": 41.0,
    "run_session_count": 5,
    "coros_training_load": 868,
    "hyrox_run_time_sum_s": 2920,
    "hyrox_rule_reference_pace_s_per_km": 365.0,
    "official_10k_net_time_s": 3190,
    "avg_short_term_load": 320.0,
    "avg_sleep_score": 82.0,
    "avg_resting_hr_bpm": 55.0,
    "latest_vo2max_running": 47.0,
}
for name, expected in metrics.items():
    actual = model_metric(name)
    assert actual is not None and abs(float(actual) - expected) < 1e-6, f"{name}: expected {expected}, got {actual}"
    print(f"PASS DOSI {name}: {actual}")

print("All fixture and DOSI checks passed.")
