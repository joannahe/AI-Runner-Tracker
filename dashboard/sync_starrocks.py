"""Snapshot fitness analytics tables and view results from StarRocks into local DuckDB.

The destination belongs under ignored private_data/. Connection credentials come from
macOS Keychain and are never written to the repository or printed.
"""

import argparse
from collections import Counter
import os
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "coros_import" / "private_data" / "starrocks_full.duckdb"
BLOCKED = {"source_connection", "source_snapshot", "sync_state"}
IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
NIL = "{http://www.w3.org/2001/XMLSchema-instance}nil"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--host", required=True)
parser.add_argument("--port", type=int, default=9030)
parser.add_argument("--database", required=True)
parser.add_argument("--user", required=True)
parser.add_argument("--keychain-service", required=True)
parser.add_argument("--mysql-bin", default="/opt/homebrew/opt/mysql-client/bin/mysql")
parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
args = parser.parse_args()
if not IDENT.fullmatch(args.database):
    parser.error("Invalid database name")


def dtype(name, precision, scale):
    name = name.lower()
    if name == "decimal":
        p = min(int(precision if precision not in {None, "", "NULL"} else 18), 38)
        s = min(int(scale if scale not in {None, "", "NULL"} else 0), p)
        return f"DECIMAL({p},{s})"
    return {
        "date": "DATE", "datetime": "TIMESTAMP", "timestamp": "TIMESTAMP",
        "tinyint": "INTEGER", "smallint": "INTEGER", "int": "INTEGER",
        "bigint": "BIGINT", "double": "DOUBLE", "float": "DOUBLE",
    }.get(name, "VARCHAR")


def quote(name):
    if not IDENT.fullmatch(name):
        raise ValueError("Unexpected source identifier")
    return f'"{name}"'


secret = subprocess.run(
    ["security", "find-generic-password", "-s", args.keychain_service, "-w"],
    capture_output=True, text=True, check=True,
).stdout.rstrip("\n")
if "\n" in secret or "\r" in secret:
    raise ValueError("Unexpected newline in Keychain secret")
fd, config = tempfile.mkstemp(prefix="fitness-mysql-", dir="/private/tmp")
os.fchmod(fd, 0o600)
try:
    # A 0600 temporary client file keeps the password out of process arguments.
    with os.fdopen(fd, "w") as file:
        escaped = secret.replace("\\", "\\\\").replace('"', '\\"')
        file.write(f'[client]\nuser="{args.user}"\npassword="{escaped}"\n'
                   f'host="{args.host}"\nport={args.port}\n'
                   f'database="{args.database}"\n')
    del secret

    def mysql(sql, xml=False):
        cmd = [args.mysql_bin, "--defaults-extra-file=" + config, "--default-character-set=utf8mb4"]
        cmd.extend(["--xml"] if xml else ["--batch", "--skip-column-names"])
        result = subprocess.run(cmd + ["-e", sql], capture_output=True, text=True, timeout=120)
        if result.returncode:
            raise RuntimeError(f"StarRocks query failed (exit {result.returncode}): {result.stderr[:300]}")
        return result.stdout

    objects = []
    for line in mysql("SHOW FULL TABLES").splitlines():
        name, kind = line.split("\t")[:2]
        if name not in BLOCKED:
            objects.append((name, kind))
    metadata = {}
    for line in mysql(
        "SELECT table_name,column_name,data_type,numeric_precision,numeric_scale "
        "FROM information_schema.columns WHERE table_schema='" + args.database + "' "
        "ORDER BY table_name,ordinal_position"
    ).splitlines():
        name, column, datatype, precision, scale = line.split("\t")
        metadata.setdefault(name, []).append((column, dtype(datatype, precision, scale)))

    out = args.output.expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    fd, pending_name = tempfile.mkstemp(prefix="fitness-snapshot-", suffix=".duckdb", dir=out.parent)
    os.close(fd)
    pending = Path(pending_name)
    pending.unlink()  # DuckDB creates a new database file; it cannot open an empty placeholder.
    counts = Counter()
    try:
        with duckdb.connect(str(pending)) as conn:
            conn.execute("CREATE SCHEMA fitness_demo")
            for name, kind in objects:
                columns = metadata.get(name, [])
                if not columns:
                    raise ValueError(f"Missing column metadata for {name}")
                conn.execute("CREATE TABLE fitness_demo." + quote(name) + " (" +
                             ", ".join(f"{quote(col)} {typ}" for col, typ in columns) + ")")
                xml = mysql("SELECT * FROM `" + name + "`", xml=True)
                result = ET.fromstring(xml)
                expected = [col for col, _ in columns]
                values = []
                for row in result.findall("row"):
                    fields = {field.attrib["name"]: None if field.attrib.get(NIL) == "true" else (field.text or "")
                              for field in row.findall("field")}
                    values.append(tuple(fields.get(col) for col in expected))
                if values:
                    conn.executemany("INSERT INTO fitness_demo." + quote(name) + " VALUES (" +
                                     ",".join("?" for _ in expected) + ")", values)
                local = conn.execute("SELECT COUNT(*) FROM fitness_demo." + quote(name)).fetchone()[0]
                if local != len(values):
                    raise AssertionError(f"Row count mismatch: {name}")
                counts[name] = local
                print(f"{name}: {local} rows ({'view snapshot' if kind == 'VIEW' else 'table'})")
        os.chmod(pending, 0o600)
        pending.replace(out)
    finally:
        if pending.exists():
            pending.unlink()
    print(f"Snapshot complete: {len(objects)} objects, {sum(counts.values())} rows; local private DuckDB: {out}")
finally:
    os.unlink(config)
