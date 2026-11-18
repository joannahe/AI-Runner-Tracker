-- Generated from the same fixture definitions as the other engine.

SET schema 'fitness_demo';

INSERT INTO athlete (athlete_id, gender_code, timezone_name) VALUES
  ('demo_01', 'F', 'UTC'),
  ('demo_02', 'M', 'UTC'),
  ('demo_03', 'F', 'UTC');

INSERT INTO workout_event (athlete_id, workout_event_id, event_date, started_at_local, sport_code, session_intent, is_official_race, event_name, race_format_code, participation_mode, watch_elapsed_s, official_finish_s, official_penalty_s) VALUES
  ('demo_01', 'evt_101', '2026-04-06', '2026-04-06 07:00:00', 'running', 'easy', FALSE, NULL, NULL, 'solo', 2380, NULL, 0),
  ('demo_01', 'evt_102', '2026-04-09', '2026-04-09 07:00:00', 'running', 'tempo', FALSE, NULL, NULL, 'solo', 2640, NULL, 0),
  ('demo_01', 'evt_103', '2026-04-13', '2026-04-13 07:00:00', 'running', 'long', FALSE, NULL, NULL, 'solo', 3900, NULL, 0),
  ('demo_01', 'evt_104', '2026-04-19', '2026-04-19 07:00:00', 'running', 'race', TRUE, 'Fictional Harbor 10K', '10km', 'solo', 3210, 3190, 0),
  ('demo_02', 'evt_201', '2026-04-10', '2026-04-10 07:00:00', 'running', 'easy', FALSE, NULL, NULL, 'solo', 2700, NULL, 0),
  ('demo_03', 'evt_301', '2026-04-11', '2026-04-11 07:00:00', 'hyrox', 'race', TRUE, 'Fictional Indoor Team Race', 'hyrox_doubles', 'team', 7200, 7100, 0);

INSERT INTO activity (athlete_id, activity_id, activity_date, sport_code, workout_event_id, source, source_activity_id, workout_duration_s, elapsed_duration_s, distance_m, avg_hr_bpm, avg_cadence_spm, avg_power_w, training_load, training_focus, dedup_status) VALUES
  ('demo_01', 'act_001', '2026-04-06', 'running', 'evt_101', 'coros', 'synthetic_1', 2380, 2380, 6000, 143, 166, 178, 90, 'Base', 'canonical'),
  ('demo_01', 'act_002', '2026-04-09', 'running', 'evt_102', 'coros', 'synthetic_2', 2640, 2640, 7000, 158, 172, 214, 124, 'Tempo', 'canonical'),
  ('demo_01', 'act_003', '2026-04-13', 'running', 'evt_103', 'coros', 'synthetic_3', 3900, 3900, 10000, 147, 168, 192, 150, 'Base', 'canonical'),
  ('demo_01', 'act_004', '2026-04-19', 'running', 'evt_104', 'coros', 'synthetic_4', 3210, 3210, 10000, 164, 176, 235, 202, 'Threshold', 'canonical'),
  ('demo_02', 'act_005', '2026-04-10', 'running', 'evt_201', 'coros', 'synthetic_5', 2700, 2700, 8000, 152, 174, 228, 112, 'Easy', 'canonical'),
  ('demo_01', 'act_copy', '2026-04-06', 'running', 'evt_101', 'fictional_import', 'synthetic_copy', 2380, 2380, 6000, 143, 166, 178, 90, NULL, 'duplicate'),
  ('demo_03', 'act_301', '2026-04-11', 'hyrox', 'evt_301', 'coros', 'synthetic_hyrox', 7200, 7200, NULL, NULL, NULL, NULL, 190, NULL, 'canonical');

INSERT INTO running_observation_fact (athlete_id, workout_event_id, analysis_revision, segment_ordinal, segment_kind, run_context, phase_kind, run_environment, event_date, observation_date, duration_basis, distance_status, pace_basis, duration_s, measured_distance_m, pace_time_s, pace_distance_m, avg_hr_bpm, hr_weighted_sum_bpm_s, hr_weight_s, hr_sample_coverage_s, avg_cadence_spm, cadence_weighted_sum_spm_s, cadence_weight_s, cadence_sample_coverage_s, sport_code, session_intent, is_official_race, event_name, race_format_code, participation_mode) VALUES
  ('demo_01', 'evt_101', 1, 1, 'run', 'standalone', 'main', 'outdoor', '2026-04-06', '2026-04-06', 'watch_moving', 'measured', 'measured', 2380, 6000, 2380, 6000, 143, 340340, 2380, 2380, 166, 395080, 2380, 2380, 'running', 'easy', FALSE, NULL, NULL, 'solo'),
  ('demo_01', 'evt_102', 1, 1, 'run', 'standalone', 'main', 'outdoor', '2026-04-09', '2026-04-09', 'watch_moving', 'measured', 'measured', 2640, 7000, 2640, 7000, 158, 417120, 2640, 2640, 172, 454080, 2640, 2640, 'running', 'tempo', FALSE, NULL, NULL, 'solo'),
  ('demo_01', 'evt_103', 1, 1, 'run', 'standalone', 'main', 'outdoor', '2026-04-13', '2026-04-13', 'watch_moving', 'measured', 'measured', 3900, 10000, 3900, 10000, 147, 573300, 3900, 3900, 168, 655200, 3900, 3900, 'running', 'long', FALSE, NULL, NULL, 'solo'),
  ('demo_01', 'evt_104', 1, 1, 'run', 'standalone', 'main', 'outdoor', '2026-04-19', '2026-04-19', 'watch_moving', 'measured', 'measured', 3210, 10000, 3210, 10000, 164, 526440, 3210, 3210, 176, 564960, 3210, 3210, 'running', 'race', TRUE, 'Fictional Harbor 10K', '10km', 'solo'),
  ('demo_02', 'evt_201', 1, 1, 'run', 'standalone', 'main', 'outdoor', '2026-04-10', '2026-04-10', 'watch_moving', 'measured', 'measured', 2700, 8000, 2700, 8000, 152, 410400, 2700, 2700, 174, 469800, 2700, 2700, 'running', 'easy', FALSE, NULL, NULL, 'solo');

