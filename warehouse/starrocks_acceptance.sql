-- Run after starrocks_schema.sql and starrocks_seed.sql.
-- All records and outputs below are fictional.
USE fitness_demo;
SELECT COUNT(*) AS athletes FROM athlete; -- 3
SELECT COUNT(*) AS goal_versions FROM athlete_goal; -- 4
SELECT COUNT(*) AS action_plan_versions FROM action_plan; -- 4
SELECT COUNT(*) AS planned_actions FROM planned_action; -- 7
SELECT action_id, action_kind, planning_status, completion_status, candidate_event_id, verified_event_id, match_method
FROM planned_action ORDER BY athlete_id, plan_id, plan_version, action_id; -- one manually verified, one candidate-only, five unassessed
SELECT COUNT(*) AS actions_without_plan_version FROM planned_action a LEFT JOIN action_plan p
ON a.athlete_id=p.athlete_id AND a.plan_id=p.plan_id AND a.plan_version=p.plan_version WHERE p.plan_id IS NULL; -- 0
SELECT COUNT(*) AS unverified_fulfillment FROM planned_action
WHERE completion_status<>'verified_completed' AND verified_event_id IS NOT NULL; -- 0
SELECT plan_id, plan_version, goal_id, goal_version, status, approval_status, approved_at_utc
FROM action_plan ORDER BY athlete_id, plan_id, plan_version; -- two running-plan versions; only version 1 approved
SELECT COUNT(*) AS plans_without_goal_version FROM action_plan p LEFT JOIN athlete_goal g
ON p.athlete_id=g.athlete_id AND p.goal_id=g.goal_id AND p.goal_version=g.goal_version WHERE g.goal_id IS NULL; -- 0
SELECT COUNT(*) AS pending_plans_with_approval_time FROM action_plan
WHERE approval_status='pending' AND approved_at_utc IS NOT NULL; -- 0
SELECT COUNT(*) AS active_goals FROM athlete_goal WHERE athlete_id = 'demo_01' AND status = 'active'; -- 2
SELECT COUNT(DISTINCT goal_version) AS saved_revisions FROM athlete_goal WHERE athlete_id = 'demo_01' AND goal_id = 'synthetic_run_consistency'; -- 2
SELECT COUNT(*) AS goal_progress_reviews FROM goal_progress_assessment; -- 4
SELECT COUNT(*) AS goal_progress_evidence FROM goal_progress_evidence; -- 7
SELECT goal_id, goal_version, criterion_id, status, observed_value, difference_value, method_version
FROM goal_progress_assessment ORDER BY goal_id, goal_version; -- old weekly achieved 2/2, new weekly needs_review 2/3, sleep and race insufficient_evidence
SELECT COUNT(*) AS missing_criteria FROM goal_progress_assessment a LEFT JOIN goal_criterion c
ON a.athlete_id=c.athlete_id AND a.goal_id=c.goal_id AND a.goal_version=c.goal_version AND a.criterion_id=c.criterion_id
WHERE c.criterion_id IS NULL; -- 0
SELECT COUNT(*) AS missing_progress_reviews FROM goal_progress_evidence e LEFT JOIN goal_progress_assessment a
ON e.athlete_id=a.athlete_id AND e.assessment_id=a.assessment_id AND e.assessment_version=a.assessment_version
WHERE a.assessment_id IS NULL; -- 0
SELECT COUNT(*) AS daily_recovery_reviews FROM recovery_state; -- 3
SELECT COUNT(*) AS cited_recovery_evidence FROM recovery_evidence; -- 13
SELECT COUNT(*) AS typed_capability_reviews FROM capability_assessment; -- 6
SELECT COUNT(*) AS cited_capability_evidence FROM capability_evidence; -- 26
SELECT capability_type, status, confidence FROM capability_assessment ORDER BY capability_type;
SELECT review_date, status, sleep_valid_days_7, rhr_valid_days_7, sleep_valid_days_42
FROM recovery_state ORDER BY review_date; -- all 3: insufficient_evidence; coverage 0/1/2
SELECT COUNT(*) AS missing_rule_refs FROM recovery_evidence e LEFT JOIN recovery_rule r ON e.rule_id = r.rule_id WHERE r.rule_id IS NULL; -- 0
SELECT COUNT(*) AS workout_events FROM workout_event; -- 6
SELECT COUNT(*) AS source_activities FROM activity; -- 7
SELECT COUNT(*) AS duplicate_copies FROM activity WHERE dedup_status = 'duplicate'; -- 1
SELECT COUNT(*) AS run_sessions, SUM(measured_distance_m) / 1000.0 AS km
FROM v_running_observation; -- 5, 41.0
SELECT SUM(training_load) AS canonical_load
FROM activity WHERE dedup_status = 'canonical'; -- 868
SELECT official_finish_s AS official_10k_seconds
FROM workout_event WHERE race_format_code = '10km'; -- 3190
SELECT COUNT(*) AS segments, SUM(duration_s) AS run_seconds
FROM v_running_rule_reference; -- 8, 2920
SELECT AVG(short_term_load) AS avg_short_term_load
FROM athlete_daily_training_load; -- 320
SELECT AVG(sleep_score) AS avg_sleep_score
FROM athlete_daily_sleep; -- 82
SELECT AVG(rhr_bpm) AS avg_resting_hr
FROM athlete_daily_resting_hr; -- 55
SELECT rule_kind, COUNT(*) AS rules FROM recovery_rule GROUP BY rule_kind; -- provider_band: 9; personal_signal: 6
SELECT rule_id, metric_code, lower_bound, upper_bound, lower_inclusive, upper_inclusive, rule_origin
FROM recovery_rule ORDER BY rule_kind, metric_code, lower_bound;
