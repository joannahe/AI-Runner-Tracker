# Personal StarRocks snapshot

This package contains the owner's fitness data from `joanna_fitness`, exported via a
local DuckDB snapshot. It includes 22 analytical base tables and 7 view
definitions. `source_connection`, `source_snapshot`, and `sync_state` are excluded
because they may contain credentials, raw API responses, or synchronization metadata.

The SQL files contain personal fitness measurements, dates, and profile/device
metadata. Base64 in `seed.sql` is only SQL-safe encoding, **not anonymization**.
The owner's date of birth is set to `NULL`. No API key or database password is included.

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