INSERT INTO hyrox_station_fact (athlete_id, workout_event_id, analysis_revision, segment_ordinal, station_index, segment_kind, exercise_code, exercise_name_zh, event_date, duration_s, watch_station_time_s, comparison_conditions_verified, sport_code, session_intent, is_official_race, event_name, race_format_code, participation_mode) VALUES
  ('demo_03', 'evt_301', 1, 2, 1, 'station', 'ski', 'ski', '2026-04-11', 320, 320, FALSE, 'hyrox', 'race', TRUE, 'Fictional Indoor Team Race', 'hyrox_doubles', 'team'),
  ('demo_03', 'evt_301', 1, 4, 2, 'station', 'sled', 'sled', '2026-04-11', 480, 480, FALSE, 'hyrox', 'race', TRUE, 'Fictional Indoor Team Race', 'hyrox_doubles', 'team');

INSERT INTO running_rule_reference_fact (athlete_id, workout_event_id, analysis_revision, segment_ordinal, run_index, segment_kind, event_date, duration_s, reference_distance_m, reference_distance_basis, rule_reference_pace_s_per_km, rule_id, rule_match_status, event_rule_season_verified, event_name, race_format_code, participation_mode, is_official_race, sport_code, session_intent) VALUES
  ('demo_03', 'evt_301', 1, 1, 1, 'run', '2026-04-11', 344, 1000, 'fictional_rule', 344, 'example_v1', 'matched', TRUE, 'Fictional Indoor Team Race', 'hyrox_doubles', 'team', TRUE, 'hyrox', 'race'),
  ('demo_03', 'evt_301', 1, 3, 2, 'run', '2026-04-11', 350, 1000, 'fictional_rule', 350, 'example_v1', 'matched', TRUE, 'Fictional Indoor Team Race', 'hyrox_doubles', 'team', TRUE, 'hyrox', 'race'),
  ('demo_03', 'evt_301', 1, 5, 3, 'run', '2026-04-11', 356, 1000, 'fictional_rule', 356, 'example_v1', 'matched', TRUE, 'Fictional Indoor Team Race', 'hyrox_doubles', 'team', TRUE, 'hyrox', 'race'),
  ('demo_03', 'evt_301', 1, 7, 4, 'run', '2026-04-11', 361, 1000, 'fictional_rule', 361, 'example_v1', 'matched', TRUE, 'Fictional Indoor Team Race', 'hyrox_doubles', 'team', TRUE, 'hyrox', 'race'),
  ('demo_03', 'evt_301', 1, 9, 5, 'run', '2026-04-11', 369, 1000, 'fictional_rule', 369, 'example_v1', 'matched', TRUE, 'Fictional Indoor Team Race', 'hyrox_doubles', 'team', TRUE, 'hyrox', 'race'),
  ('demo_03', 'evt_301', 1, 11, 6, 'run', '2026-04-11', 373, 1000, 'fictional_rule', 373, 'example_v1', 'matched', TRUE, 'Fictional Indoor Team Race', 'hyrox_doubles', 'team', TRUE, 'hyrox', 'race'),
  ('demo_03', 'evt_301', 1, 13, 7, 'run', '2026-04-11', 381, 1000, 'fictional_rule', 381, 'example_v1', 'matched', TRUE, 'Fictional Indoor Team Race', 'hyrox_doubles', 'team', TRUE, 'hyrox', 'race'),
  ('demo_03', 'evt_301', 1, 15, 8, 'run', '2026-04-11', 386, 1000, 'fictional_rule', 386, 'example_v1', 'matched', TRUE, 'Fictional Indoor Team Race', 'hyrox_doubles', 'team', TRUE, 'hyrox', 'race');

INSERT INTO athlete_daily_training_load (athlete_id, source, local_date, short_term_load, long_term_load, load_ratio, provider_status, observed_at_utc, source_snapshot_id) VALUES
  ('demo_01', 'fictional_watch', '2026-04-19', 345, 300, 1.15, 'Balanced', '2026-04-19 06:00:00', 'load_1'),
  ('demo_01', 'fictional_watch', '2026-04-20', 320, 300, 1.067, 'Balanced', '2026-04-20 06:00:00', 'load_2'),
  ('demo_01', 'fictional_watch', '2026-04-21', 295, 300, 0.983, 'Balanced', '2026-04-21 06:00:00', 'load_3');

INSERT INTO athlete_daily_sleep (athlete_id, source, wake_date, data_status, sleep_score, daily_sleep_min, main_sleep_min, observed_at_utc, source_snapshot_id) VALUES
  ('demo_01', 'fictional_watch', '2026-04-19', 'present', 80, 430, 420, '2026-04-19 06:00:00', 'sleep_1'),
  ('demo_01', 'fictional_watch', '2026-04-20', 'present', 82, 440, 430, '2026-04-20 06:00:00', 'sleep_2'),
  ('demo_01', 'fictional_watch', '2026-04-21', 'present', 84, 450, 440, '2026-04-21 06:00:00', 'sleep_3');

INSERT INTO athlete_daily_hrv (athlete_id, source, wake_date, hrv_avg_ms, normal_low_ms, normal_high_ms, baseline_ms, provider_evaluation, data_status, observed_at_utc, source_snapshot_id) VALUES
  ('demo_01', 'fictional_watch', '2026-04-19', 48, 42, 55, 48, 'normal', 'present', '2026-04-19 06:00:00', 'hrv_1'),
  ('demo_01', 'fictional_watch', '2026-04-20', 39, 42, 55, 48, 'below_normal', 'present', '2026-04-20 06:00:00', 'hrv_2'),
  ('demo_01', 'fictional_watch', '2026-04-21', 47, 42, 55, 48, 'normal', 'present', '2026-04-21 06:00:00', 'hrv_3');

