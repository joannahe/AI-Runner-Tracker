# Personal DuckDB snapshot

`joanna_fitness.duckdb` is the owner's real fitness history, exported from the StarRocks `joanna_fitness` database. It uses the DuckDB `fitness_demo` schema so the local dashboard can read it without a server. The 22 base tables contain 2,026 rows. Seven materialized analytical view results add 1,730 rows; unlike the StarRocks rebuild package, these are static snapshots.

Build the personal dashboard from this file:

```sh
.venv/bin/python dashboard/build.py --personal
```

Open `dashboard/personal-preview.html` in a browser. Install `warehouse/requirements.txt` first for a compatible DuckDB 1.5.6 reader. The file includes workout dates, measurements and profile/device information, but the date of birth has been removed. No passwords, API keys, source connection records, raw source snapshots or synchronization state are bundled. The data is **not anonymized**.

For a separate local StarRocks installation, use `personal_starrocks/schema.sql` followed by `personal_starrocks/seed.sql`, then run `personal_starrocks/verify.sql`.
