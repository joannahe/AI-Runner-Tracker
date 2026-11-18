-- COROS Training Focus: count completed running sessions by primary focus.
-- Edit week_start to review another completed local Monday-Sunday week.
-- The provider focus is a whole-session label, not time spent in a zone.
WITH parameters AS (
  SELECT DATE '2026-11-09' AS week_start, 0.20::DOUBLE AS high_fraction_limit
),
ranked AS (
  SELECT a.athlete_id, a.workout_event_id, a.activity_id, a.activity_date,
         a.training_focus,
         ROW_NUMBER() OVER (
           PARTITION BY a.athlete_id, a.workout_event_id
           ORDER BY CASE a.dedup_status WHEN 'canonical' THEN 0 ELSE 1 END,
                    a.activity_id
         ) AS pick
  FROM fitness_demo.activity AS a
  CROSS JOIN parameters AS p
  WHERE a.source = 'coros'
    AND a.sport_code = 'running'
    AND a.dedup_status IN ('canonical', 'unique')
    AND a.activity_date >= p.week_start
    AND a.activity_date < p.week_start + INTERVAL 7 DAY
),
weekly AS (
  SELECT athlete_id,
         COUNT(*) AS total_sessions,
         COUNT(*) FILTER (WHERE training_focus IN ('Recovery', 'Easy', 'Base')) AS low_sessions,
         COUNT(*) FILTER (WHERE training_focus = 'Tempo') AS moderate_sessions,
         COUNT(*) FILTER (WHERE training_focus IN ('Threshold', 'VO2 Max', 'Anaerobic')) AS high_sessions,
         COUNT(*) FILTER (WHERE training_focus IS NULL OR training_focus NOT IN
           ('Recovery', 'Easy', 'Base', 'Tempo', 'Threshold', 'VO2 Max', 'Anaerobic')) AS unknown_sessions
  FROM ranked
  WHERE pick = 1
  GROUP BY athlete_id
)
SELECT p.week_start, w.athlete_id, w.total_sessions, w.low_sessions,
       w.moderate_sessions, w.high_sessions, w.unknown_sessions,
       ROUND(100.0 * w.high_sessions / NULLIF(w.total_sessions, 0), 1) AS high_session_pct,
       CASE WHEN p.week_start + INTERVAL 7 DAY > CURRENT_DATE THEN 'INCOMPLETE_WEEK'
            WHEN w.unknown_sessions > 0 THEN 'INSUFFICIENT_FOCUS'
            WHEN w.high_sessions::DOUBLE / NULLIF(w.total_sessions, 0) > p.high_fraction_limit
              THEN 'REVIEW_DISTRIBUTION'
            ELSE 'WITHIN_CONFIGURED_SHARE' END AS review_status
FROM weekly AS w
CROSS JOIN parameters AS p
ORDER BY w.athlete_id;