INSERT INTO athlete_daily_resting_hr (athlete_id, source, local_date, rhr_bpm, data_status, observed_at_utc, source_snapshot_id) VALUES
  ('demo_01', 'fictional_watch', '2026-04-19', 56, 'present', '2026-04-19 06:00:00', 'rhr_1'),
  ('demo_01', 'fictional_watch', '2026-04-20', 55, 'present', '2026-04-20 06:00:00', 'rhr_2'),
  ('demo_01', 'fictional_watch', '2026-04-21', 54, 'present', '2026-04-21 06:00:00', 'rhr_3');

INSERT INTO athlete_recovery_observation (athlete_id, observation_id, source, observed_at_utc, recovery_pct, recovery_level, estimated_full_recovery_h, source_snapshot_id) VALUES
  ('demo_01', 'recovery_1', 'fictional_watch', '2026-04-21 07:00:00', 76, 'normal', 8, 'recovery_fixture');

INSERT INTO athlete_hr_zone (athlete_id, zone_scheme_id, zone_index, sport_code, scheme_method, valid_from_utc, lower_inclusive_bpm, upper_exclusive_bpm) VALUES
  ('demo_01', 'fictional_hr_v1', 1, 'running', 'fictional', '2026-01-01 00:00:00', 0, 121),
  ('demo_01', 'fictional_hr_v1', 2, 'running', 'fictional', '2026-01-01 00:00:00', 121, 141),
  ('demo_01', 'fictional_hr_v1', 3, 'running', 'fictional', '2026-01-01 00:00:00', 141, 158),
  ('demo_01', 'fictional_hr_v1', 4, 'running', 'fictional', '2026-01-01 00:00:00', 158, 174),
  ('demo_01', 'fictional_hr_v1', 5, 'running', 'fictional', '2026-01-01 00:00:00', 174, 230);

INSERT INTO athlete_pace_zone (athlete_id, zone_scheme_id, zone_index, sport_code, scheme_method, valid_from_utc, fast_boundary_s_per_km, slow_boundary_s_per_km) VALUES
  ('demo_01', 'fictional_pace_v1', 1, 'running', 'fictional', '2026-01-01 00:00:00', 430, 600),
  ('demo_01', 'fictional_pace_v1', 2, 'running', 'fictional', '2026-01-01 00:00:00', 380, 430),
  ('demo_01', 'fictional_pace_v1', 3, 'running', 'fictional', '2026-01-01 00:00:00', 350, 380),
  ('demo_01', 'fictional_pace_v1', 4, 'running', 'fictional', '2026-01-01 00:00:00', 320, 350),
  ('demo_01', 'fictional_pace_v1', 5, 'running', 'fictional', '2026-01-01 00:00:00', 250, 320);

INSERT INTO fitness_measurement (athlete_id, measurement_id, metric_code, metric_value, unit, measured_at_utc, effective_from_utc, observed_at_utc, time_quality, source) VALUES
  ('demo_01', 'fictional_vo2max_running', 'vo2max_running', 47, 'ml/kg/min', '2026-04-15 10:00:00', '2026-04-15 10:00:00', '2026-04-15 10:00:00', 'exact', 'fictional_watch'),
  ('demo_01', 'fictional_threshold_pace_s_per_km', 'threshold_pace_s_per_km', 350, 's/km', '2026-04-15 10:00:00', '2026-04-15 10:00:00', '2026-04-15 10:00:00', 'exact', 'fictional_watch'),
  ('demo_01', 'fictional_threshold_hr_bpm', 'threshold_hr_bpm', 169, 'bpm', '2026-04-15 10:00:00', '2026-04-15 10:00:00', '2026-04-15 10:00:00', 'exact', 'fictional_watch');

INSERT INTO activity_segment (athlete_id, activity_id, lap_ordinal, segment_kind, is_canonical, duration_s, distance_m, avg_pace_s_per_km, avg_hr_bpm, avg_cadence_spm, avg_power_w) VALUES
  ('demo_01', 'act_001', 1, 'run', TRUE, 2380, 6000, 396, 143, 166, 178),
  ('demo_01', 'act_002', 1, 'run', TRUE, 2640, 7000, 377, 158, 172, 214),
  ('demo_01', 'act_003', 1, 'run', TRUE, 3900, 10000, 390, 147, 168, 192),
  ('demo_01', 'act_004', 1, 'run', TRUE, 3210, 10000, 321, 164, 176, 235),
  ('demo_02', 'act_005', 1, 'run', TRUE, 2700, 8000, 337, 152, 174, 228);

INSERT INTO athlete_goal (athlete_id, goal_id, goal_version, goal_type, title, status, created_at_utc) VALUES
  ('demo_01', 'synthetic_run_consistency', 1, 'running_consistency', 'Run regularly', 'superseded', '2026-04-01 09:00:00'),
  ('demo_01', 'synthetic_run_consistency', 2, 'running_consistency', 'Build a consistent running habit', 'active', '2026-04-08 09:00:00'),
  ('demo_01', 'synthetic_sleep', 1, 'sleep', 'Improve sleep consistency', 'active', '2026-04-10 09:00:00'),
  ('demo_02', 'synthetic_race', 1, 'race', 'Prepare for a 10K', 'active', '2026-04-05 09:00:00');

