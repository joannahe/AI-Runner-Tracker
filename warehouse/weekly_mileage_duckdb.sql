-- Apply once to an existing warehouse; the coverage table is intentionally empty.
CREATE SCHEMA IF NOT EXISTS fitness_demo;
SET schema 'fitness_demo';

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
