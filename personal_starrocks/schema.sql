-- Personal fitness data snapshot; load only into a new, empty local StarRocks database.

CREATE DATABASE IF NOT EXISTS `joanna_fitness`;

USE `joanna_fitness`;

CREATE TABLE `activity` (
  `athlete_id` varchar(32) NOT NULL COMMENT "",
  `activity_id` varchar(32) NOT NULL COMMENT "",
  `source_connection_id` varchar(32) NOT NULL COMMENT "",
  `source` varchar(16) NOT NULL COMMENT "",
  `sport_type` int(11) NOT NULL COMMENT "",
  `source_activity_id` varchar(128) NOT NULL COMMENT "",
  `activity_date` date NOT NULL COMMENT "Activity date in the source time zone",
  `timezone_name` varchar(64) NOT NULL COMMENT "",
  `start_ts_ms` bigint(20) NULL COMMENT "UTC Unix timestamp in milliseconds",
  `end_ts_ms` bigint(20) NULL COMMENT "",
  `title` varchar(256) NULL COMMENT "",
  `primary_recording_device_id` varchar(32) NULL COMMENT "",
  `workout_event_id` varchar(32) NULL COMMENT "",
  `sport_code` varchar(32) NULL COMMENT "Normalized sport category; original sport_type is retained",
  `origin_app_id` varchar(256) NULL COMMENT "",
  `origin_record_id` varchar(128) NULL COMMENT "",
  `dedup_status` varchar(32) NULL COMMENT "unique/confirmed_copy/pending_review",
  `workout_duration_s` decimal(16, 3) NULL COMMENT "Source Workout Time; distinct from the FIT timer",
  `elapsed_duration_s` decimal(16, 3) NULL COMMENT "Source Total Time / elapsed duration",
  `fit_timer_duration_s` decimal(16, 3) NULL COMMENT "",
  `moving_duration_s` decimal(16, 3) NULL COMMENT "",
  `distance_m` decimal(16, 3) NULL COMMENT "",
  `distance_basis` varchar(40) NULL COMMENT "activity_total/run_only/unknown",
  `avg_pace_s_per_km` decimal(12, 4) NULL COMMENT "Source average pace",
  `moving_pace_s_per_km` decimal(12, 4) NULL COMMENT "",
  `adjusted_pace_s_per_km` decimal(12, 4) NULL COMMENT "",
  `pace_distance_basis` varchar(40) NULL COMMENT "activity_distance/unknown",
  `avg_speed_m_per_s` decimal(12, 4) NULL COMMENT "",
  `avg_hr_bpm` smallint(6) NULL COMMENT "",
  `max_hr_bpm` smallint(6) NULL COMMENT "",
  `avg_cadence_spm` decimal(10, 3) NULL COMMENT "",
  `avg_power_w` decimal(10, 3) NULL COMMENT "",
  `calories_kcal` decimal(12, 3) NULL COMMENT "",
  `elevation_gain_m` decimal(12, 3) NULL COMMENT "",
  `training_load` decimal(12, 3) NULL COMMENT "",
  `aerobic_te` decimal(6, 3) NULL COMMENT "",
  `anaerobic_te` decimal(6, 3) NULL COMMENT "",
  `training_focus` varchar(64) NULL COMMENT "",
  `detail_status` varchar(24) NULL COMMENT "",
  `latest_list_snapshot_id` varchar(32) NULL COMMENT "",
  `latest_detail_snapshot_id` varchar(32) NULL COMMENT "",
  `active_lap_snapshot_id` varchar(32) NULL COMMENT "",
  `active_sample_series_id` varchar(32) NULL COMMENT "",
  `source_observed_at_utc` datetime NOT NULL COMMENT "",
  `parser_version` varchar(32) NOT NULL COMMENT "",
  `quality_flags` json NULL COMMENT "",
  `extra_metrics` json NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`athlete_id`, `activity_id`)
DISTRIBUTED BY HASH(`athlete_id`, `activity_id`) BUCKETS 1 
ORDER BY(`athlete_id`, `activity_date`, `sport_type`)
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `activity_context` (
  `athlete_id` varchar(32) NOT NULL COMMENT "",
  `activity_id` varchar(32) NOT NULL COMMENT "",
  `source_connection_id` varchar(32) NOT NULL COMMENT "",
  `source` varchar(16) NOT NULL COMMENT "",
  `sport_type` int(11) NOT NULL COMMENT "",
  `source_activity_id` varchar(128) NOT NULL COMMENT "",
  `session_intent` varchar(32) NULL COMMENT "race/easy/interval/test/unknown",
  `event_name` varchar(128) NULL COMMENT "",
  `race_format` varchar(64) NULL COMMENT "standard_hyrox_doubles/custom/unknown",
  `division` varchar(64) NULL COMMENT "",
  `partner_ref` varchar(64) NULL COMMENT "",
  `planned_work` json NULL COMMENT "",
  `official_results` json NULL COMMENT "Official result source and timing basis; keep separate from watch elapsed time",
  `annotations` json NULL COMMENT "Field-level evidence: user_confirmed, poster, or inferred, with timestamp",
  `updated_at_utc` datetime NOT NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`athlete_id`, `activity_id`)
DISTRIBUTED BY HASH(`athlete_id`, `activity_id`) BUCKETS 1 
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `activity_device` (
  `athlete_id` varchar(32) NOT NULL COMMENT "",
  `activity_id` varchar(32) NOT NULL COMMENT "",
  `device_id` varchar(32) NOT NULL COMMENT "",
  `device_role` varchar(16) NOT NULL COMMENT "Device role, such as recorder, hr_sensor, power_sensor, or footpod",
  `evidence_type` varchar(40) NOT NULL COMMENT "fit_device_info/provider_activity/user_confirmed/inferred",
  `source_snapshot_id` varchar(32) NULL COMMENT "",
  `recorded_firmware_version` varchar(64) NULL COMMENT "",
  `observed_at_utc` datetime NOT NULL COMMENT "",
  `extra_metadata` json NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`athlete_id`, `activity_id`, `device_id`, `device_role`)
DISTRIBUTED BY HASH(`athlete_id`, `activity_id`) BUCKETS 1 
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `activity_sample` (
  `athlete_id` varchar(32) NOT NULL COMMENT "",
  `activity_id` varchar(32) NOT NULL COMMENT "",
  `series_id` varchar(32) NOT NULL COMMENT "",
  `sample_index` bigint(20) NOT NULL COMMENT "",
  `source_connection_id` varchar(32) NOT NULL COMMENT "",
  `source` varchar(16) NOT NULL COMMENT "",
  `sport_type` int(11) NOT NULL COMMENT "",
  `source_activity_id` varchar(128) NOT NULL COMMENT "",
  `timestamp_ms` bigint(20) NOT NULL COMMENT "",
  `source_sample_id` varchar(128) NULL COMMENT "",
  `hr_bpm` smallint(6) NULL COMMENT "",
  `hr_device_id` varchar(32) NULL COMMENT "",
  `power_device_id` varchar(32) NULL COMMENT "",
  `cumulative_distance_m` decimal(16, 3) NULL COMMENT "",
  `speed_m_per_s` decimal(12, 4) NULL COMMENT "",
  `cadence_spm` decimal(10, 3) NULL COMMENT "",
  `power_w` decimal(10, 3) NULL COMMENT "",
  `altitude_m` decimal(12, 3) NULL COMMENT "",
  `latitude` double NULL COMMENT "",
  `longitude` double NULL COMMENT "",
  `extra_metrics` json NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`athlete_id`, `activity_id`, `series_id`, `sample_index`)