INSERT INTO goal_criterion (athlete_id, goal_id, goal_version, criterion_id, criterion_kind, metric_name, comparison_operator, target_value, target_unit, aggregation_window, target_date, evidence_policy, created_at_utc) VALUES
  ('demo_01', 'synthetic_run_consistency', 1, 'weekly_run_days', 'running_frequency', 'run_day_count', '>=', 2, 'days/week', 'calendar_week', NULL, 'standalone_runs_only', '2026-04-01 09:00:00'),
  ('demo_01', 'synthetic_run_consistency', 2, 'weekly_run_days', 'running_frequency', 'run_day_count', '>=', 3, 'days/week', 'calendar_week', NULL, 'standalone_runs_only', '2026-04-08 09:00:00'),
  ('demo_01', 'synthetic_sleep', 1, 'main_sleep', 'sleep_duration', 'avg_main_sleep_minutes', '>=', 420, 'minutes', 'rolling_7_wake_days', NULL, 'minimum_5_valid_days', '2026-04-10 09:00:00'),
  ('demo_02', 'synthetic_race', 1, 'ten_k_time', 'race_time', 'official_10k_net_time_s', '<=', 3000, 'seconds', 'official_10k_event', '2026-06-01', 'same_distance_official_net_time', '2026-04-05 09:00:00');

INSERT INTO recovery_state (athlete_id, assessment_id, assessment_version, review_date, source, status, method_version, evaluated_at_utc, sleep_valid_days_7, rhr_valid_days_7, sleep_valid_days_42, load_source, load_date, sleep_source, sleep_wake_date, rhr_source, rhr_date, provider_observation_id) VALUES
  ('demo_01', 'recovery_review_demo_01_2026-04-19', 1, '2026-04-19', 'fictional_watch', 'insufficient_evidence', 'recovery_review_v1', '2026-04-19 08:00:00', 0, 0, 0, 'fictional_watch', '2026-04-19', 'fictional_watch', '2026-04-19', 'fictional_watch', '2026-04-19', NULL),
  ('demo_01', 'recovery_review_demo_01_2026-04-20', 1, '2026-04-20', 'fictional_watch', 'insufficient_evidence', 'recovery_review_v1', '2026-04-20 08:00:00', 1, 1, 1, 'fictional_watch', '2026-04-20', 'fictional_watch', '2026-04-20', 'fictional_watch', '2026-04-20', NULL),
  ('demo_01', 'recovery_review_demo_01_2026-04-21', 1, '2026-04-21', 'fictional_watch', 'insufficient_evidence', 'recovery_review_v1', '2026-04-21 08:00:00', 2, 2, 2, 'fictional_watch', '2026-04-21', 'fictional_watch', '2026-04-21', 'fictional_watch', '2026-04-21', 'recovery_1');

INSERT INTO recovery_evidence (athlete_id, assessment_id, assessment_version, evidence_id, source_dataset, source_record_id, source_date, metric_code, observed_value, unit, rule_id, evaluation_status, valid_prior_days, baseline_days) VALUES
  ('demo_01', 'recovery_review_demo_01_2026-04-19', 1, 'load_ratio', 'daily_training_load', 'fictional_watch:2026-04-19', '2026-04-19', 'load_ratio', 1.15, 'ratio', 'coros_load_optimized', 'provider_band_only', NULL, NULL),
  ('demo_01', 'recovery_review_demo_01_2026-04-19', 1, 'sleep_7d', 'daily_sleep', 'fictional_watch:2026-04-19', '2026-04-19', 'main_sleep_min', 420, 'minutes', 'personal_sleep_7d_drop', 'insufficient_baseline', 0, 7),
  ('demo_01', 'recovery_review_demo_01_2026-04-19', 1, 'sleep_42d', 'daily_sleep', 'fictional_watch:2026-04-19', '2026-04-19', 'main_sleep_min', 420, 'minutes', 'personal_sleep_42d_low', 'insufficient_baseline', 0, 42),
  ('demo_01', 'recovery_review_demo_01_2026-04-19', 1, 'rhr_7d', 'daily_resting_hr', 'fictional_watch:2026-04-19', '2026-04-19', 'rhr_bpm', 56, 'bpm', 'personal_rhr_7d_rise', 'insufficient_baseline', 0, 7),
  ('demo_01', 'recovery_review_demo_01_2026-04-20', 1, 'load_ratio', 'daily_training_load', 'fictional_watch:2026-04-20', '2026-04-20', 'load_ratio', 1.067, 'ratio', 'coros_load_optimized', 'provider_band_only', NULL, NULL),
  ('demo_01', 'recovery_review_demo_01_2026-04-20', 1, 'sleep_7d', 'daily_sleep', 'fictional_watch:2026-04-20', '2026-04-20', 'main_sleep_min', 430, 'minutes', 'personal_sleep_7d_drop', 'insufficient_baseline', 1, 7),
  ('demo_01', 'recovery_review_demo_01_2026-04-20', 1, 'sleep_42d', 'daily_sleep', 'fictional_watch:2026-04-20', '2026-04-20', 'main_sleep_min', 430, 'minutes', 'personal_sleep_42d_low', 'insufficient_baseline', 1, 42),
  ('demo_01', 'recovery_review_demo_01_2026-04-20', 1, 'rhr_7d', 'daily_resting_hr', 'fictional_watch:2026-04-20', '2026-04-20', 'rhr_bpm', 55, 'bpm', 'personal_rhr_7d_rise', 'insufficient_baseline', 1, 7),
  ('demo_01', 'recovery_review_demo_01_2026-04-21', 1, 'load_ratio', 'daily_training_load', 'fictional_watch:2026-04-21', '2026-04-21', 'load_ratio', 0.983, 'ratio', 'coros_load_maintaining', 'provider_band_only', NULL, NULL),
  ('demo_01', 'recovery_review_demo_01_2026-04-21', 1, 'sleep_7d', 'daily_sleep', 'fictional_watch:2026-04-21', '2026-04-21', 'main_sleep_min', 440, 'minutes', 'personal_sleep_7d_drop', 'insufficient_baseline', 2, 7),
  ('demo_01', 'recovery_review_demo_01_2026-04-21', 1, 'sleep_42d', 'daily_sleep', 'fictional_watch:2026-04-21', '2026-04-21', 'main_sleep_min', 440, 'minutes', 'personal_sleep_42d_low', 'insufficient_baseline', 2, 42),
  ('demo_01', 'recovery_review_demo_01_2026-04-21', 1, 'rhr_7d', 'daily_resting_hr', 'fictional_watch:2026-04-21', '2026-04-21', 'rhr_bpm', 54, 'bpm', 'personal_rhr_7d_rise', 'insufficient_baseline', 2, 7),
  ('demo_01', 'recovery_review_demo_01_2026-04-21', 1, 'provider_recovery', 'recovery_observation', 'recovery_1', '2026-04-21', 'recovery_pct', 76, 'percent', 'coros_recovery_normal', 'provider_band_only', NULL, NULL);

