# AI Runner Tracker: assistant guide for users

Use this file when helping someone **use** the project. For repository edits, also follow [AGENTS.md](AGENTS.md). First read [README.md](README.md) and [ARCHITECTURE.md](ARCHITECTURE.md). Local DuckDB is the default storage; StarRocks is an optional warehouse route. Ask what the user wants to do; do not assume that they need StarRocks, DOSI, or coaching advice.

## Choose the user's path

1. **Explore running data:** open the bundled personal dashboard and its Alerts tab first, or build the separate fictional dashboard. Neither first look needs a watch account or DOSI installation.
2. **Import your own data:** use the local COROS or Garmin importer, review what it will read, and confirm the write. The resulting database stays on the user's computer.
3. **Explore DOSI:** inspect the semantic model, generated SQL, ontology mappings, and an executed metric query. Install the DOSI CLI separately.

Ask only for details required by the chosen path. Never request a watch password, API key, token, or private database in chat. For a training review, ask for the goal, time horizon, available training days, and whether the user wants a descriptive review or a draft plan. The athlete approves any proposed plan change.

## Path A: local dashboard

Open `dashboard/personal-preview.html` and select **Alerts / 关注点** to inspect the bundled, owner-authorized running snapshot. This is the shortest first-run path and needs no installation. For a fresh local rebuild, create `.venv`, install `warehouse/requirements.txt` (DuckDB 1.5.6-compatible), then run `.venv/bin/python dashboard/build.py --personal`. If the user wants a localhost address, run `python3 -m http.server 8000` from the project root and open `http://127.0.0.1:8000/dashboard/personal-preview.html`. The bundled personal data omits the date of birth. For a separate fictional database and dashboard, run:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r warehouse/requirements.txt
.venv/bin/python warehouse/build.py
.venv/bin/python dashboard/build.py
```

Open `dashboard/index.html`, select one of the three fictional athletes at the top, and explore the tabs and **Alerts / 关注点**. This HTML is an offline snapshot; rebuild it after changing data. `warehouse/build.py` also regenerates SQL and model files, so inspect local edits before using it in a customized checkout. Report a failed command and its next check rather than saying setup succeeded without verification.

## Path B: import personal watch data

After creating `.venv`, install the importer dependencies and run the local app:

```sh
.venv/bin/python -m pip install -r coros_import/requirements.txt
.venv/bin/python coros_import/run_local.py
```

Open `http://127.0.0.1:8767/` **on the same computer**. Choose a brand, alias, dates, and available read categories; preview and confirm before saving. COROS uses account authorization through MCP. The checkboxes restrict the read tools this app calls; COROS controls account-level consent. Garmin supports the key holder's own Personal API Key or Activities CSV. Garmin sleep, VO₂ max, training load, FIT files, and multi-user account linking are not implemented. See [the importer guide](coros_import/README.md) for limits and errors. Do not suggest exposing the loopback server to the internet.

Confirmed data is written to the Git-ignored `coros_import/private_data/coros_import.duckdb`. To view it alongside the fictional athletes:

```sh
.venv/bin/python dashboard/build.py --additional-db coros_import/private_data/coros_import.duckdb
```

Reopen `dashboard/index.html` and select the imported athlete. This generated HTML now embeds private observations: do not publish or share it without that athlete's separate consent. Reuse the participant ID and alias on later imports; inspect possible cross-platform duplicates before interpreting totals.

## Path C: inspect the semantic layer and ontology

After the fictional warehouse exists and DOSI is separately installed:

```sh
dosi --version
dosi --model fitness_analysis.yaml --ontology fitness_ontology.yaml validate
dosi --model fitness_analysis.yaml query --metrics measured_run_distance_km --dialect duckdb
dosi --model fitness_analysis.yaml query --metrics measured_run_distance_km --execute --db warehouse/running_demo.duckdb
.venv/bin/python warehouse/verify_duckdb.py
```

Show both the generated SQL and executed result. Explain that metrics are defined in `fitness_analysis.yaml`, concepts and mappings are in `fitness_ontology.yaml`, and DuckDB executes the SQL. Open `lineage.html` or `dosi-ontology-view.html` to inspect the graph; use `ontology_bindings.yaml` to distinguish executable mappings from conceptual links. The `.starrocks.yaml` files and `warehouse/starrocks_*.sql` provide a separate StarRocks path.

The dashboard builder runs its **own direct SQL** against DuckDB; it does not call DOSI. StarRocks can replace the warehouse for DOSI queries using the matching model, but the current watch importer still writes to DuckDB and the dashboard needs a DuckDB snapshot of StarRocks data. The ontology maps concepts, but DOSI does not automatically execute `coaching_knowledge.yaml` as coaching rules. Distinguish a model-backed query, dashboard calculation, and Agent interpretation. Do not describe a proposed review workflow or reminder as an already running background coach.

## If asked for training advice or alerts

Read [coaching_knowledge.yaml](coaching_knowledge.yaml), [RECOVERY_RULES.md](RECOVERY_RULES.md), [QUESTION_CATALOG_AND_ONBOARDING.md](QUESTION_CATALOG_AND_ONBOARDING.md), and [TRAINING_COACH_AGENT.md](TRAINING_COACH_AGENT.md). For each observation, show athlete, date range, source, metric value, personal baseline or provider range, threshold and rule version, missing inputs, and the suggested human-reviewed action. Separate facts from interpretations. Missing data is unknown, not zero; an empty calendar date does not prove rest. COROS `training_focus` is a completed session's label, not measured time in a heart-rate zone. Keep official race time distinct from watch time and measured distance distinct from rule-reference distance. Do not diagnose illness or silently alter an approved plan.

The owner-authorized snapshot in `personal_duckdb/`, `personal_starrocks/`, and `dashboard/personal-preview.html` is identifiable and separately [licensed](DATA_LICENSE.md). Synthetic data is the default onboarding path. Never expose another person's private import, an HTML export containing it, credentials, or local keychain contents.

## Completion check

Confirm that the dashboard file exists and opens, an import was previewed and confirmed, or a DOSI query validates and returns checkable SQL and results. State unavailable data and untested provider connections plainly. Use English-first UI guidance and offer Chinese if the user prefers it.
