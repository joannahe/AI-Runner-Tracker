"""Export the personal DOSI overlay as an additive StarRocks fixture seed.

Run after starrocks_schema.sql and starrocks_seed.sql in an empty fitness_demo
database. This includes personal health data and must be reviewed before release.
"""

import base64
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import re

import duckdb


ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / 'warehouse/running_demo_personal.duckdb'
SNAPSHOT = ROOT / 'personal_duckdb/joanna_fitness.duckdb'
OUT = ROOT / 'warehouse/starrocks_personal_seed.sql'
IDENT = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def literal(value):
    if value is None:
        return 'NULL'
    if isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    if isinstance(value, (int, float, Decimal)):
        return str(value)
    if isinstance(value, datetime):
        return "'" + value.isoformat(sep=' ') + "'"
    if isinstance(value, date):
        return "'" + value.isoformat() + "'"
    encoded = base64.b64encode(str(value).encode('utf-8')).decode('ascii')
    return f"from_base64('{encoded}')"


def main():
    with duckdb.connect(str(SNAPSHOT), read_only=True) as source:
        athlete_ids = [r[0] for r in source.execute('SELECT athlete_id FROM fitness_demo.athlete').fetchall()]
    if len(athlete_ids) != 1:
        raise RuntimeError('Expected one owner in the personal snapshot')
    owner = athlete_ids[0]
    statements = [
        '-- Additional personal data for the generic DOSI fixture. Contains identifying health information.',
        '-- Apply once, after starrocks_schema.sql and starrocks_seed.sql, to an empty database.',
        'USE fitness_demo;',
    ]
    counts = {}
    with duckdb.connect(str(DB), read_only=True) as conn:
        names = [r[0] for r in conn.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema='fitness_demo' AND table_type='BASE TABLE'
            ORDER BY table_name""").fetchall()]
        for table in names:
            if not IDENT.fullmatch(table):
                raise ValueError('Unexpected table name')
            columns = [r[0] for r in conn.execute(f'DESCRIBE fitness_demo."{table}"').fetchall()]
            if 'athlete_id' not in columns:
                continue
            if any(not IDENT.fullmatch(col) for col in columns):
                raise ValueError('Unexpected column name')
            records = conn.execute(
                f'SELECT * FROM fitness_demo."{table}" WHERE athlete_id=?', [owner]
            ).fetchall()
            counts[table] = len(records)
            if not records:
                continue
            col_sql = ', '.join('`' + col + '`' for col in columns)
            for start in range(0, len(records), 40):
                batch = records[start:start + 40]
                values = ['(' + ', '.join(literal(v) for v in row) + ')' for row in batch]
                statements.append(
                    f'INSERT INTO `{table}` ({col_sql}) VALUES\n' + ',\n'.join(values) + ';'
                )
    if counts['athlete_daily_hrv'] != 166 or counts['activity'] != 82:
        raise RuntimeError('Personal StarRocks seed does not match validated source counts')
    OUT.write_text('\n\n'.join(statements) + '\n', encoding='utf-8')
    print('Wrote', OUT.name, 'with', sum(counts.values()), 'personal rows across',
          sum(1 for n in counts.values() if n), 'tables')
    print('HRV', counts['athlete_daily_hrv'], 'activities', counts['activity'])


if __name__ == '__main__':
    main()