INSERT INTO recovery_rule (rule_id, rule_kind, metric_code, lower_bound, upper_bound, lower_inclusive, upper_inclusive, label, meaning, rule_origin, source_url, baseline_days, min_valid_days) VALUES
  ('coros_recovery_exhausted', 'provider_band', 'recovery_pct', 0, 20, TRUE, FALSE, 'Exhausted', 'Rest is recommended by COROS.', 'coros', 'https://support.coros.com/hc/en-us/articles/360061452651-COROS-Fitness-Metrics-Explained', NULL, NULL),
  ('coros_recovery_fatigued', 'provider_band', 'recovery_pct', 20, 70, TRUE, FALSE, 'Fatigued', 'Provider-estimated recovery is low.', 'coros', 'https://support.coros.com/hc/en-us/articles/360061452651-COROS-Fitness-Metrics-Explained', NULL, NULL),
  ('coros_recovery_normal', 'provider_band', 'recovery_pct', 70, 90, TRUE, FALSE, 'Normal', 'Provider-estimated recovery is normal.', 'coros', 'https://support.coros.com/hc/en-us/articles/360061452651-COROS-Fitness-Metrics-Explained', NULL, NULL),
  ('coros_recovery_fresh', 'provider_band', 'recovery_pct', 90, 100, TRUE, TRUE, 'Fresh', 'Provider labels this range fresh.', 'coros', 'https://support.coros.com/hc/en-us/articles/360061452651-COROS-Fitness-Metrics-Explained', NULL, NULL),
  ('coros_load_decreasing', 'provider_band', 'load_ratio', 0, 0.5, TRUE, FALSE, 'Decreasing', 'Low recent load relative to base fitness.', 'coros', 'https://support.coros.com/hc/en-us/articles/26485283220884-EvoLab', NULL, NULL),
  ('coros_load_performance', 'provider_band', 'load_ratio', 0.5, 0.8, TRUE, FALSE, 'Resuming or Performance', 'May be appropriate during a taper; context matters.', 'coros', 'https://support.coros.com/hc/en-us/articles/26485283220884-EvoLab', NULL, NULL),
  ('coros_load_maintaining', 'provider_band', 'load_ratio', 0.8, 1.0, TRUE, FALSE, 'Maintaining', 'Moderate recent load relative to base fitness.', 'coros', 'https://support.coros.com/hc/en-us/articles/26485283220884-EvoLab', NULL, NULL),
  ('coros_load_optimized', 'provider_band', 'load_ratio', 1.0, 1.5, TRUE, FALSE, 'Optimized', 'Provider describes productive training in this range.', 'coros', 'https://support.coros.com/hc/en-us/articles/26485283220884-EvoLab', NULL, NULL),
  ('coros_load_excessive', 'provider_band', 'load_ratio', 1.5, NULL, TRUE, FALSE, 'Excessive', 'Recent load may be excessive; review recovery.', 'coros', 'https://support.coros.com/hc/en-us/articles/26485283220884-EvoLab', NULL, NULL),
  ('personal_load_high', 'personal_signal', 'load_ratio', 1.5, NULL, FALSE, FALSE, 'High load review', 'Review the next session; not an overtraining diagnosis.', 'user_configured', NULL, NULL, NULL),
  ('personal_load_low', 'personal_signal', 'load_ratio', NULL, 0.8, FALSE, FALSE, 'Low load review', 'Review goal and taper context; not automatically ineffective training.', 'user_configured', NULL, NULL, NULL),
  ('personal_sleep_42d_low', 'personal_signal', 'sleep_42d_delta_pct', NULL, -10, FALSE, FALSE, 'Long-term sleep decrease', 'Sleep duration differs from the prior 42-day mean; quality is not inferred.', 'user_configured', NULL, 42, 28),
  ('personal_sleep_42d_high', 'personal_signal', 'sleep_42d_delta_pct', 10, NULL, FALSE, FALSE, 'Long-term sleep increase', 'Sleep duration differs from the prior 42-day mean; quality is not inferred.', 'user_configured', NULL, 42, 28),
  ('personal_sleep_7d_drop', 'personal_signal', 'sleep_7d_delta_pct', NULL, -10, FALSE, FALSE, 'Recent sleep decrease', 'A recent sleep-shortening signal for fatigue review.', 'user_configured', NULL, 7, 5),
  ('personal_rhr_7d_rise', 'personal_signal', 'rhr_7d_delta_pct', 10, NULL, FALSE, FALSE, 'Recent resting-HR rise', 'A possible fatigue-related signal requiring context.', 'user_configured', NULL, 7, 5);

