"""Build a StarRocks schema and data package from the verified local fitness snapshot.

The source StarRocks account is used only for DDL and type metadata. Rows come from
the local DuckDB snapshot. Connection and raw MCP tables are intentionally excluded.
"""

import argparse
import base64
from datetime import date, datetime
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile

import duckdb
from translate_starrocks_comments import translate_comments

ROOT = Path(__file__).resolve().parent.parent
BLOCKED = {"source_connection", "source_snapshot", "sync_state"}
IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--host", required=True)
parser.add_argument("--port", type=int, default=9030)
parser.add_argument("--database", required=True)
parser.add_argument("--user", required=True)
parser.add_argument("--keychain-service", required=True)
parser.add_argument("--mysql-bin", default="/opt/homebrew/opt/mysql-client/bin/mysql")
parser.add_argument("--snapshot", type=Path, default=ROOT / "coros_import/private_data/starrocks_full.duckdb")
parser.add_argument("--output-dir", type=Path, default=ROOT / "personal_starrocks")
args = parser.parse_args()
if not IDENT.fullmatch(args.database):
    parser.error("Invalid database name")


def literal(value, kind):
    if value is None:
        return "NULL"
    if kind in {"int", "bigint", "smallint", "tinyint", "decimal", "double", "float"}:
        return str(value)
    encoded = base64.b64encode(str(value).encode("utf-8")).decode("ascii")
    text = f"from_base64('{encoded}')"
    return f"parse_json({text})" if kind == "json" else text


def source_ddl(xml_text):
    fields = ET.fromstring(xml_text).findall(".//row/field")
    if not fields:
        raise ValueError("Missing StarRocks DDL")
    return (fields[1].text or "").rstrip(";\n") + ";"


secret = subprocess.run(["security", "find-generic-password", "-s", args.keychain_service, "-w"],
                        capture_output=True, text=True, check=True).stdout.rstrip("\n")
if "\n" in secret or "\r" in secret:
    raise ValueError("Unexpected newline in Keychain secret")