DISTRIBUTED BY HASH(`athlete_id`, `activity_id`) BUCKETS 1 
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `activity_segment` (
  `athlete_id` varchar(32) NOT NULL COMMENT "",
  `activity_id` varchar(32) NOT NULL COMMENT "",
  `lap_snapshot_id` varchar(32) NOT NULL COMMENT "",
  `lap_group_type` int(11) NOT NULL COMMENT "",
  `lap_group_ordinal` int(11) NOT NULL COMMENT "",
  `lap_ordinal` int(11) NOT NULL COMMENT "",
  `source_connection_id` varchar(32) NOT NULL COMMENT "",
  `source` varchar(16) NOT NULL COMMENT "",
  `sport_type` int(11) NOT NULL COMMENT "",
  `source_activity_id` varchar(128) NOT NULL COMMENT "",
  `source_lap_index` int(11) NULL COMMENT "",
  `source_segment_name` varchar(128) NULL COMMENT "",
  `segment_kind` varchar(32) NULL COMMENT "run/station/unknown/summary",
  `is_canonical` boolean NOT NULL COMMENT "Canonical group selected for analysis; do not sum across groups",
  `duration_s` decimal(16, 3) NULL COMMENT "",
  `distance_m` decimal(16, 3) NULL COMMENT "",
  `source_distance_raw` double NULL COMMENT "",
  `source_distance_unit` varchar(32) NULL COMMENT "",
  `distance_to_m_factor` double NULL COMMENT "",
  `distance_status` varchar(32) NULL COMMENT "validated/missing/unit_unverified",
  `avg_pace_s_per_km` decimal(12, 4) NULL COMMENT "",
  `avg_hr_bpm` smallint(6) NULL COMMENT "",
  `max_hr_bpm` smallint(6) NULL COMMENT "",
  `avg_cadence_spm` decimal(10, 3) NULL COMMENT "",
  `avg_power_w` decimal(10, 3) NULL COMMENT "",
  `parser_version` varchar(32) NOT NULL COMMENT "",
  `quality_flags` json NULL COMMENT "",
  `extra_metrics` json NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`athlete_id`, `activity_id`, `lap_snapshot_id`, `lap_group_type`, `lap_group_ordinal`, `lap_ordinal`)
DISTRIBUTED BY HASH(`athlete_id`, `activity_id`) BUCKETS 1 
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `athlete` (
  `athlete_id` varchar(32) NOT NULL COMMENT "Immutable platform UUID; do not use nickname or email as the primary key",
  `display_name` varchar(128) NULL COMMENT "",
  `birth_date` date NULL COMMENT "",
  `gender_code` varchar(24) NULL COMMENT "Platform profile value: female, male, other, or unknown",
  `timezone_name` varchar(64) NOT NULL COMMENT "",
  `profile_source_connection_id` varchar(32) NULL COMMENT "",
  `profile_source_snapshot_id` varchar(32) NULL COMMENT "",
  `profile_observed_at_utc` datetime NULL COMMENT "",
  `created_at_utc` datetime NOT NULL COMMENT "",
  `updated_at_utc` datetime NOT NULL COMMENT "",
  `extra_profile` json NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`athlete_id`)
DISTRIBUTED BY HASH(`athlete_id`) BUCKETS 1 
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `athlete_body_measurement` (
  `athlete_id` varchar(32) NOT NULL COMMENT "",
  `measurement_id` varchar(32) NOT NULL COMMENT "",
  `metric_code` varchar(40) NOT NULL COMMENT "Measurement type, such as height_cm, weight_kg, body_fat_pct, or vo2max_ml_kg_min",
  `metric_value` decimal(16, 6) NOT NULL COMMENT "",
  `unit` varchar(32) NOT NULL COMMENT "",
  `measured_at_utc` datetime NULL COMMENT "Actual measurement time; do not substitute the fetch time",
  `effective_from_utc` datetime NULL COMMENT "Effective time explicitly stated by the user or source; may be null",
  `observed_at_utc` datetime NOT NULL COMMENT "",
  `source` varchar(16) NOT NULL COMMENT "",
  `source_connection_id` varchar(32) NULL COMMENT "",
  `device_id` varchar(32) NULL COMMENT "Set only when the measurement device is known",
  `source_measurement_id` varchar(128) NULL COMMENT "",
  `source_snapshot_id` varchar(32) NULL COMMENT "",
  `measurement_method` varchar(40) NULL COMMENT "Measurement method, such as account_profile, manual, scale, or lab",
  `time_quality` varchar(32) NOT NULL COMMENT "measured_time_known/effective_time_known/observed_only",
  `quality_flags` json NULL COMMENT "",
  `extra_metadata` json NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`athlete_id`, `measurement_id`)