INSERT INTO capability_assessment (athlete_id, assessment_id, assessment_version, capability_type, review_date, status, confidence, method_version, rationale, created_at_utc) VALUES
  ('demo_01', 'capability_aerobic_capacity_20260421', 1, 'aerobic_capacity', '2026-04-21', 'baseline_only', 'contextual', 'capability_review_v1', 'One device VO2max estimate; no comparable history.', '2026-04-21 09:00:00'),
  ('demo_01', 'capability_threshold_endurance_20260421', 1, 'threshold_endurance', '2026-04-21', 'baseline_only', 'contextual', 'capability_review_v1', 'One dated threshold estimate; no comparable history.', '2026-04-21 09:00:00'),
  ('demo_01', 'capability_running_pace_capacity_20260421', 1, 'running_pace_capacity', '2026-04-21', 'baseline_only', 'contextual', 'capability_review_v1', 'One pace-zone scheme; faster future boundaries require the same method and observed-run corroboration.', '2026-04-21 09:00:00'),
  ('demo_01', 'capability_aerobic_endurance_20260421', 1, 'aerobic_endurance', '2026-04-21', 'descriptive_only', 'exploratory', 'capability_review_v1', 'Runs have different intents; pace and heart rate cannot establish a controlled trend.', '2026-04-21 09:00:00'),
  ('demo_01', 'capability_running_mechanics_20260421', 1, 'running_mechanics', '2026-04-21', 'descriptive_only', 'descriptive', 'capability_review_v1', 'Cadence differs by pace and workout purpose; no economy score is inferred.', '2026-04-21 09:00:00'),
  ('demo_01', 'capability_race_performance_20260421', 1, 'race_performance', '2026-04-21', 'observed_outcome', 'observed', 'capability_review_v1', 'One official 10K net result; no same-distance comparison yet.', '2026-04-21 09:00:00');

INSERT INTO capability_evidence (athlete_id, assessment_id, assessment_version, evidence_id, evidence_kind, metric_name, source_dataset, source_record_id, source_date, observed_value, unit, comparability_status, confidence) VALUES
  ('demo_01', 'capability_aerobic_capacity_20260421', 1, 'vo2max_running', 'provider_estimate', 'latest_vo2max_running', 'latest_fitness_measurement', 'fictional_vo2max_running', '2026-04-15', 47, 'ml/kg/min', 'single_snapshot', 'contextual'),
  ('demo_01', 'capability_threshold_endurance_20260421', 1, 'threshold_pace_s_per_km', 'provider_estimate', 'latest_threshold_pace_s_per_km', 'latest_fitness_measurement', 'fictional_threshold_pace_s_per_km', '2026-04-15', 350, 's/km', 'single_snapshot', 'contextual'),
  ('demo_01', 'capability_threshold_endurance_20260421', 1, 'threshold_hr_bpm', 'provider_estimate', 'latest_threshold_hr_bpm', 'latest_fitness_measurement', 'fictional_threshold_hr_bpm', '2026-04-15', 169, 'bpm', 'single_snapshot', 'contextual'),
  ('demo_01', 'capability_running_pace_capacity_20260421', 1, 'zone_1_fast', 'pace_zone_boundary', NULL, 'running_pace_zone', 'fictional_pace_v1:1:fast', '2026-01-01', 430, 's/km', 'single_scheme_version', 'contextual'),
  ('demo_01', 'capability_running_pace_capacity_20260421', 1, 'zone_1_slow', 'pace_zone_boundary', NULL, 'running_pace_zone', 'fictional_pace_v1:1:slow', '2026-01-01', 600, 's/km', 'single_scheme_version', 'contextual'),
  ('demo_01', 'capability_running_pace_capacity_20260421', 1, 'zone_2_fast', 'pace_zone_boundary', NULL, 'running_pace_zone', 'fictional_pace_v1:2:fast', '2026-01-01', 380, 's/km', 'single_scheme_version', 'contextual'),
  ('demo_01', 'capability_running_pace_capacity_20260421', 1, 'zone_2_slow', 'pace_zone_boundary', NULL, 'running_pace_zone', 'fictional_pace_v1:2:slow', '2026-01-01', 430, 's/km', 'single_scheme_version', 'contextual'),
  ('demo_01', 'capability_running_pace_capacity_20260421', 1, 'zone_3_fast', 'pace_zone_boundary', NULL, 'running_pace_zone', 'fictional_pace_v1:3:fast', '2026-01-01', 350, 's/km', 'single_scheme_version', 'contextual'),
  ('demo_01', 'capability_running_pace_capacity_20260421', 1, 'zone_3_slow', 'pace_zone_boundary', NULL, 'running_pace_zone', 'fictional_pace_v1:3:slow', '2026-01-01', 380, 's/km', 'single_scheme_version', 'contextual'),
  ('demo_01', 'capability_running_pace_capacity_20260421', 1, 'zone_4_fast', 'pace_zone_boundary', NULL, 'running_pace_zone', 'fictional_pace_v1:4:fast', '2026-01-01', 320, 's/km', 'single_scheme_version', 'contextual'),
  ('demo_01', 'capability_running_pace_capacity_20260421', 1, 'zone_4_slow', 'pace_zone_boundary', NULL, 'running_pace_zone', 'fictional_pace_v1:4:slow', '2026-01-01', 350, 's/km', 'single_scheme_version', 'contextual'),
  ('demo_01', 'capability_running_pace_capacity_20260421', 1, 'zone_5_fast', 'pace_zone_boundary', NULL, 'running_pace_zone', 'fictional_pace_v1:5:fast', '2026-01-01', 250, 's/km', 'single_scheme_version', 'contextual'),
  ('demo_01', 'capability_running_pace_capacity_20260421', 1, 'zone_5_slow', 'pace_zone_boundary', NULL, 'running_pace_zone', 'fictional_pace_v1:5:slow', '2026-01-01', 320, 's/km', 'single_scheme_version', 'contextual'),
  ('demo_01', 'capability_aerobic_endurance_20260421', 1, 'evt_101_pace', 'observed_run', 'measured_pace_s_per_km', 'running_observation', 'evt_101:1:1', '2026-04-06', 396.6666666666667, 's/km', 'mixed_session_intents', 'exploratory'),
  ('demo_01', 'capability_aerobic_endurance_20260421', 1, 'evt_101_heart_rate', 'observed_run', 'weighted_avg_hr_bpm', 'running_observation', 'evt_101:1:1', '2026-04-06', 143, 'bpm', 'mixed_session_intents', 'exploratory'),
  ('demo_01', 'capability_running_mechanics_20260421', 1, 'evt_101_cadence', 'observed_run', 'weighted_avg_cadence_spm', 'running_observation', 'evt_101:1:1', '2026-04-06', 166, 'spm', 'mixed_pace_and_intent', 'descriptive'),
  ('demo_01', 'capability_aerobic_endurance_20260421', 1, 'evt_102_pace', 'observed_run', 'measured_pace_s_per_km', 'running_observation', 'evt_102:1:1', '2026-04-09', 377.14285714285717, 's/km', 'mixed_session_intents', 'exploratory'),
  ('demo_01', 'capability_aerobic_endurance_20260421', 1, 'evt_102_heart_rate', 'observed_run', 'weighted_avg_hr_bpm', 'running_observation', 'evt_102:1:1', '2026-04-09', 158, 'bpm', 'mixed_session_intents', 'exploratory'),
  ('demo_01', 'capability_running_mechanics_20260421', 1, 'evt_102_cadence', 'observed_run', 'weighted_avg_cadence_spm', 'running_observation', 'evt_102:1:1', '2026-04-09', 172, 'spm', 'mixed_pace_and_intent', 'descriptive'),
  ('demo_01', 'capability_aerobic_endurance_20260421', 1, 'evt_103_pace', 'observed_run', 'measured_pace_s_per_km', 'running_observation', 'evt_103:1:1', '2026-04-13', 390.0, 's/km', 'mixed_session_intents', 'exploratory'),
  ('demo_01', 'capability_aerobic_endurance_20260421', 1, 'evt_103_heart_rate', 'observed_run', 'weighted_avg_hr_bpm', 'running_observation', 'evt_103:1:1', '2026-04-13', 147, 'bpm', 'mixed_session_intents', 'exploratory'),
  ('demo_01', 'capability_running_mechanics_20260421', 1, 'evt_103_cadence', 'observed_run', 'weighted_avg_cadence_spm', 'running_observation', 'evt_103:1:1', '2026-04-13', 168, 'spm', 'mixed_pace_and_intent', 'descriptive'),
  ('demo_01', 'capability_aerobic_endurance_20260421', 1, 'evt_104_pace', 'observed_run', 'measured_pace_s_per_km', 'running_observation', 'evt_104:1:1', '2026-04-19', 321.0, 's/km', 'mixed_session_intents', 'exploratory'),
  ('demo_01', 'capability_aerobic_endurance_20260421', 1, 'evt_104_heart_rate', 'observed_run', 'weighted_avg_hr_bpm', 'running_observation', 'evt_104:1:1', '2026-04-19', 164, 'bpm', 'mixed_session_intents', 'exploratory'),
  ('demo_01', 'capability_running_mechanics_20260421', 1, 'evt_104_cadence', 'observed_run', 'weighted_avg_cadence_spm', 'running_observation', 'evt_104:1:1', '2026-04-19', 176, 'spm', 'mixed_pace_and_intent', 'descriptive'),
  ('demo_01', 'capability_race_performance_20260421', 1, 'official_10k_net_time', 'official_race', 'official_10k_net_time_s', 'workout_event', 'evt_104', '2026-04-19', 3190, 'seconds', 'single_race', 'observed');

