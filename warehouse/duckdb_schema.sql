-- Completely fictional athletes and workouts; safe for public demos.

CREATE SCHEMA IF NOT EXISTS fitness_demo;

SET schema 'fitness_demo';

CREATE TABLE IF NOT EXISTS athlete (
  athlete_id VARCHAR(255),
  gender_code VARCHAR(255),
  timezone_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS workout_event (
  athlete_id VARCHAR(255),
  workout_event_id VARCHAR(255),
  event_date DATE,
  started_at_local TIMESTAMP,
  sport_code VARCHAR(255),
  session_intent VARCHAR(255),
  is_official_race BOOLEAN,
  event_name VARCHAR(255),
  race_format_code VARCHAR(255),
  division_code VARCHAR(255),
  participation_mode VARCHAR(255),
  partner_ref VARCHAR(255),
  watch_elapsed_s BIGINT,
  official_finish_s BIGINT,
  official_penalty_s BIGINT
);

CREATE TABLE IF NOT EXISTS activity (
  athlete_id VARCHAR(255),
  activity_id VARCHAR(255),
  activity_date DATE,
  sport_code VARCHAR(255),
  workout_event_id VARCHAR(255),
  source VARCHAR(255),
  source_activity_id VARCHAR(255),
  workout_duration_s BIGINT,
  elapsed_duration_s BIGINT,
  distance_m BIGINT,
  avg_hr_bpm BIGINT,
  avg_cadence_spm BIGINT,
  avg_power_w BIGINT,
  training_load BIGINT,
  training_focus VARCHAR(255),
  calories_kcal BIGINT,
  dedup_status VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS running_observation_fact (
  athlete_id VARCHAR(255),
  workout_event_id VARCHAR(255),
  analysis_revision BIGINT,
  segment_ordinal BIGINT,
  run_index BIGINT,
  station_index BIGINT,
  segment_kind VARCHAR(255),
  exercise_code VARCHAR(255),
  run_context VARCHAR(255),
  phase_kind VARCHAR(255),
  run_environment VARCHAR(255),
  event_date DATE,
  observation_date DATE,
  duration_basis VARCHAR(255),
  distance_status VARCHAR(255),
  pace_basis VARCHAR(255),
  duration_s BIGINT,
  measured_distance_m BIGINT,
  planned_distance_m BIGINT,
  reported_pace_s_per_km BIGINT,
  measured_pace_s_per_km BIGINT,
  pace_time_s BIGINT,
  pace_distance_m BIGINT,
  avg_hr_bpm BIGINT,
  hr_weighted_sum_bpm_s BIGINT,
  hr_weight_s BIGINT,
  hr_sample_coverage_s BIGINT,
  avg_cadence_spm BIGINT,
  cadence_weighted_sum_spm_s BIGINT,
  cadence_weight_s BIGINT,
  cadence_sample_coverage_s BIGINT,
  sport_code VARCHAR(255),
  session_intent VARCHAR(255),
  is_official_race BOOLEAN,
  event_name VARCHAR(255),
  race_format_code VARCHAR(255),
  division_code VARCHAR(255),
  participation_mode VARCHAR(255),
  partner_ref VARCHAR(255)
);

CREATE VIEW v_running_observation AS SELECT * FROM running_observation_fact;

CREATE TABLE IF NOT EXISTS hyrox_station_fact (
  athlete_id VARCHAR(255),
  workout_event_id VARCHAR(255),
  analysis_revision BIGINT,
  segment_ordinal BIGINT,
  run_index BIGINT,
  station_index BIGINT,
  segment_kind VARCHAR(255),
  exercise_code VARCHAR(255),
  exercise_name_zh VARCHAR(255),
  event_date DATE,
  duration_s BIGINT,
  watch_station_time_s BIGINT,
  official_station_finish_s BIGINT,
  official_penalty_s BIGINT,
  comparison_conditions_verified BOOLEAN,
  comparison_group_key VARCHAR(255),
  repetitions BIGINT,
  prescribed_repetitions BIGINT,
  load_total_kg DECIMAL(18,3),
  load_per_hand_kg DECIMAL(18,3),
  sport_code VARCHAR(255),
  session_intent VARCHAR(255),
  is_official_race BOOLEAN,
  event_name VARCHAR(255),
  race_format_code VARCHAR(255),
  division_code VARCHAR(255),
  participation_mode VARCHAR(255),
  partner_ref VARCHAR(255)
);

CREATE VIEW v_hyrox_race_station AS SELECT * FROM hyrox_station_fact;

CREATE TABLE IF NOT EXISTS running_rule_reference_fact (
  athlete_id VARCHAR(255),
  workout_event_id VARCHAR(255),
  analysis_revision BIGINT,
  segment_ordinal BIGINT,
  run_index BIGINT,
  segment_kind VARCHAR(255),
  exercise_code VARCHAR(255),
  event_date DATE,
  duration_s BIGINT,
  reference_distance_m BIGINT,
  reference_distance_basis VARCHAR(255),
  rule_reference_pace_s_per_km BIGINT,
  rule_id VARCHAR(255),
  rule_match_status VARCHAR(255),
  event_rule_season_verified BOOLEAN,
  measured_pace_s_per_km BIGINT,
  avg_hr_bpm BIGINT,
  hr_weighted_sum_bpm_s BIGINT,
  hr_weight_s BIGINT,
  avg_cadence_spm BIGINT,
  cadence_weighted_sum_spm_s BIGINT,
  cadence_weight_s BIGINT,
  event_name VARCHAR(255),
  race_format_code VARCHAR(255),
  participation_mode VARCHAR(255),
  division_code VARCHAR(255),
  partner_ref VARCHAR(255),
  is_official_race BOOLEAN,
  sport_code VARCHAR(255),
  session_intent VARCHAR(255)
);

CREATE VIEW v_running_rule_reference AS SELECT * FROM running_rule_reference_fact;

CREATE TABLE IF NOT EXISTS athlete_daily_training_load (
  athlete_id VARCHAR(255),
  source VARCHAR(255),
  local_date DATE,
  short_term_load BIGINT,
  long_term_load BIGINT,
  load_ratio DECIMAL(18,3),
  provider_status VARCHAR(255),
  observed_at_utc TIMESTAMP,
  source_snapshot_id VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS athlete_daily_sleep (
  athlete_id VARCHAR(255),
  source VARCHAR(255),
  wake_date DATE,
  data_status VARCHAR(255),
  source_score_raw VARCHAR(255),
  sleep_score DECIMAL(18,3),
  daily_sleep_min BIGINT,
  main_sleep_min BIGINT,
  main_period_min BIGINT,
  nap_sleep_min BIGINT,
  deep_pct DECIMAL(18,3),
  light_pct DECIMAL(18,3),
  rem_pct DECIMAL(18,3),
  awake_pct DECIMAL(18,3),
  awake_min BIGINT,
  awake_count BIGINT,
  metrics_scope VARCHAR(255),
  main_start_local TIMESTAMP,
  main_end_local TIMESTAMP,
  observed_at_utc TIMESTAMP,
  source_snapshot_id VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS athlete_daily_hrv (
  athlete_id VARCHAR(255),
  source VARCHAR(255),
  wake_date DATE,
  hrv_avg_ms DECIMAL(18,3),
  normal_low_ms DECIMAL(18,3),
  normal_high_ms DECIMAL(18,3),
  baseline_ms DECIMAL(18,3),
  provider_evaluation VARCHAR(255),
  data_status VARCHAR(255),
  observed_at_utc TIMESTAMP,
  source_snapshot_id VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS athlete_daily_resting_hr (
  athlete_id VARCHAR(255),
  source VARCHAR(255),
  local_date DATE,
  rhr_bpm BIGINT,
  data_status VARCHAR(255),
  observed_at_utc TIMESTAMP,
  source_snapshot_id VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS athlete_recovery_observation (
  athlete_id VARCHAR(255),
  observation_id VARCHAR(255),
  source VARCHAR(255),
  observed_at_utc TIMESTAMP,
  recovery_pct DECIMAL(18,3),
  recovery_level VARCHAR(255),
  estimated_full_recovery_h BIGINT,
  source_snapshot_id VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS athlete_hr_zone (
  athlete_id VARCHAR(255),
  zone_scheme_id VARCHAR(255),
  zone_index BIGINT,
  sport_code VARCHAR(255),
  scheme_method VARCHAR(255),
  valid_from_utc TIMESTAMP,
  valid_to_utc TIMESTAMP,
  lower_inclusive_bpm BIGINT,
  upper_exclusive_bpm BIGINT
);

CREATE TABLE IF NOT EXISTS athlete_pace_zone (
  athlete_id VARCHAR(255),
  zone_scheme_id VARCHAR(255),
  zone_index BIGINT,
  sport_code VARCHAR(255),
  scheme_method VARCHAR(255),
  valid_from_utc TIMESTAMP,
  valid_to_utc TIMESTAMP,
  fast_boundary_s_per_km BIGINT,
  slow_boundary_s_per_km BIGINT
);

CREATE TABLE IF NOT EXISTS fitness_measurement (
  athlete_id VARCHAR(255),
  measurement_id VARCHAR(255),
  metric_code VARCHAR(255),
  metric_value DECIMAL(18,3),
  unit VARCHAR(255),
  measured_at_utc TIMESTAMP,
  effective_from_utc TIMESTAMP,
  observed_at_utc TIMESTAMP,
  time_quality VARCHAR(255),
  source VARCHAR(255)
);

CREATE VIEW v_latest_body_measurement AS SELECT athlete_id, measurement_id, metric_code, metric_value, unit, measured_at_utc, effective_from_utc, observed_at_utc, time_quality, source FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY athlete_id, metric_code ORDER BY COALESCE(measured_at_utc, observed_at_utc) DESC, measurement_id DESC) AS recency_rank FROM fitness_measurement) ranked WHERE recency_rank = 1;

CREATE TABLE IF NOT EXISTS activity_segment (
  athlete_id VARCHAR(255),
  activity_id VARCHAR(255),
  lap_ordinal BIGINT,
  segment_kind VARCHAR(255),
  is_canonical BOOLEAN,
  duration_s BIGINT,
  distance_m BIGINT,
  avg_pace_s_per_km BIGINT,
  avg_hr_bpm BIGINT,
  avg_cadence_spm BIGINT,
  avg_power_w BIGINT
);

CREATE TABLE IF NOT EXISTS athlete_goal (
  athlete_id VARCHAR(255),
  goal_id VARCHAR(255),
  goal_version BIGINT,
  goal_type VARCHAR(255),
  title VARCHAR(255),
  status VARCHAR(255),
  created_at_utc TIMESTAMP
);

CREATE TABLE IF NOT EXISTS goal_criterion (
  athlete_id VARCHAR(255),
  goal_id VARCHAR(255),
  goal_version BIGINT,
  criterion_id VARCHAR(255),
  criterion_kind VARCHAR(255),
  metric_name VARCHAR(255),
  comparison_operator VARCHAR(255),
  target_value DECIMAL(18,3),
  target_unit VARCHAR(255),
  aggregation_window VARCHAR(255),
  target_date DATE,
  evidence_policy VARCHAR(255),
  created_at_utc TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recovery_state (
  athlete_id VARCHAR(255),
  assessment_id VARCHAR(255),
  assessment_version BIGINT,
  review_date DATE,
  source VARCHAR(255),
  status VARCHAR(255),
  method_version VARCHAR(255),
  evaluated_at_utc TIMESTAMP,
  sleep_valid_days_7 BIGINT,
  rhr_valid_days_7 BIGINT,
  sleep_valid_days_42 BIGINT,
  load_source VARCHAR(255),
  load_date DATE,
  sleep_source VARCHAR(255),
  sleep_wake_date DATE,
  rhr_source VARCHAR(255),
  rhr_date DATE,
  provider_observation_id VARCHAR(255),
  hrv_source VARCHAR(255),
  hrv_wake_date DATE
);

CREATE TABLE IF NOT EXISTS recovery_evidence (
  athlete_id VARCHAR(255),
  assessment_id VARCHAR(255),
  assessment_version BIGINT,
  evidence_id VARCHAR(255),
  source_dataset VARCHAR(255),
  source_record_id VARCHAR(255),
  source_date DATE,
  metric_code VARCHAR(255),
  observed_value DECIMAL(18,3),
  unit VARCHAR(255),
  rule_id VARCHAR(255),
  evaluation_status VARCHAR(255),
  valid_prior_days BIGINT,
  baseline_days BIGINT
);

CREATE TABLE IF NOT EXISTS recovery_rule (
  rule_id VARCHAR(255),
  rule_kind VARCHAR(255),
  metric_code VARCHAR(255),
  lower_bound DECIMAL(18,3),
  upper_bound DECIMAL(18,3),
  lower_inclusive BOOLEAN,
  upper_inclusive BOOLEAN,
  label VARCHAR(255),
  meaning VARCHAR(255),
  rule_origin VARCHAR(255),
  source_url VARCHAR(255),
  baseline_days BIGINT,
  min_valid_days BIGINT
);

CREATE TABLE IF NOT EXISTS capability_assessment (
  athlete_id VARCHAR(255),
  assessment_id VARCHAR(255),
  assessment_version BIGINT,
  capability_type VARCHAR(255),
  review_date DATE,
  status VARCHAR(255),
  confidence VARCHAR(255),
  method_version VARCHAR(255),
  rationale VARCHAR(255),
  created_at_utc TIMESTAMP
);

CREATE TABLE IF NOT EXISTS capability_evidence (
  athlete_id VARCHAR(255),
  assessment_id VARCHAR(255),
  assessment_version BIGINT,
  evidence_id VARCHAR(255),
  evidence_kind VARCHAR(255),
  metric_name VARCHAR(255),
  source_dataset VARCHAR(255),
  source_record_id VARCHAR(255),
  source_date DATE,
  observed_value DECIMAL(18,3),
  unit VARCHAR(255),
  comparability_status VARCHAR(255),
  confidence VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS goal_progress_assessment (
  athlete_id VARCHAR(255),
  assessment_id VARCHAR(255),
  assessment_version BIGINT,
  goal_id VARCHAR(255),
  goal_version BIGINT,
  criterion_id VARCHAR(255),
  review_date DATE,
  window_start_date DATE,
  window_end_date DATE,
  status VARCHAR(255),
  observed_value DECIMAL(18,3),
  difference_value DECIMAL(18,3),
  difference_unit VARCHAR(255),
  comparison_basis VARCHAR(255),
  method_version VARCHAR(255),
  rationale VARCHAR(255),
  evaluated_at_utc TIMESTAMP
);

CREATE TABLE IF NOT EXISTS goal_progress_evidence (
  athlete_id VARCHAR(255),
  assessment_id VARCHAR(255),
  assessment_version BIGINT,
  evidence_id VARCHAR(255),
  source_dataset VARCHAR(255),
  source_record_id VARCHAR(255),
  source_date DATE,
  metric_name VARCHAR(255),
  observed_value DECIMAL(18,3),
  unit VARCHAR(255),
  quality_status VARCHAR(255),
  comparison_basis VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS action_plan (
  athlete_id VARCHAR(255),
  plan_id VARCHAR(255),
  plan_version BIGINT,
  goal_id VARCHAR(255),
  goal_version BIGINT,
  title VARCHAR(255),
  plan_summary VARCHAR(255),
  status VARCHAR(255),
  approval_status VARCHAR(255),
  created_at_utc TIMESTAMP,
  approved_at_utc TIMESTAMP,
  revision_reason VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS planned_action (
  athlete_id VARCHAR(255),
  plan_id VARCHAR(255),
  plan_version BIGINT,
  action_id VARCHAR(255),
  scheduled_date DATE,
  action_kind VARCHAR(255),
  title VARCHAR(255),
  target_duration_min BIGINT,
  planning_status VARCHAR(255),
  completion_status VARCHAR(255),
  candidate_event_id VARCHAR(255),
  verified_event_id VARCHAR(255),
  match_method VARCHAR(255),
  match_reviewed_at_utc TIMESTAMP,
  source VARCHAR(255),
  planned_intensity VARCHAR(255),
  title_zh VARCHAR(255),
  target_distance_km DECIMAL(18,3),
  target_distance_min_km DECIMAL(18,3),
  target_distance_max_km DECIMAL(18,3),
  distance_basis VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS planned_action_segment (
  athlete_id VARCHAR(255),
  plan_id VARCHAR(255),
  plan_version BIGINT,
  action_id VARCHAR(255),
  segment_ordinal BIGINT,
  segment_type VARCHAR(255),
  title_en VARCHAR(255),
  title_zh VARCHAR(255),
  target_duration_min BIGINT,
  target_distance_km DECIMAL(18,3),
  target_pace_fast_s_per_km BIGINT,
  target_pace_slow_s_per_km BIGINT,
  target_hr_low_bpm BIGINT,
  target_hr_high_bpm BIGINT
);

CREATE TABLE IF NOT EXISTS coach_review (
  athlete_id VARCHAR(255),
  review_id VARCHAR(255),
  goal_id VARCHAR(255),
  goal_version BIGINT,
  plan_id VARCHAR(255),
  plan_version BIGINT,
  review_date DATE,
  window_start_date DATE,
  window_end_date DATE,
  data_watermark_date DATE,
  rule_version VARCHAR(255),
  status VARCHAR(255),
  summary VARCHAR(2048),
  next_step_text VARCHAR(2048),
  created_at_utc TIMESTAMP
);

CREATE TABLE IF NOT EXISTS coach_review_finding (
  athlete_id VARCHAR(255),
  review_id VARCHAR(255),
  finding_id VARCHAR(255),
  rule_code VARCHAR(255),
  status VARCHAR(255),
  observed_value DECIMAL(18,3),
  baseline_value DECIMAL(18,3),
  unit VARCHAR(255),
  evidence_date DATE,
  source_dataset VARCHAR(255),
  source_record_id VARCHAR(255),
  evidence_status VARCHAR(255),
  summary VARCHAR(2048)
);

CREATE TABLE IF NOT EXISTS coach_review_proposal (
  athlete_id VARCHAR(255),
  review_id VARCHAR(255),
  proposal_id VARCHAR(255),
  plan_id VARCHAR(255),
  plan_version BIGINT,
  action_id VARCHAR(255),
  proposed_change VARCHAR(2048),
  decision_status VARCHAR(255),
  decided_at_utc TIMESTAMP
);

CREATE TABLE IF NOT EXISTS activity_import_coverage (athlete_id VARCHAR(255), local_date DATE, status VARCHAR(32));

CREATE VIEW v_weekly_running_distance AS
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
  ON cur.athlete_id = prior.athlete_id AND prior.week_start = cur.week_start - INTERVAL 7 DAY
WHERE prior.distance_km > 0;
