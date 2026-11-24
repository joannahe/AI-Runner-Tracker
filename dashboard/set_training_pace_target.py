"""Save a versioned athlete-selected training pace target in DuckDB.

This is a coaching target, separate from COROS's measured threshold estimate.
The existing running_pace_zone semantic dataset exposes the saved range.
"""

import argparse
from datetime import date, datetime, time, timezone
from pathlib import Path
from uuid import uuid4

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "personal_duckdb" / "joanna_fitness.duckdb"


def pace_seconds(value):
    minutes, separator, seconds = value.partition(":")
    if separator != ":" or not minutes.isdigit() or not seconds.isdigit() or len(seconds) != 2:
        raise argparse.ArgumentTypeError("Use m:ss per km, such as 5:30")
    total = int(minutes) * 60 + int(seconds)
    if int(seconds) >= 60 or total <= 0:
        raise argparse.ArgumentTypeError("Invalid pace")
    return total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--fast", type=pace_seconds, required=True)
    parser.add_argument("--slow", type=pace_seconds, required=True)
    parser.add_argument("--effective-date", type=date.fromisoformat, required=True)
    parser.add_argument("--athlete-id", help="Required only if the database has multiple athletes")
    args = parser.parse_args()
    if args.fast > args.slow:
        parser.error("Fast pace must be less than or equal to slow pace in seconds/km")
    if not args.db.is_file():
        parser.error("DuckDB file does not exist")
    with duckdb.connect(str(args.db)) as db:
        athletes = [row[0] for row in db.execute("SELECT athlete_id FROM fitness_demo.athlete").fetchall()]
        if args.athlete_id:
            if args.athlete_id not in athletes:
                parser.error("athlete_id does not exist")
            athlete = args.athlete_id
        elif len(athletes) == 1:
            athlete = athletes[0]
        else:
            parser.error("Multiple athletes found; supply --athlete-id")
        effective_at = datetime.combine(args.effective_date, time.min, tzinfo=timezone.utc).replace(tzinfo=None)
        scheme_id = f"user_threshold_{args.effective_date.isoformat()}_{uuid4().hex[:8]}"
        db.begin()
        try:
            db.execute("""UPDATE fitness_demo.athlete_pace_zone SET valid_to_utc=?
                WHERE athlete_id=? AND sport_code='running' AND zone_index=4
                  AND scheme_method='user_threshold_target' AND valid_to_utc IS NULL""",
                [effective_at, athlete])
            db.execute("""INSERT INTO fitness_demo.athlete_pace_zone
                (athlete_id,zone_scheme_id,zone_index,sport_code,scheme_method,
                 valid_from_utc,valid_to_utc,fast_boundary_s_per_km,slow_boundary_s_per_km)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                [athlete, scheme_id, 4, "running", "user_threshold_target",
                 effective_at, None, args.fast, args.slow])
            db.commit()
        except Exception:
            db.rollback()
            raise
    print(f"Saved user threshold training target {args.fast//60}:{args.fast%60:02d}–"
          f"{args.slow//60}:{args.slow%60:02d}/km from {args.effective_date}; scheme={scheme_id}")


if __name__ == "__main__":
    main()