fd, config = tempfile.mkstemp(prefix="fitness-mysql-", dir="/private/tmp")
os.fchmod(fd, 0o600)
try:
    with os.fdopen(fd, "w") as file:
        escaped = secret.replace("\\", "\\\\").replace('"', '\\"')
        file.write(f'[client]\nuser="{args.user}"\npassword="{escaped}"\n'
                   f'host="{args.host}"\nport={args.port}\ndatabase="{args.database}"\n')
    del secret

    def mysql(sql, xml=False):
        cmd = [args.mysql_bin, "--defaults-extra-file=" + config, "--default-character-set=utf8mb4"]
        cmd.extend(["--xml"] if xml else ["--batch", "--skip-column-names"])
        result = subprocess.run(cmd + ["-e", sql], capture_output=True, text=True, timeout=120)
        if result.returncode:
            raise RuntimeError(f"StarRocks metadata query failed: {result.stderr[:250]}")
        return result.stdout

    objects = [line.split("\t")[:2] for line in mysql("SHOW FULL TABLES").splitlines()]
    tables = [name for name, kind in objects if kind == "BASE TABLE" and name not in BLOCKED]
    views = [name for name, kind in objects if kind == "VIEW"]
    types = {}
    for line in mysql("SELECT table_name,column_name,data_type FROM information_schema.columns "
                      f"WHERE table_schema='{args.database}' ORDER BY table_name,ordinal_position").splitlines():
        name, col, kind = line.split("\t")
        types.setdefault(name, []).append((col, kind.lower()))

    schema = ["-- Personal fitness data snapshot; load only into a new, empty local StarRocks database.",
              f"CREATE DATABASE IF NOT EXISTS `{args.database}`;", f"USE `{args.database}`;"]
    for name in tables:
        schema.append(source_ddl(mysql(f"SHOW CREATE TABLE `{name}`", xml=True)))
    view_ddl = {name: source_ddl(mysql(f"SHOW CREATE VIEW `{name}`", xml=True)) for name in views}
    for name, ddl in view_ddl.items():
        if any(re.search(r"\b" + blocked + r"\b", ddl, re.I) for blocked in BLOCKED):
            raise ValueError(f"View {name} depends on excluded connection or raw-snapshot tables")
    remaining = dict(view_ddl)
    while remaining:
        ready = [name for name, ddl in remaining.items() if not any(
            other != name and re.search(r"\b" + other + r"\b", ddl, re.I)
            for other in remaining)]
        if not ready:
            raise ValueError("Cyclic or unresolved view dependencies")
        for name in ready:
            schema.append(remaining.pop(name))

    snapshot = args.snapshot.expanduser().resolve()
    counts = {}
    view_counts = {}
    inserts = ["-- Personal data. Apply once after schema.sql, to a new empty database.",
               f"USE `{args.database}`;"]
    with duckdb.connect(str(snapshot), read_only=True) as conn:
        for name in tables:
            columns = types[name]
            cols = [col for col, _ in columns]
            if any(not IDENT.fullmatch(col) for col in cols):
                raise ValueError(f"Unexpected column name in {name}")
            result = conn.execute(f'SELECT * FROM fitness_demo."{name}"')
            found = [x[0] for x in result.description]
            if found != cols:
                raise ValueError(f"Column order mismatch in {name}")
            records = result.fetchall()
            counts[name] = len(records)
            for start in range(0, len(records), 40):
                batch = records[start:start + 40]
                rows = ["(" + ",".join(literal(value, kind) for value, (_, kind) in zip(record, columns)) + ")"
                        for record in batch]
                inserts.append(f"INSERT INTO `{name}` VALUES\n" + ",\n".join(rows) + ";")
        for name in views:
            view_counts[name] = conn.execute(f'SELECT COUNT(*) FROM fitness_demo."{name}"').fetchone()[0]

    target = args.output_dir.expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    (target / "schema.sql").write_text(translate_comments("\n\n".join(schema) + "\n"), encoding="utf-8")
    (target / "seed.sql").write_text("\n\n".join(inserts) + "\n", encoding="utf-8")
    check = [f"USE `{args.database}`;"] + [f"SELECT '{name}' AS object_name, COUNT(*) AS actual_rows FROM `{name}`; -- expected {count}"
                 for name, count in [*counts.items(), *view_counts.items()]]
    (target / "verify.sql").write_text("\n".join(check) + "\n", encoding="utf-8")
    manifest = {"database": args.database, "scope": "fitness analytics; credentials and raw ingestion excluded",
                "base_table_count": len(tables), "view_count": len(views), "row_counts": counts,
                "view_row_counts": view_counts,
                "source_duckdb_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest()}
    (target / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    readme = f"""# Personal StarRocks snapshot

This package contains the owner's fitness data from `joanna_fitness`, exported via a
local DuckDB snapshot. It includes {len(tables)} analytical base tables and {len(views)} view
definitions. `source_connection`, `source_snapshot`, and `sync_state` are excluded
because they may contain credentials, raw API responses, or synchronization metadata.

The SQL files contain personal fitness measurements, dates, and profile/device
metadata. Base64 in `seed.sql` is only SQL-safe encoding, **not anonymization**.
No API key or database password is included.

Run on a new, empty StarRocks database in this order: `schema.sql`, `seed.sql`,
then `verify.sql`. `seed.sql` is not idempotent; running it twice will duplicate rows.
For a local StarRocks FE at port 9030, from this folder:

```sh
mysql -h 127.0.0.1 -P 9030 -u root -p < schema.sql
mysql -h 127.0.0.1 -P 9030 -u root -p < seed.sql
mysql -h 127.0.0.1 -P 9030 -u root -p < verify.sql
```

The client prompts for the password. Use an account with CREATE and INSERT rights;
do not put its password in a command or this repository.
The DDL came from StarRocks 4.x. A different version or cluster topology may require
adjusting replication settings. The DuckDB mirror of the seven views is a static
snapshot; the StarRocks package recreates them as live views.

See `manifest.json` for expected row counts. This package has been generated and
checked against the DuckDB snapshot, but has not been loaded into a separate local
StarRocks server in this workflow.
"""
    (target / "README.md").write_text(readme, encoding="utf-8")
    archive = target.with_suffix(".zip")
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for filename in ["README.md", "manifest.json", "schema.sql", "seed.sql", "verify.sql"]:
            z.write(target / filename, arcname=f"personal_starrocks/{filename}")
    for path in [*target.iterdir(), archive]:
        os.chmod(path, 0o600)
    print(f"Wrote {len(tables)} tables, {len(views)} views, {sum(counts.values())} base rows: {target}")
    print(f"Archive: {archive}")
finally:
    os.unlink(config)