DISTRIBUTED BY HASH(`athlete_id`) BUCKETS 1 
ORDER BY(`athlete_id`, `metric_code`, `observed_at_utc`)
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `athlete_daily_hrv` (
  `athlete_id` varchar(255) NOT NULL COMMENT "",
  `source` varchar(255) NOT NULL COMMENT "",
  `wake_date` date NOT NULL COMMENT "",
  `hrv_avg_ms` decimal(18, 3) NULL COMMENT "",
  `normal_low_ms` decimal(18, 3) NULL COMMENT "",
  `normal_high_ms` decimal(18, 3) NULL COMMENT "",
  `baseline_ms` decimal(18, 3) NULL COMMENT "",
  `provider_evaluation` varchar(255) NULL COMMENT "",
  `data_status` varchar(255) NULL COMMENT "",
  `observed_at_utc` datetime NULL COMMENT "",
  `source_snapshot_id` varchar(255) NULL COMMENT ""
) ENGINE=OLAP 
DUPLICATE KEY(`athlete_id`, `source`, `wake_date`)
DISTRIBUTED BY HASH(`athlete_id`) BUCKETS 1 
PROPERTIES (
"compression" = "LZ4",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `athlete_daily_resting_hr` (
  `athlete_id` varchar(32) NOT NULL COMMENT "",
  `source` varchar(16) NOT NULL COMMENT "",
  `local_date` date NOT NULL COMMENT "",
  `rhr_bpm` decimal(8, 3) NULL COMMENT "",
  `data_status` varchar(16) NOT NULL COMMENT "",
  `observed_at_utc` datetime NOT NULL COMMENT "",
  `source_snapshot_id` varchar(32) NOT NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`athlete_id`, `source`, `local_date`)
DISTRIBUTED BY HASH(`athlete_id`, `local_date`) BUCKETS 1 
ORDER BY(`athlete_id`, `local_date`)
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `athlete_daily_sleep` (
  `athlete_id` varchar(32) NOT NULL COMMENT "",
  `source` varchar(16) NOT NULL COMMENT "",
  `wake_date` date NOT NULL COMMENT "",
  `data_status` varchar(24) NOT NULL COMMENT "",
  `source_score_raw` int(11) NULL COMMENT "",
  `sleep_score` int(11) NULL COMMENT "",
  `daily_sleep_min` int(11) NULL COMMENT "",
  `main_sleep_min` int(11) NULL COMMENT "",
  `main_period_min` int(11) NULL COMMENT "",
  `nap_sleep_min` int(11) NULL COMMENT "",
  `deep_pct` decimal(7, 3) NULL COMMENT "",
  `light_pct` decimal(7, 3) NULL COMMENT "",
  `rem_pct` decimal(7, 3) NULL COMMENT "",
  `awake_pct` decimal(7, 3) NULL COMMENT "",
  `awake_min` int(11) NULL COMMENT "",
  `awake_count` int(11) NULL COMMENT "",
  `metrics_scope` varchar(16) NULL COMMENT "",
  `main_start_local` datetime NULL COMMENT "",
  `main_end_local` datetime NULL COMMENT "",
  `quality_flags` json NULL COMMENT "",
  `observed_at_utc` datetime NOT NULL COMMENT "",
  `source_snapshot_id` varchar(32) NOT NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`athlete_id`, `source`, `wake_date`)
DISTRIBUTED BY HASH(`athlete_id`, `wake_date`) BUCKETS 1 
ORDER BY(`athlete_id`, `wake_date`)
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `athlete_daily_training_load` (
  `athlete_id` varchar(32) NOT NULL COMMENT "",
  `source` varchar(16) NOT NULL COMMENT "",
  `local_date` date NOT NULL COMMENT "",
  `short_term_load` decimal(12, 3) NULL COMMENT "",
  `long_term_load` decimal(12, 3) NULL COMMENT "",
  `load_ratio` decimal(10, 4) NULL COMMENT "",
  `provider_status` varchar(32) NULL COMMENT "",
  `observed_at_utc` datetime NOT NULL COMMENT "",
  `source_snapshot_id` varchar(32) NOT NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`athlete_id`, `source`, `local_date`)
DISTRIBUTED BY HASH(`athlete_id`, `local_date`) BUCKETS 1 
ORDER BY(`athlete_id`, `local_date`)
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `athlete_device_binding` (
  `athlete_id` varchar(32) NOT NULL COMMENT "",
  `binding_id` varchar(32) NOT NULL COMMENT "",
  `device_id` varchar(32) NOT NULL COMMENT "",
  `source_connection_id` varchar(32) NULL COMMENT "",
  `source_device_id` varchar(128) NULL COMMENT "",
  `relationship_type` varchar(32) NOT NULL COMMENT "Device relationship: account_bound, owned, borrowed, or shared",
  `status` varchar(24) NOT NULL COMMENT "",
  `valid_from_utc` datetime NULL COMMENT "",
  `valid_to_utc` datetime NULL COMMENT "",
  `first_observed_at_utc` datetime NOT NULL COMMENT "",
  `last_observed_at_utc` datetime NOT NULL COMMENT "",
  `evidence_type` varchar(40) NOT NULL COMMENT "",
  `source_snapshot_id` varchar(32) NULL COMMENT "",
  `extra_metadata` json NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`athlete_id`, `binding_id`)
DISTRIBUTED BY HASH(`athlete_id`) BUCKETS 1 
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `athlete_hr_zone` (
  `athlete_id` varchar(32) NOT NULL COMMENT "",
  `zone_scheme_id` varchar(32) NOT NULL COMMENT "",
  `zone_index` int(11) NOT NULL COMMENT "",
  `sport_code` varchar(32) NOT NULL COMMENT "",
  `scheme_method` varchar(32) NOT NULL COMMENT "Zone calculation method, such as absolute_bpm, max_hr, lthr, or hrr",
  `valid_from_utc` datetime NOT NULL COMMENT "",
  `valid_to_utc` datetime NULL COMMENT "",
  `lower_inclusive_bpm` decimal(8, 3) NOT NULL COMMENT "",
  `upper_exclusive_bpm` decimal(8, 3) NULL COMMENT "",
  `evidence` json NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`athlete_id`, `zone_scheme_id`, `zone_index`)
DISTRIBUTED BY HASH(`athlete_id`) BUCKETS 1 
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `athlete_pace_zone` (
  `athlete_id` varchar(32) NOT NULL COMMENT "",
  `zone_scheme_id` varchar(32) NOT NULL COMMENT "",
  `zone_index` int(11) NOT NULL COMMENT "",
  `sport_code` varchar(32) NOT NULL COMMENT "",
  `scheme_method` varchar(32) NOT NULL COMMENT "",
  `valid_from_utc` datetime NOT NULL COMMENT "",
  `valid_to_utc` datetime NULL COMMENT "",
  `fast_boundary_s_per_km` decimal(10, 3) NULL COMMENT "",
  `slow_boundary_s_per_km` decimal(10, 3) NULL COMMENT "",
  `evidence` json NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`athlete_id`, `zone_scheme_id`, `zone_index`)
DISTRIBUTED BY HASH(`athlete_id`) BUCKETS 1 
ORDER BY(`athlete_id`, `zone_scheme_id`, `zone_index`)
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `athlete_recovery_observation` (
  `athlete_id` varchar(32) NOT NULL COMMENT "",
  `observation_id` varchar(32) NOT NULL COMMENT "",
  `source` varchar(16) NOT NULL COMMENT "",
  `observed_at_utc` datetime NOT NULL COMMENT "",
  `recovery_pct` decimal(7, 3) NULL COMMENT "",
  `recovery_level` varchar(32) NULL COMMENT "",
  `estimated_full_recovery_h` decimal(8, 3) NULL COMMENT "",
  `source_snapshot_id` varchar(32) NOT NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`athlete_id`, `observation_id`)
DISTRIBUTED BY HASH(`athlete_id`, `observation_id`) BUCKETS 1 
ORDER BY(`athlete_id`, `observed_at_utc`)
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `device` (
  `device_id` varchar(32) NOT NULL COMMENT "Internal platform device UUID",
  `manufacturer` varchar(64) NULL COMMENT "",
  `model_name` varchar(128) NULL COMMENT "",
  `device_type` varchar(32) NULL COMMENT "watch/hr_strap/power_meter/footpod/scale/unknown",
  `hardware_serial` varchar(128) NULL COMMENT "",
  `firmware_version` varchar(64) NULL COMMENT "",
  `first_observed_at_utc` datetime NOT NULL COMMENT "",
  `last_observed_at_utc` datetime NOT NULL COMMENT "",
  `source_snapshot_id` varchar(32) NULL COMMENT "",
  `extra_metadata` json NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`device_id`)
DISTRIBUTED BY HASH(`device_id`) BUCKETS 1 
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `exercise_definition` (
  `exercise_code` varchar(40) NOT NULL COMMENT "",
  `name_zh` varchar(80) NOT NULL COMMENT "",
  `exercise_family` varchar(32) NOT NULL COMMENT "run/station/other",
  `aliases` json NULL COMMENT "",
  `notes` varchar(512) NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`exercise_code`)
DISTRIBUTED BY HASH(`exercise_code`) BUCKETS 1 
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `exercise_segment` (
  `athlete_id` varchar(32) NOT NULL COMMENT "",
  `workout_event_id` varchar(32) NOT NULL COMMENT "",
  `analysis_revision` bigint(20) NOT NULL COMMENT "",
  `segment_ordinal` int(11) NOT NULL COMMENT "",
  `source_activity_id_internal` varchar(32) NOT NULL COMMENT "",
  `run_index` int(11) NULL COMMENT "",
  `station_index` int(11) NULL COMMENT "",
  `segment_kind` varchar(24) NOT NULL COMMENT "run/station/transition/rest/other/unknown",
  `exercise_code` varchar(40) NULL COMMENT "",
  `exercise_identity_evidence` varchar(32) NOT NULL COMMENT "provider_named/user_confirmed/inferred/unknown",
  `run_context` varchar(24) NULL COMMENT "standalone/hybrid",
  `phase_kind` varchar(24) NULL COMMENT "warmup/work/recovery/cooldown/unknown",
  `run_environment` varchar(24) NULL COMMENT "outdoor/indoor/track/unknown",
  `start_ts_ms` bigint(20) NULL COMMENT "",
  `end_ts_ms` bigint(20) NULL COMMENT "",
  `segment_started_at_local` datetime NULL COMMENT "",
  `segment_local_date` date NULL COMMENT "",
  `segment_time_quality` varchar(32) NOT NULL COMMENT "source_timestamp/aligned_timer_events/event_date_only/unknown",
  `duration_s` decimal(16, 3) NULL COMMENT "",
  `duration_basis` varchar(32) NOT NULL COMMENT "workout_time/watch_segment/elapsed/moving/unknown",
  `measured_distance_m` decimal(16, 3) NULL COMMENT "",
  `planned_distance_m` decimal(16, 3) NULL COMMENT "",
  `distance_status` varchar(32) NOT NULL COMMENT "validated/missing/unverified",
  `reported_pace_s_per_km` decimal(12, 4) NULL COMMENT "",
  `pace_time_s` decimal(16, 3) NULL COMMENT "Time numerator using the same basis as pace_distance_m",
  `pace_distance_m` decimal(16, 3) NULL COMMENT "Include only measured distance with a matching timing basis",
  `pace_basis` varchar(32) NULL COMMENT "",
  `avg_hr_bpm` decimal(8, 3) NULL COMMENT "",
  `hr_weighted_sum_bpm_s` double NULL COMMENT "",
  `hr_weight_s` decimal(16, 3) NULL COMMENT "",
  `hr_sample_coverage_s` decimal(16, 3) NULL COMMENT "Seconds covered by valid samples; null when only a mean is available",
  `hr_aggregation_method` varchar(40) NULL COMMENT "sample_integral/provider_mean_weighted/unknown",
  `avg_cadence_spm` decimal(10, 3) NULL COMMENT "",
  `cadence_weighted_sum_spm_s` double NULL COMMENT "",
  `cadence_weight_s` decimal(16, 3) NULL COMMENT "",
  `cadence_sample_coverage_s` decimal(16, 3) NULL COMMENT "",
  `cadence_aggregation_method` varchar(40) NULL COMMENT "",
  `cadence_definition` varchar(40) NULL COMMENT "Cadence definition, such as bilateral_steps_per_min or unknown",
  `repetitions` int(11) NULL COMMENT "",
  `prescribed_repetitions` int(11) NULL COMMENT "",
  `load_total_kg` decimal(10, 3) NULL COMMENT "",
  `load_per_hand_kg` decimal(10, 3) NULL COMMENT "",
  `load_includes_sled` boolean NULL COMMENT "",
  `completion_scope` varchar(24) NULL COMMENT "individual/team/unknown",
  `includes_transition` boolean NULL COMMENT "",
  `comparison_conditions_verified` boolean NOT NULL COMMENT "True only after required distance, repetitions, load, and rules are verified",
  `comparison_group_key` varchar(64) NULL COMMENT "Group key for strict like-for-like comparison; create only after conditions are verified",
  `official_station_finish_s` decimal(16, 3) NULL COMMENT "",
  `official_penalty_s` decimal(12, 3) NULL COMMENT "",
  `watch_station_time_s` decimal(16, 3) NULL COMMENT "",
  `source_lap_snapshot_id` varchar(32) NULL COMMENT "",
  `source_lap_group_ordinal` int(11) NULL COMMENT "",
  `source_lap_ordinal` int(11) NULL COMMENT "",
  `source_sample_series_id` varchar(32) NULL COMMENT "",
  `metric_provenance` json NULL COMMENT "",
  `quality_flags` json NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`athlete_id`, `workout_event_id`, `analysis_revision`, `segment_ordinal`)
DISTRIBUTED BY HASH(`athlete_id`, `workout_event_id`) BUCKETS 1 
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `segment_hr_zone_time` (
  `athlete_id` varchar(32) NOT NULL COMMENT "",
  `workout_event_id` varchar(32) NOT NULL COMMENT "",
  `analysis_revision` bigint(20) NOT NULL COMMENT "",
  `segment_ordinal` int(11) NOT NULL COMMENT "",
  `zone_scheme_id` varchar(32) NOT NULL COMMENT "",
  `zone_index` int(11) NOT NULL COMMENT "",
  `zone_seconds` decimal(16, 3) NOT NULL COMMENT "",
  `source_sample_series_id` varchar(32) NOT NULL COMMENT "",
  `integration_method` varchar(40) NOT NULL COMMENT "",
  `gap_policy` json NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`athlete_id`, `workout_event_id`, `analysis_revision`, `segment_ordinal`, `zone_scheme_id`, `zone_index`)
DISTRIBUTED BY HASH(`athlete_id`, `workout_event_id`) BUCKETS 1 
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `segment_rule_mapping` (
  `athlete_id` varchar(32) NOT NULL COMMENT "",
  `workout_event_id` varchar(32) NOT NULL COMMENT "",
  `analysis_revision` bigint(20) NOT NULL COMMENT "",
  `segment_ordinal` int(11) NOT NULL COMMENT "",
  `rule_id` varchar(64) NOT NULL COMMENT "",
  `rule_segment_ordinal` int(11) NOT NULL COMMENT "",
  `rule_match_status` varchar(48) NOT NULL COMMENT "",
  `event_rule_season_verified` boolean NOT NULL COMMENT "",
  `evidence` json NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`athlete_id`, `workout_event_id`, `analysis_revision`, `segment_ordinal`)
DISTRIBUTED BY HASH(`athlete_id`, `workout_event_id`) BUCKETS 1 
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `sport_rule_segment` (
  `rule_id` varchar(64) NOT NULL COMMENT "",
  `rule_segment_ordinal` int(11) NOT NULL COMMENT "",
  `exercise_code` varchar(40) NOT NULL COMMENT "",
  `reference_distance_m` decimal(16, 3) NULL COMMENT "",
  `prescribed_repetitions` int(11) NULL COMMENT "",
  `distance_basis` varchar(32) NOT NULL COMMENT "",
  `source_url` varchar(512) NOT NULL COMMENT "",
  `retrieved_on` date NOT NULL COMMENT "",
  `source_season` varchar(16) NOT NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`rule_id`, `rule_segment_ordinal`)
DISTRIBUTED BY HASH(`rule_id`) BUCKETS 1 
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE TABLE `workout_event` (
  `athlete_id` varchar(32) NOT NULL COMMENT "",
  `workout_event_id` varchar(32) NOT NULL COMMENT "One real workout; cross-platform copies map to the same event",
  `preferred_activity_id` varchar(32) NOT NULL COMMENT "",
  `active_analysis_revision` bigint(20) NOT NULL COMMENT "",
  `event_date` date NOT NULL COMMENT "",
  `started_at_local` datetime NULL COMMENT "",
  `timezone_name` varchar(64) NOT NULL COMMENT "",
  `sport_code` varchar(32) NOT NULL COMMENT "Normalized category, such as running, hybrid_fitness, or cycling",
  `session_intent` varchar(32) NOT NULL COMMENT "race/easy/interval/test/unknown",
  `is_official_race` boolean NULL COMMENT "Confirmed official race; does not imply an official result is available",
  `event_name` varchar(128) NULL COMMENT "",
  `race_format_code` varchar(64) NULL COMMENT "standard_hyrox/custom_hybrid/unknown",
  `rule_set_version` varchar(64) NULL COMMENT "",
  `division_code` varchar(64) NULL COMMENT "",
  `participation_mode` varchar(24) NULL COMMENT "singles/doubles/relay/unknown",
  `partner_ref` varchar(64) NULL COMMENT "",
  `watch_elapsed_s` decimal(16, 3) NULL COMMENT "",
  `official_finish_s` decimal(16, 3) NULL COMMENT "",
  `official_penalty_s` decimal(12, 3) NULL COMMENT "",
  `classification_evidence` json NULL COMMENT "",
  `updated_at_utc` datetime NOT NULL COMMENT ""
) ENGINE=OLAP 
PRIMARY KEY(`athlete_id`, `workout_event_id`)
DISTRIBUTED BY HASH(`athlete_id`, `workout_event_id`) BUCKETS 1 
ORDER BY(`athlete_id`, `event_date`, `sport_code`)
PROPERTIES (
"compression" = "LZ4",
"enable_persistent_index" = "true",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "1"
);

CREATE VIEW `v_current_exercise_segment` (`athlete_id`, `workout_event_id`, `analysis_revision`, `segment_ordinal`, `source_activity_id_internal`, `run_index`, `station_index`, `segment_kind`, `exercise_code`, `exercise_identity_evidence`, `run_context`, `phase_kind`, `run_environment`, `start_ts_ms`, `end_ts_ms`, `segment_started_at_local`, `segment_local_date`, `segment_time_quality`, `duration_s`, `duration_basis`, `measured_distance_m`, `planned_distance_m`, `distance_status`, `reported_pace_s_per_km`, `pace_time_s`, `pace_distance_m`, `pace_basis`, `avg_hr_bpm`, `hr_weighted_sum_bpm_s`, `hr_weight_s`, `hr_sample_coverage_s`, `hr_aggregation_method`, `avg_cadence_spm`, `cadence_weighted_sum_spm_s`, `cadence_weight_s`, `cadence_sample_coverage_s`, `cadence_aggregation_method`, `cadence_definition`, `repetitions`, `prescribed_repetitions`, `load_total_kg`, `load_per_hand_kg`, `load_includes_sled`, `completion_scope`, `includes_transition`, `comparison_conditions_verified`, `comparison_group_key`, `official_station_finish_s`, `official_penalty_s`, `watch_station_time_s`, `source_lap_snapshot_id`, `source_lap_group_ordinal`, `source_lap_ordinal`, `source_sample_series_id`, `metric_provenance`, `quality_flags`, `event_date`, `started_at_local`, `timezone_name`, `sport_code`, `observation_date`, `observation_date_basis`, `session_intent`, `is_official_race`, `event_name`, `race_format_code`, `rule_set_version`, `division_code`, `participation_mode`, `partner_ref`) SECURITY NONE AS SELECT `joanna_fitness`.`s`.`athlete_id`, `joanna_fitness`.`s`.`workout_event_id`, `joanna_fitness`.`s`.`analysis_revision`, `joanna_fitness`.`s`.`segment_ordinal`, `joanna_fitness`.`s`.`source_activity_id_internal`, `joanna_fitness`.`s`.`run_index`, `joanna_fitness`.`s`.`station_index`, `joanna_fitness`.`s`.`segment_kind`, `joanna_fitness`.`s`.`exercise_code`, `joanna_fitness`.`s`.`exercise_identity_evidence`, `joanna_fitness`.`s`.`run_context`, `joanna_fitness`.`s`.`phase_kind`, `joanna_fitness`.`s`.`run_environment`, `joanna_fitness`.`s`.`start_ts_ms`, `joanna_fitness`.`s`.`end_ts_ms`, `joanna_fitness`.`s`.`segment_started_at_local`, `joanna_fitness`.`s`.`segment_local_date`, `joanna_fitness`.`s`.`segment_time_quality`, `joanna_fitness`.`s`.`duration_s`, `joanna_fitness`.`s`.`duration_basis`, `joanna_fitness`.`s`.`measured_distance_m`, `joanna_fitness`.`s`.`planned_distance_m`, `joanna_fitness`.`s`.`distance_status`, `joanna_fitness`.`s`.`reported_pace_s_per_km`, `joanna_fitness`.`s`.`pace_time_s`, `joanna_fitness`.`s`.`pace_distance_m`, `joanna_fitness`.`s`.`pace_basis`, `joanna_fitness`.`s`.`avg_hr_bpm`, `joanna_fitness`.`s`.`hr_weighted_sum_bpm_s`, `joanna_fitness`.`s`.`hr_weight_s`, `joanna_fitness`.`s`.`hr_sample_coverage_s`, `joanna_fitness`.`s`.`hr_aggregation_method`, `joanna_fitness`.`s`.`avg_cadence_spm`, `joanna_fitness`.`s`.`cadence_weighted_sum_spm_s`, `joanna_fitness`.`s`.`cadence_weight_s`, `joanna_fitness`.`s`.`cadence_sample_coverage_s`, `joanna_fitness`.`s`.`cadence_aggregation_method`, `joanna_fitness`.`s`.`cadence_definition`, `joanna_fitness`.`s`.`repetitions`, `joanna_fitness`.`s`.`prescribed_repetitions`, `joanna_fitness`.`s`.`load_total_kg`, `joanna_fitness`.`s`.`load_per_hand_kg`, `joanna_fitness`.`s`.`load_includes_sled`, `joanna_fitness`.`s`.`completion_scope`, `joanna_fitness`.`s`.`includes_transition`, `joanna_fitness`.`s`.`comparison_conditions_verified`, `joanna_fitness`.`s`.`comparison_group_key`, `joanna_fitness`.`s`.`official_station_finish_s`, `joanna_fitness`.`s`.`official_penalty_s`, `joanna_fitness`.`s`.`watch_station_time_s`, `joanna_fitness`.`s`.`source_lap_snapshot_id`, `joanna_fitness`.`s`.`source_lap_group_ordinal`, `joanna_fitness`.`s`.`source_lap_ordinal`, `joanna_fitness`.`s`.`source_sample_series_id`, `joanna_fitness`.`s`.`metric_provenance`, `joanna_fitness`.`s`.`quality_flags`, `joanna_fitness`.`e`.`event_date`, `joanna_fitness`.`e`.`started_at_local`, `joanna_fitness`.`e`.`timezone_name`, `joanna_fitness`.`e`.`sport_code`, coalesce(`joanna_fitness`.`s`.`segment_local_date`, `joanna_fitness`.`e`.`event_date`) AS `observation_date`, CASE WHEN (`joanna_fitness`.`s`.`segment_local_date` IS NOT NULL) THEN 'segment_start' ELSE 'event_date_fallback' END AS `observation_date_basis`, `joanna_fitness`.`e`.`session_intent`, `joanna_fitness`.`e`.`is_official_race`, `joanna_fitness`.`e`.`event_name`, `joanna_fitness`.`e`.`race_format_code`, `joanna_fitness`.`e`.`rule_set_version`, `joanna_fitness`.`e`.`division_code`, `joanna_fitness`.`e`.`participation_mode`, `joanna_fitness`.`e`.`partner_ref`
FROM `joanna_fitness`.`exercise_segment` AS `s` INNER JOIN `joanna_fitness`.`workout_event` AS `e` ON ((`joanna_fitness`.`s`.`athlete_id` = `joanna_fitness`.`e`.`athlete_id`) AND (`joanna_fitness`.`s`.`workout_event_id` = `joanna_fitness`.`e`.`workout_event_id`)) AND (`joanna_fitness`.`s`.`analysis_revision` = `joanna_fitness`.`e`.`active_analysis_revision`);

CREATE VIEW `v_current_segments` (`athlete_id`, `activity_id`, `lap_snapshot_id`, `lap_group_type`, `lap_group_ordinal`, `lap_ordinal`, `source_connection_id`, `source`, `sport_type`, `source_activity_id`, `source_lap_index`, `source_segment_name`, `segment_kind`, `is_canonical`, `duration_s`, `distance_m`, `source_distance_raw`, `source_distance_unit`, `distance_to_m_factor`, `distance_status`, `avg_pace_s_per_km`, `avg_hr_bpm`, `max_hr_bpm`, `avg_cadence_spm`, `avg_power_w`, `parser_version`, `quality_flags`, `extra_metrics`) SECURITY NONE AS SELECT `joanna_fitness`.`s`.`athlete_id`, `joanna_fitness`.`s`.`activity_id`, `joanna_fitness`.`s`.`lap_snapshot_id`, `joanna_fitness`.`s`.`lap_group_type`, `joanna_fitness`.`s`.`lap_group_ordinal`, `joanna_fitness`.`s`.`lap_ordinal`, `joanna_fitness`.`s`.`source_connection_id`, `joanna_fitness`.`s`.`source`, `joanna_fitness`.`s`.`sport_type`, `joanna_fitness`.`s`.`source_activity_id`, `joanna_fitness`.`s`.`source_lap_index`, `joanna_fitness`.`s`.`source_segment_name`, `joanna_fitness`.`s`.`segment_kind`, `joanna_fitness`.`s`.`is_canonical`, `joanna_fitness`.`s`.`duration_s`, `joanna_fitness`.`s`.`distance_m`, `joanna_fitness`.`s`.`source_distance_raw`, `joanna_fitness`.`s`.`source_distance_unit`, `joanna_fitness`.`s`.`distance_to_m_factor`, `joanna_fitness`.`s`.`distance_status`, `joanna_fitness`.`s`.`avg_pace_s_per_km`, `joanna_fitness`.`s`.`avg_hr_bpm`, `joanna_fitness`.`s`.`max_hr_bpm`, `joanna_fitness`.`s`.`avg_cadence_spm`, `joanna_fitness`.`s`.`avg_power_w`, `joanna_fitness`.`s`.`parser_version`, `joanna_fitness`.`s`.`quality_flags`, `joanna_fitness`.`s`.`extra_metrics`
FROM `joanna_fitness`.`activity_segment` AS `s` INNER JOIN `joanna_fitness`.`activity` AS `a` ON ((`joanna_fitness`.`s`.`athlete_id` = `joanna_fitness`.`a`.`athlete_id`) AND (`joanna_fitness`.`s`.`activity_id` = `joanna_fitness`.`a`.`activity_id`)) AND (`joanna_fitness`.`s`.`lap_snapshot_id` = `joanna_fitness`.`a`.`active_lap_snapshot_id`);

CREATE VIEW `v_latest_body_measurement` (`athlete_id`, `measurement_id`, `metric_code`, `metric_value`, `unit`, `measured_at_utc`, `effective_from_utc`, `observed_at_utc`, `time_quality`, `source`) SECURITY NONE AS SELECT `ranked`.`athlete_id`, `ranked`.`measurement_id`, `ranked`.`metric_code`, `ranked`.`metric_value`, `ranked`.`unit`, `ranked`.`measured_at_utc`, `ranked`.`effective_from_utc`, `ranked`.`observed_at_utc`, `ranked`.`time_quality`, `ranked`.`source`
FROM (SELECT `joanna_fitness`.`m`.`athlete_id`, `joanna_fitness`.`m`.`measurement_id`, `joanna_fitness`.`m`.`metric_code`, `joanna_fitness`.`m`.`metric_value`, `joanna_fitness`.`m`.`unit`, `joanna_fitness`.`m`.`measured_at_utc`, `joanna_fitness`.`m`.`effective_from_utc`, `joanna_fitness`.`m`.`observed_at_utc`, `joanna_fitness`.`m`.`source`, `joanna_fitness`.`m`.`source_connection_id`, `joanna_fitness`.`m`.`device_id`, `joanna_fitness`.`m`.`source_measurement_id`, `joanna_fitness`.`m`.`source_snapshot_id`, `joanna_fitness`.`m`.`measurement_method`, `joanna_fitness`.`m`.`time_quality`, `joanna_fitness`.`m`.`quality_flags`, `joanna_fitness`.`m`.`extra_metadata`, row_number() OVER (PARTITION BY `joanna_fitness`.`m`.`athlete_id`, `joanna_fitness`.`m`.`metric_code` ORDER BY `joanna_fitness`.`m`.`observed_at_utc` DESC, `joanna_fitness`.`m`.`measurement_id` DESC ) AS `rn`
FROM `joanna_fitness`.`athlete_body_measurement` AS `m`) `ranked`
WHERE `ranked`.`rn` = 1;

CREATE VIEW `v_running_activity` (`athlete_id`, `activity_id`, `source_connection_id`, `source`, `sport_type`, `source_activity_id`, `activity_date`, `timezone_name`, `start_ts_ms`, `end_ts_ms`, `title`, `primary_recording_device_id`, `workout_event_id`, `sport_code`, `origin_app_id`, `origin_record_id`, `dedup_status`, `workout_duration_s`, `elapsed_duration_s`, `fit_timer_duration_s`, `moving_duration_s`, `distance_m`, `distance_basis`, `avg_pace_s_per_km`, `moving_pace_s_per_km`, `adjusted_pace_s_per_km`, `pace_distance_basis`, `avg_speed_m_per_s`, `avg_hr_bpm`, `max_hr_bpm`, `avg_cadence_spm`, `avg_power_w`, `calories_kcal`, `elevation_gain_m`, `training_load`, `aerobic_te`, `anaerobic_te`, `training_focus`, `detail_status`, `latest_list_snapshot_id`, `latest_detail_snapshot_id`, `active_lap_snapshot_id`, `active_sample_series_id`, `source_observed_at_utc`, `parser_version`, `quality_flags`, `extra_metrics`, `session_intent`, `event_name`) SECURITY NONE AS SELECT `joanna_fitness`.`a`.`athlete_id`, `joanna_fitness`.`a`.`activity_id`, `joanna_fitness`.`a`.`source_connection_id`, `joanna_fitness`.`a`.`source`, `joanna_fitness`.`a`.`sport_type`, `joanna_fitness`.`a`.`source_activity_id`, `joanna_fitness`.`a`.`activity_date`, `joanna_fitness`.`a`.`timezone_name`, `joanna_fitness`.`a`.`start_ts_ms`, `joanna_fitness`.`a`.`end_ts_ms`, `joanna_fitness`.`a`.`title`, `joanna_fitness`.`a`.`primary_recording_device_id`, `joanna_fitness`.`a`.`workout_event_id`, `joanna_fitness`.`a`.`sport_code`, `joanna_fitness`.`a`.`origin_app_id`, `joanna_fitness`.`a`.`origin_record_id`, `joanna_fitness`.`a`.`dedup_status`, `joanna_fitness`.`a`.`workout_duration_s`, `joanna_fitness`.`a`.`elapsed_duration_s`, `joanna_fitness`.`a`.`fit_timer_duration_s`, `joanna_fitness`.`a`.`moving_duration_s`, `joanna_fitness`.`a`.`distance_m`, `joanna_fitness`.`a`.`distance_basis`, `joanna_fitness`.`a`.`avg_pace_s_per_km`, `joanna_fitness`.`a`.`moving_pace_s_per_km`, `joanna_fitness`.`a`.`adjusted_pace_s_per_km`, `joanna_fitness`.`a`.`pace_distance_basis`, `joanna_fitness`.`a`.`avg_speed_m_per_s`, `joanna_fitness`.`a`.`avg_hr_bpm`, `joanna_fitness`.`a`.`max_hr_bpm`, `joanna_fitness`.`a`.`avg_cadence_spm`, `joanna_fitness`.`a`.`avg_power_w`, `joanna_fitness`.`a`.`calories_kcal`, `joanna_fitness`.`a`.`elevation_gain_m`, `joanna_fitness`.`a`.`training_load`, `joanna_fitness`.`a`.`aerobic_te`, `joanna_fitness`.`a`.`anaerobic_te`, `joanna_fitness`.`a`.`training_focus`, `joanna_fitness`.`a`.`detail_status`, `joanna_fitness`.`a`.`latest_list_snapshot_id`, `joanna_fitness`.`a`.`latest_detail_snapshot_id`, `joanna_fitness`.`a`.`active_lap_snapshot_id`, `joanna_fitness`.`a`.`active_sample_series_id`, `joanna_fitness`.`a`.`source_observed_at_utc`, `joanna_fitness`.`a`.`parser_version`, `joanna_fitness`.`a`.`quality_flags`, `joanna_fitness`.`a`.`extra_metrics`, `joanna_fitness`.`c`.`session_intent`, `joanna_fitness`.`c`.`event_name`
FROM `joanna_fitness`.`activity` AS `a` LEFT OUTER JOIN `joanna_fitness`.`activity_context` AS `c` ON (`joanna_fitness`.`a`.`athlete_id` = `joanna_fitness`.`c`.`athlete_id`) AND (`joanna_fitness`.`a`.`activity_id` = `joanna_fitness`.`c`.`activity_id`)
WHERE (`joanna_fitness`.`a`.`sport_type` IN (100, 101, 102, 103)) AND (`joanna_fitness`.`a`.`source` = 'coros');

CREATE VIEW `v_hyrox_race_station` (`athlete_id`, `workout_event_id`, `analysis_revision`, `segment_ordinal`, `source_activity_id_internal`, `run_index`, `station_index`, `segment_kind`, `exercise_code`, `exercise_identity_evidence`, `run_context`, `phase_kind`, `run_environment`, `start_ts_ms`, `end_ts_ms`, `segment_started_at_local`, `segment_local_date`, `segment_time_quality`, `duration_s`, `duration_basis`, `measured_distance_m`, `planned_distance_m`, `distance_status`, `reported_pace_s_per_km`, `pace_time_s`, `pace_distance_m`, `pace_basis`, `avg_hr_bpm`, `hr_weighted_sum_bpm_s`, `hr_weight_s`, `hr_sample_coverage_s`, `hr_aggregation_method`, `avg_cadence_spm`, `cadence_weighted_sum_spm_s`, `cadence_weight_s`, `cadence_sample_coverage_s`, `cadence_aggregation_method`, `cadence_definition`, `repetitions`, `prescribed_repetitions`, `load_total_kg`, `load_per_hand_kg`, `load_includes_sled`, `completion_scope`, `includes_transition`, `comparison_conditions_verified`, `comparison_group_key`, `official_station_finish_s`, `official_penalty_s`, `watch_station_time_s`, `source_lap_snapshot_id`, `source_lap_group_ordinal`, `source_lap_ordinal`, `source_sample_series_id`, `metric_provenance`, `quality_flags`, `event_date`, `started_at_local`, `timezone_name`, `sport_code`, `observation_date`, `observation_date_basis`, `session_intent`, `is_official_race`, `event_name`, `race_format_code`, `rule_set_version`, `division_code`, `participation_mode`, `partner_ref`, `exercise_name_zh`) SECURITY NONE AS SELECT `joanna_fitness`.`s`.`athlete_id`, `joanna_fitness`.`s`.`workout_event_id`, `joanna_fitness`.`s`.`analysis_revision`, `joanna_fitness`.`s`.`segment_ordinal`, `joanna_fitness`.`s`.`source_activity_id_internal`, `joanna_fitness`.`s`.`run_index`, `joanna_fitness`.`s`.`station_index`, `joanna_fitness`.`s`.`segment_kind`, `joanna_fitness`.`s`.`exercise_code`, `joanna_fitness`.`s`.`exercise_identity_evidence`, `joanna_fitness`.`s`.`run_context`, `joanna_fitness`.`s`.`phase_kind`, `joanna_fitness`.`s`.`run_environment`, `joanna_fitness`.`s`.`start_ts_ms`, `joanna_fitness`.`s`.`end_ts_ms`, `joanna_fitness`.`s`.`segment_started_at_local`, `joanna_fitness`.`s`.`segment_local_date`, `joanna_fitness`.`s`.`segment_time_quality`, `joanna_fitness`.`s`.`duration_s`, `joanna_fitness`.`s`.`duration_basis`, `joanna_fitness`.`s`.`measured_distance_m`, `joanna_fitness`.`s`.`planned_distance_m`, `joanna_fitness`.`s`.`distance_status`, `joanna_fitness`.`s`.`reported_pace_s_per_km`, `joanna_fitness`.`s`.`pace_time_s`, `joanna_fitness`.`s`.`pace_distance_m`, `joanna_fitness`.`s`.`pace_basis`, `joanna_fitness`.`s`.`avg_hr_bpm`, `joanna_fitness`.`s`.`hr_weighted_sum_bpm_s`, `joanna_fitness`.`s`.`hr_weight_s`, `joanna_fitness`.`s`.`hr_sample_coverage_s`, `joanna_fitness`.`s`.`hr_aggregation_method`, `joanna_fitness`.`s`.`avg_cadence_spm`, `joanna_fitness`.`s`.`cadence_weighted_sum_spm_s`, `joanna_fitness`.`s`.`cadence_weight_s`, `joanna_fitness`.`s`.`cadence_sample_coverage_s`, `joanna_fitness`.`s`.`cadence_aggregation_method`, `joanna_fitness`.`s`.`cadence_definition`, `joanna_fitness`.`s`.`repetitions`, `joanna_fitness`.`s`.`prescribed_repetitions`, `joanna_fitness`.`s`.`load_total_kg`, `joanna_fitness`.`s`.`load_per_hand_kg`, `joanna_fitness`.`s`.`load_includes_sled`, `joanna_fitness`.`s`.`completion_scope`, `joanna_fitness`.`s`.`includes_transition`, `joanna_fitness`.`s`.`comparison_conditions_verified`, `joanna_fitness`.`s`.`comparison_group_key`, `joanna_fitness`.`s`.`official_station_finish_s`, `joanna_fitness`.`s`.`official_penalty_s`, `joanna_fitness`.`s`.`watch_station_time_s`, `joanna_fitness`.`s`.`source_lap_snapshot_id`, `joanna_fitness`.`s`.`source_lap_group_ordinal`, `joanna_fitness`.`s`.`source_lap_ordinal`, `joanna_fitness`.`s`.`source_sample_series_id`, `joanna_fitness`.`s`.`metric_provenance`, `joanna_fitness`.`s`.`quality_flags`, `joanna_fitness`.`s`.`event_date`, `joanna_fitness`.`s`.`started_at_local`, `joanna_fitness`.`s`.`timezone_name`, `joanna_fitness`.`s`.`sport_code`, `joanna_fitness`.`s`.`observation_date`, `joanna_fitness`.`s`.`observation_date_basis`, `joanna_fitness`.`s`.`session_intent`, `joanna_fitness`.`s`.`is_official_race`, `joanna_fitness`.`s`.`event_name`, `joanna_fitness`.`s`.`race_format_code`, `joanna_fitness`.`s`.`rule_set_version`, `joanna_fitness`.`s`.`division_code`, `joanna_fitness`.`s`.`participation_mode`, `joanna_fitness`.`s`.`partner_ref`, `joanna_fitness`.`d`.`name_zh` AS `exercise_name_zh`
FROM `joanna_fitness`.`v_current_exercise_segment` AS `s` INNER JOIN `joanna_fitness`.`exercise_definition` AS `d` ON `joanna_fitness`.`s`.`exercise_code` = `joanna_fitness`.`d`.`exercise_code`
WHERE ((((`joanna_fitness`.`s`.`segment_kind` = 'station') AND (`joanna_fitness`.`s`.`session_intent` = 'race')) AND (`joanna_fitness`.`s`.`is_official_race` = TRUE)) AND (`joanna_fitness`.`s`.`sport_code` = 'hybrid_fitness')) AND (`joanna_fitness`.`s`.`exercise_identity_evidence` IN ('provider_named', 'user_confirmed', 'official_result'));

CREATE VIEW `v_running_observation` (`athlete_id`, `workout_event_id`, `analysis_revision`, `segment_ordinal`, `source_activity_id_internal`, `run_index`, `station_index`, `segment_kind`, `exercise_code`, `exercise_identity_evidence`, `run_context`, `phase_kind`, `run_environment`, `start_ts_ms`, `end_ts_ms`, `segment_started_at_local`, `segment_local_date`, `segment_time_quality`, `duration_s`, `duration_basis`, `measured_distance_m`, `planned_distance_m`, `distance_status`, `reported_pace_s_per_km`, `pace_time_s`, `pace_distance_m`, `pace_basis`, `avg_hr_bpm`, `hr_weighted_sum_bpm_s`, `hr_weight_s`, `hr_sample_coverage_s`, `hr_aggregation_method`, `avg_cadence_spm`, `cadence_weighted_sum_spm_s`, `cadence_weight_s`, `cadence_sample_coverage_s`, `cadence_aggregation_method`, `cadence_definition`, `repetitions`, `prescribed_repetitions`, `load_total_kg`, `load_per_hand_kg`, `load_includes_sled`, `completion_scope`, `includes_transition`, `comparison_conditions_verified`, `comparison_group_key`, `official_station_finish_s`, `official_penalty_s`, `watch_station_time_s`, `source_lap_snapshot_id`, `source_lap_group_ordinal`, `source_lap_ordinal`, `source_sample_series_id`, `metric_provenance`, `quality_flags`, `event_date`, `started_at_local`, `timezone_name`, `sport_code`, `observation_date`, `observation_date_basis`, `session_intent`, `is_official_race`, `event_name`, `race_format_code`, `rule_set_version`, `division_code`, `participation_mode`, `partner_ref`, `measured_pace_s_per_km`) SECURITY NONE AS SELECT `joanna_fitness`.`s`.`athlete_id`, `joanna_fitness`.`s`.`workout_event_id`, `joanna_fitness`.`s`.`analysis_revision`, `joanna_fitness`.`s`.`segment_ordinal`, `joanna_fitness`.`s`.`source_activity_id_internal`, `joanna_fitness`.`s`.`run_index`, `joanna_fitness`.`s`.`station_index`, `joanna_fitness`.`s`.`segment_kind`, `joanna_fitness`.`s`.`exercise_code`, `joanna_fitness`.`s`.`exercise_identity_evidence`, `joanna_fitness`.`s`.`run_context`, `joanna_fitness`.`s`.`phase_kind`, `joanna_fitness`.`s`.`run_environment`, `joanna_fitness`.`s`.`start_ts_ms`, `joanna_fitness`.`s`.`end_ts_ms`, `joanna_fitness`.`s`.`segment_started_at_local`, `joanna_fitness`.`s`.`segment_local_date`, `joanna_fitness`.`s`.`segment_time_quality`, `joanna_fitness`.`s`.`duration_s`, `joanna_fitness`.`s`.`duration_basis`, `joanna_fitness`.`s`.`measured_distance_m`, `joanna_fitness`.`s`.`planned_distance_m`, `joanna_fitness`.`s`.`distance_status`, `joanna_fitness`.`s`.`reported_pace_s_per_km`, `joanna_fitness`.`s`.`pace_time_s`, `joanna_fitness`.`s`.`pace_distance_m`, `joanna_fitness`.`s`.`pace_basis`, `joanna_fitness`.`s`.`avg_hr_bpm`, `joanna_fitness`.`s`.`hr_weighted_sum_bpm_s`, `joanna_fitness`.`s`.`hr_weight_s`, `joanna_fitness`.`s`.`hr_sample_coverage_s`, `joanna_fitness`.`s`.`hr_aggregation_method`, `joanna_fitness`.`s`.`avg_cadence_spm`, `joanna_fitness`.`s`.`cadence_weighted_sum_spm_s`, `joanna_fitness`.`s`.`cadence_weight_s`, `joanna_fitness`.`s`.`cadence_sample_coverage_s`, `joanna_fitness`.`s`.`cadence_aggregation_method`, `joanna_fitness`.`s`.`cadence_definition`, `joanna_fitness`.`s`.`repetitions`, `joanna_fitness`.`s`.`prescribed_repetitions`, `joanna_fitness`.`s`.`load_total_kg`, `joanna_fitness`.`s`.`load_per_hand_kg`, `joanna_fitness`.`s`.`load_includes_sled`, `joanna_fitness`.`s`.`completion_scope`, `joanna_fitness`.`s`.`includes_transition`, `joanna_fitness`.`s`.`comparison_conditions_verified`, `joanna_fitness`.`s`.`comparison_group_key`, `joanna_fitness`.`s`.`official_station_finish_s`, `joanna_fitness`.`s`.`official_penalty_s`, `joanna_fitness`.`s`.`watch_station_time_s`, `joanna_fitness`.`s`.`source_lap_snapshot_id`, `joanna_fitness`.`s`.`source_lap_group_ordinal`, `joanna_fitness`.`s`.`source_lap_ordinal`, `joanna_fitness`.`s`.`source_sample_series_id`, `joanna_fitness`.`s`.`metric_provenance`, `joanna_fitness`.`s`.`quality_flags`, `joanna_fitness`.`s`.`event_date`, `joanna_fitness`.`s`.`started_at_local`, `joanna_fitness`.`s`.`timezone_name`, `joanna_fitness`.`s`.`sport_code`, `joanna_fitness`.`s`.`observation_date`, `joanna_fitness`.`s`.`observation_date_basis`, `joanna_fitness`.`s`.`session_intent`, `joanna_fitness`.`s`.`is_official_race`, `joanna_fitness`.`s`.`event_name`, `joanna_fitness`.`s`.`race_format_code`, `joanna_fitness`.`s`.`rule_set_version`, `joanna_fitness`.`s`.`division_code`, `joanna_fitness`.`s`.`participation_mode`, `joanna_fitness`.`s`.`partner_ref`, CASE WHEN ((`joanna_fitness`.`s`.`pace_distance_m` > 0) AND (`joanna_fitness`.`s`.`pace_time_s` IS NOT NULL)) THEN ((`joanna_fitness`.`s`.`pace_time_s` * 1000) / `joanna_fitness`.`s`.`pace_distance_m`) ELSE NULL END AS `measured_pace_s_per_km`
FROM `joanna_fitness`.`v_current_exercise_segment` AS `s`
WHERE `joanna_fitness`.`s`.`segment_kind` = 'run';

CREATE VIEW `v_running_rule_reference` (`athlete_id`, `workout_event_id`, `analysis_revision`, `segment_ordinal`, `source_activity_id_internal`, `run_index`, `station_index`, `segment_kind`, `exercise_code`, `exercise_identity_evidence`, `run_context`, `phase_kind`, `run_environment`, `start_ts_ms`, `end_ts_ms`, `segment_started_at_local`, `segment_local_date`, `segment_time_quality`, `duration_s`, `duration_basis`, `measured_distance_m`, `planned_distance_m`, `distance_status`, `reported_pace_s_per_km`, `pace_time_s`, `pace_distance_m`, `pace_basis`, `avg_hr_bpm`, `hr_weighted_sum_bpm_s`, `hr_weight_s`, `hr_sample_coverage_s`, `hr_aggregation_method`, `avg_cadence_spm`, `cadence_weighted_sum_spm_s`, `cadence_weight_s`, `cadence_sample_coverage_s`, `cadence_aggregation_method`, `cadence_definition`, `repetitions`, `prescribed_repetitions`, `load_total_kg`, `load_per_hand_kg`, `load_includes_sled`, `completion_scope`, `includes_transition`, `comparison_conditions_verified`, `comparison_group_key`, `official_station_finish_s`, `official_penalty_s`, `watch_station_time_s`, `source_lap_snapshot_id`, `source_lap_group_ordinal`, `source_lap_ordinal`, `source_sample_series_id`, `metric_provenance`, `quality_flags`, `event_date`, `started_at_local`, `timezone_name`, `sport_code`, `observation_date`, `observation_date_basis`, `session_intent`, `is_official_race`, `event_name`, `race_format_code`, `rule_set_version`, `division_code`, `participation_mode`, `partner_ref`, `measured_pace_s_per_km`, `rule_id`, `rule_match_status`, `event_rule_season_verified`, `reference_distance_m`, `reference_distance_basis`, `rule_reference_pace_s_per_km`) SECURITY NONE AS SELECT `joanna_fitness`.`s`.`athlete_id`, `joanna_fitness`.`s`.`workout_event_id`, `joanna_fitness`.`s`.`analysis_revision`, `joanna_fitness`.`s`.`segment_ordinal`, `joanna_fitness`.`s`.`source_activity_id_internal`, `joanna_fitness`.`s`.`run_index`, `joanna_fitness`.`s`.`station_index`, `joanna_fitness`.`s`.`segment_kind`, `joanna_fitness`.`s`.`exercise_code`, `joanna_fitness`.`s`.`exercise_identity_evidence`, `joanna_fitness`.`s`.`run_context`, `joanna_fitness`.`s`.`phase_kind`, `joanna_fitness`.`s`.`run_environment`, `joanna_fitness`.`s`.`start_ts_ms`, `joanna_fitness`.`s`.`end_ts_ms`, `joanna_fitness`.`s`.`segment_started_at_local`, `joanna_fitness`.`s`.`segment_local_date`, `joanna_fitness`.`s`.`segment_time_quality`, `joanna_fitness`.`s`.`duration_s`, `joanna_fitness`.`s`.`duration_basis`, `joanna_fitness`.`s`.`measured_distance_m`, `joanna_fitness`.`s`.`planned_distance_m`, `joanna_fitness`.`s`.`distance_status`, `joanna_fitness`.`s`.`reported_pace_s_per_km`, `joanna_fitness`.`s`.`pace_time_s`, `joanna_fitness`.`s`.`pace_distance_m`, `joanna_fitness`.`s`.`pace_basis`, `joanna_fitness`.`s`.`avg_hr_bpm`, `joanna_fitness`.`s`.`hr_weighted_sum_bpm_s`, `joanna_fitness`.`s`.`hr_weight_s`, `joanna_fitness`.`s`.`hr_sample_coverage_s`, `joanna_fitness`.`s`.`hr_aggregation_method`, `joanna_fitness`.`s`.`avg_cadence_spm`, `joanna_fitness`.`s`.`cadence_weighted_sum_spm_s`, `joanna_fitness`.`s`.`cadence_weight_s`, `joanna_fitness`.`s`.`cadence_sample_coverage_s`, `joanna_fitness`.`s`.`cadence_aggregation_method`, `joanna_fitness`.`s`.`cadence_definition`, `joanna_fitness`.`s`.`repetitions`, `joanna_fitness`.`s`.`prescribed_repetitions`, `joanna_fitness`.`s`.`load_total_kg`, `joanna_fitness`.`s`.`load_per_hand_kg`, `joanna_fitness`.`s`.`load_includes_sled`, `joanna_fitness`.`s`.`completion_scope`, `joanna_fitness`.`s`.`includes_transition`, `joanna_fitness`.`s`.`comparison_conditions_verified`, `joanna_fitness`.`s`.`comparison_group_key`, `joanna_fitness`.`s`.`official_station_finish_s`, `joanna_fitness`.`s`.`official_penalty_s`, `joanna_fitness`.`s`.`watch_station_time_s`, `joanna_fitness`.`s`.`source_lap_snapshot_id`, `joanna_fitness`.`s`.`source_lap_group_ordinal`, `joanna_fitness`.`s`.`source_lap_ordinal`, `joanna_fitness`.`s`.`source_sample_series_id`, `joanna_fitness`.`s`.`metric_provenance`, `joanna_fitness`.`s`.`quality_flags`, `joanna_fitness`.`s`.`event_date`, `joanna_fitness`.`s`.`started_at_local`, `joanna_fitness`.`s`.`timezone_name`, `joanna_fitness`.`s`.`sport_code`, `joanna_fitness`.`s`.`observation_date`, `joanna_fitness`.`s`.`observation_date_basis`, `joanna_fitness`.`s`.`session_intent`, `joanna_fitness`.`s`.`is_official_race`, `joanna_fitness`.`s`.`event_name`, `joanna_fitness`.`s`.`race_format_code`, `joanna_fitness`.`s`.`rule_set_version`, `joanna_fitness`.`s`.`division_code`, `joanna_fitness`.`s`.`participation_mode`, `joanna_fitness`.`s`.`partner_ref`, `joanna_fitness`.`s`.`measured_pace_s_per_km`, `joanna_fitness`.`m`.`rule_id`, `joanna_fitness`.`m`.`rule_match_status`, `joanna_fitness`.`m`.`event_rule_season_verified`, `joanna_fitness`.`r`.`reference_distance_m`, `joanna_fitness`.`r`.`distance_basis` AS `reference_distance_basis`, CASE WHEN ((`joanna_fitness`.`r`.`reference_distance_m` > 0) AND (`joanna_fitness`.`s`.`duration_s` IS NOT NULL)) THEN ((`joanna_fitness`.`s`.`duration_s` * 1000.0) / `joanna_fitness`.`r`.`reference_distance_m`) ELSE NULL END AS `rule_reference_pace_s_per_km`
FROM `joanna_fitness`.`v_running_observation` AS `s` INNER JOIN `joanna_fitness`.`segment_rule_mapping` AS `m` ON (((`joanna_fitness`.`s`.`athlete_id` = `joanna_fitness`.`m`.`athlete_id`) AND (`joanna_fitness`.`s`.`workout_event_id` = `joanna_fitness`.`m`.`workout_event_id`)) AND (`joanna_fitness`.`s`.`analysis_revision` = `joanna_fitness`.`m`.`analysis_revision`)) AND (`joanna_fitness`.`s`.`segment_ordinal` = `joanna_fitness`.`m`.`segment_ordinal`) INNER JOIN `joanna_fitness`.`sport_rule_segment` AS `r` ON ((`joanna_fitness`.`m`.`rule_id` = `joanna_fitness`.`r`.`rule_id`) AND (`joanna_fitness`.`m`.`rule_segment_ordinal` = `joanna_fitness`.`r`.`rule_segment_ordinal`)) AND (`joanna_fitness`.`s`.`exercise_code` = `joanna_fitness`.`r`.`exercise_code`)
WHERE (((`joanna_fitness`.`m`.`rule_match_status` = 'named_sequence_matched_reference') AND (`joanna_fitness`.`s`.`is_official_race` = TRUE)) AND (`joanna_fitness`.`s`.`race_format_code` = 'standard_hyrox')) AND (`joanna_fitness`.`s`.`participation_mode` = 'doubles');
