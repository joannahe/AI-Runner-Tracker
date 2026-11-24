"""Idempotent local DuckDB migration for versioned training-plan details."""


ACTION_COLUMNS = {
    "title_zh": "VARCHAR",
    "target_distance_km": "DECIMAL(8,2)",
    "target_distance_min_km": "DECIMAL(8,2)",
    "target_distance_max_km": "DECIMAL(8,2)",
    "distance_basis": "VARCHAR",
}


def ensure_plan_detail_schema(db):
    existing = {row[0] for row in db.execute("DESCRIBE fitness_demo.planned_action").fetchall()}
    for name, kind in ACTION_COLUMNS.items():
        if name not in existing:
            db.execute(f"ALTER TABLE fitness_demo.planned_action ADD COLUMN {name} {kind}")
    db.execute("""CREATE TABLE IF NOT EXISTS fitness_demo.planned_action_segment (
        athlete_id VARCHAR, plan_id VARCHAR, plan_version BIGINT, action_id VARCHAR,
        segment_ordinal BIGINT, segment_type VARCHAR, title_en VARCHAR, title_zh VARCHAR,
        target_duration_min BIGINT, target_distance_km DECIMAL(8,2),
        target_pace_fast_s_per_km BIGINT, target_pace_slow_s_per_km BIGINT,
        target_hr_low_bpm BIGINT, target_hr_high_bpm BIGINT
    )""")