INSERT INTO goal_progress_assessment (athlete_id, assessment_id, assessment_version, goal_id, goal_version, criterion_id, review_date, window_start_date, window_end_date, status, observed_value, difference_value, difference_unit, comparison_basis, method_version, rationale, evaluated_at_utc) VALUES
  ('demo_01', 'synthetic_run_consistency_v1_weekly_run_days_2026-04-12', 1, 'synthetic_run_consistency', 1, 'weekly_run_days', '2026-04-12', '2026-04-06', '2026-04-12', 'achieved', 2, 0, 'days/week', 'distinct_standalone_run_days_in_completed_calendar_week', 'goal_progress_v1', 'Two distinct standalone run days in the completed calendar week.', '2026-04-12 09:00:00'),
  ('demo_01', 'synthetic_run_consistency_v2_weekly_run_days_2026-04-21', 1, 'synthetic_run_consistency', 2, 'weekly_run_days', '2026-04-21', '2026-04-13', '2026-04-19', 'needs_review', 2, -1, 'days/week', 'distinct_standalone_run_days_in_completed_calendar_week', 'goal_progress_v1', 'Two distinct standalone run days in the completed calendar week; target is three.', '2026-04-21 09:00:00'),
  ('demo_01', 'synthetic_sleep_v1_main_sleep_2026-04-21', 1, 'synthetic_sleep', 1, 'main_sleep', '2026-04-21', '2026-04-15', '2026-04-21', 'insufficient_evidence', NULL, NULL, NULL, 'rolling_7_wake_days_minimum_5', 'goal_progress_v1', 'Only three valid wake days; policy requires five before evaluating the seven-day mean.', '2026-04-21 09:00:00'),
  ('demo_02', 'synthetic_race_v1_ten_k_time_2026-04-21', 1, 'synthetic_race', 1, 'ten_k_time', '2026-04-21', NULL, '2026-04-21', 'insufficient_evidence', NULL, NULL, NULL, 'same_athlete_official_10k_net_time', 'goal_progress_v1', 'No same-athlete official 10K net result; another athlete''s race is not evidence.', '2026-04-21 09:00:00');

