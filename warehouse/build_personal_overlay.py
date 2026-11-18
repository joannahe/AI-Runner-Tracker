"""Build a DOSI-model-compatible DuckDB sample with the owner's historical data.

The refreshed source snapshot is read-only. The fictional fixture remains
untouched. Re-running rebuilds the same separate output file.
"""

from pathlib import Path
import os
import shutil

import duckdb


ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / 'warehouse/running_demo.duckdb'
SNAPSHOT = ROOT / 'personal_duckdb/joanna_fitness.duckdb'
OUT = ROOT / 'warehouse/running_demo_personal.duckdb'
TMP = OUT.with_suffix('.building.duckdb')
COMPAT = OUT.with_suffix('.compat-building.duckdb')


def columns(conn, database, name):
    prefix = '' if database == 'main' else database + '.'
    return [r[0] for r in conn.execute(f'DESCRIBE {prefix}fitness_demo.{name}').fetchall()]


def copy_columns(conn, source_db, source_table, target_table, where=''):
    common = [c for c in columns(conn, 'main', target_table)
              if c in columns(conn, source_db, source_table)]
    if not common:
        raise RuntimeError(f'No matching fields: {source_table} → {target_table}')
    names = ', '.join('"' + c + '"' for c in common)
    conn.execute(f'''INSERT INTO fitness_demo.{target_table} ({names})
                     SELECT {names} FROM {source_db}.fitness_demo.{source_table} {where}''')
    return conn.execute('SELECT COUNT(*) FROM fitness_demo.' + target_table).fetchone()[0]


def main():
    if TMP.exists():
        TMP.unlink()
    shutil.copy2(FIXTURE, TMP)
    conn = duckdb.connect(str(TMP))
    try:
        conn.execute(f"ATTACH '{SNAPSHOT}' AS history (READ_ONLY)")
        conn.execute('BEGIN TRANSACTION')

        # The historical StarRocks snapshot is the canonical source of workout IDs.
        for table in [
            'athlete', 'workout_event', 'activity', 'activity_segment',
            'athlete_daily_training_load', 'athlete_daily_sleep',
            'athlete_daily_resting_hr', 'athlete_daily_hrv', 'athlete_hr_zone',
            'athlete_recovery_observation',
        ]:
            copy_columns(conn, 'history', table, table)
        for source, target in [
            ('v_running_observation', 'running_observation_fact'),
            ('v_hyrox_race_station', 'hyrox_station_fact'),
            ('v_running_rule_reference', 'running_rule_reference_fact'),
        ]:
            copy_columns(conn, 'history', source, target)

        athlete_ids = [r[0] for r in conn.execute(
            'SELECT athlete_id FROM history.fitness_demo.athlete').fetchall()]
        if len(athlete_ids) != 1:
            raise RuntimeError('Historical snapshot must contain one owner')
        canonical = athlete_ids[0]
        # Personal HRV is present, but no calculated RecoveryState is
        # fabricated. The evaluator must produce dated evidence-backed reviews.
        historical_workouts = conn.execute(
            'SELECT COUNT(*) FROM history.fitness_demo.workout_event').fetchone()[0]
        checks = {
            'athlete': 1,
            'athlete_daily_hrv': 166,
            'workout_event': historical_workouts,
        }
        for table, expected in checks.items():
            got = conn.execute(f'SELECT COUNT(*) FROM fitness_demo.{table} WHERE athlete_id=?',
                               [canonical]).fetchone()[0]
            if got != expected:
                raise RuntimeError(f'{table}: expected {expected}, got {got}')
        count, distinct_days, first, last = conn.execute('''
            SELECT COUNT(*), COUNT(DISTINCT wake_date), MIN(wake_date), MAX(wake_date)
            FROM fitness_demo.athlete_daily_hrv WHERE athlete_id=?''',
            [canonical]).fetchone()
        if count != 166 or distinct_days != 166:
            raise RuntimeError('HRV date uniqueness failed')
        conn.execute('COMMIT')
        print('Built', OUT.name)
        print('Owner workouts', checks['workout_event'])
        print('Owner HRV', count, 'days', first, 'to', last)
        for table in ['activity', 'athlete_daily_training_load',
                      'athlete_daily_sleep', 'athlete_daily_resting_hr',
                      'running_observation_fact', 'hyrox_station_fact']:
            print(table, conn.execute(f'''SELECT COUNT(*) FROM fitness_demo.{table}
                                         WHERE athlete_id=?''', [canonical]).fetchone()[0])
    except:
        try: conn.execute('ROLLBACK')
        except: pass
        raise
    finally:
        conn.close()
    # The installed DOSI engine embeds an older DuckDB reader. DuckDB 2.x
    # otherwise writes files that DOSI cannot open. Copy into a compatible
    # storage version without changing the upstream snapshot.
    if COMPAT.exists():
        COMPAT.unlink()
    with duckdb.connect() as converter:
        converter.execute("ATTACH ? AS source_db (READ_ONLY)", [str(TMP)])
        converter.execute("ATTACH ? AS compatible (STORAGE_VERSION 'v1.2.0')", [str(COMPAT)])
        converter.execute('COPY FROM DATABASE source_db TO compatible')
    os.replace(COMPAT, OUT)
    TMP.unlink()


if __name__ == '__main__':
    main()