INSERT INTO goal_progress_evidence (athlete_id, assessment_id, assessment_version, evidence_id, source_dataset, source_record_id, source_date, metric_name, observed_value, unit, quality_status, comparison_basis) VALUES
  ('demo_01', 'synthetic_run_consistency_v1_weekly_run_days_2026-04-12', 1, 'evt_101', 'workout_event', 'evt_101', '2026-04-06', 'run_day_count', 1, 'run_day', 'canonical_standalone', 'calendar_week'),
  ('demo_01', 'synthetic_run_consistency_v1_weekly_run_days_2026-04-12', 1, 'evt_102', 'workout_event', 'evt_102', '2026-04-09', 'run_day_count', 1, 'run_day', 'canonical_standalone', 'calendar_week'),
  ('demo_01', 'synthetic_run_consistency_v2_weekly_run_days_2026-04-21', 1, 'evt_103', 'workout_event', 'evt_103', '2026-04-13', 'run_day_count', 1, 'run_day', 'canonical_standalone', 'calendar_week'),
  ('demo_01', 'synthetic_run_consistency_v2_weekly_run_days_2026-04-21', 1, 'evt_104', 'workout_event', 'evt_104', '2026-04-19', 'run_day_count', 1, 'run_day', 'canonical_standalone', 'calendar_week'),
  ('demo_01', 'synthetic_sleep_v1_main_sleep_2026-04-21', 1, '2026-04-19', 'daily_sleep', 'fictional_watch:2026-04-19', '2026-04-19', 'avg_main_sleep_minutes', 420, 'minutes', 'present_but_incomplete_window', 'wake_date'),
  ('demo_01', 'synthetic_sleep_v1_main_sleep_2026-04-21', 1, '2026-04-20', 'daily_sleep', 'fictional_watch:2026-04-20', '2026-04-20', 'avg_main_sleep_minutes', 430, 'minutes', 'present_but_incomplete_window', 'wake_date'),
  ('demo_01', 'synthetic_sleep_v1_main_sleep_2026-04-21', 1, '2026-04-21', 'daily_sleep', 'fictional_watch:2026-04-21', '2026-04-21', 'avg_main_sleep_minutes', 440, 'minutes', 'present_but_incomplete_window', 'wake_date');

INSERT INTO action_plan (athlete_id, plan_id, plan_version, goal_id, goal_version, title, plan_summary, status, approval_status, created_at_utc, approved_at_utc, revision_reason) VALUES
  ('demo_01', 'synthetic_running_plan', 1, 'synthetic_run_consistency', 1, 'Two running days per week', 'A human-approved plan direction for the initial running-consistency goal; scheduled actions are modeled separately.', 'superseded', 'approved', '2026-04-01 10:00:00', '2026-04-02 09:00:00', 'Initial plan'),
  ('demo_01', 'synthetic_running_plan', 2, 'synthetic_run_consistency', 2, 'Review three running days per week', 'Draft revision after the goal target changed; no training schedule is applied until human approval.', 'draft', 'pending', '2026-04-08 10:00:00', NULL, 'Goal target changed from two to three run days'),
  ('demo_01', 'synthetic_sleep_plan', 1, 'synthetic_sleep', 1, 'Review sleep routine', 'Draft sleep-focused plan direction awaiting sufficient evidence and human approval.', 'draft', 'pending', '2026-04-10 10:00:00', NULL, 'Initial plan'),
  ('demo_02', 'synthetic_race_plan', 1, 'synthetic_race', 1, 'Review 10K preparation', 'Draft race preparation direction; specific sessions are not yet scheduled.', 'draft', 'pending', '2026-04-05 10:00:00', NULL, 'Initial plan');

INSERT INTO planned_action (athlete_id, plan_id, plan_version, action_id, scheduled_date, action_kind, title, target_duration_min, planning_status, completion_status, candidate_event_id, verified_event_id, match_method, match_reviewed_at_utc, source) VALUES
  ('demo_01', 'synthetic_running_plan', 1, 'run_20260406', '2026-04-06', 'run', 'Easy run', 40, 'approved', 'verified_completed', NULL, 'evt_101', 'manual_verified', '2026-04-07 09:00:00', 'fictional_manual_plan'),
  ('demo_01', 'synthetic_running_plan', 1, 'run_20260409', '2026-04-09', 'run', 'Steady run', 45, 'approved', 'candidate_only', 'evt_102', NULL, 'date_sport_candidate', NULL, 'fictional_manual_plan'),
  ('demo_01', 'synthetic_running_plan', 2, 'run_20260413', '2026-04-13', 'run', 'Proposed easy run', 35, 'proposed', 'not_assessed', NULL, NULL, NULL, NULL, 'fictional_manual_plan'),
  ('demo_01', 'synthetic_running_plan', 2, 'rest_20260416', '2026-04-16', 'rest', 'Proposed rest day', NULL, 'proposed', 'not_assessed', NULL, NULL, NULL, NULL, 'fictional_manual_plan'),
  ('demo_01', 'synthetic_running_plan', 2, 'run_20260419', '2026-04-19', 'run', 'Proposed longer run', 55, 'proposed', 'not_assessed', NULL, NULL, NULL, NULL, 'fictional_manual_plan'),
  ('demo_01', 'synthetic_sleep_plan', 1, 'sleep_20260420', '2026-04-20', 'sleep_routine', 'Proposed consistent bedtime', NULL, 'proposed', 'not_assessed', NULL, NULL, NULL, NULL, 'fictional_manual_plan'),
  ('demo_02', 'synthetic_race_plan', 1, 'run_20260422', '2026-04-22', 'run', 'Proposed easy 10K preparation run', 30, 'proposed', 'not_assessed', NULL, NULL, NULL, NULL, 'fictional_manual_plan');
