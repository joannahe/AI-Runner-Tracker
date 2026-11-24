# Agent guide

AI Runner Tracker supports two valid paths: exploring local running data and dashboard insights, and studying DOSI's **semantic layer and ontology** through the same running-coach use case. Do not force ontology setup on someone who only wants the tracker. Training observations apply the definitions; they are not a claim that DOSI executes coaching rules or provides medical advice.

Local DuckDB is the default storage and dashboard source. StarRocks is an optional warehouse query route with matching SQL and model files; current watch imports do not write to StarRocks, and the dashboard needs a DuckDB snapshot of StarRocks data. Keep the [architecture diagram](assets/architecture.svg) and [architecture notes](ARCHITECTURE.md) accurate when data paths change.

## First orientation

1. Read `README.md` for local setup and the two data paths.
2. Read `ARCHITECTURE.md` for the actual data flow and `agent.md` when assisting an end user.
3. Read `LICENSE`, `DATA_LICENSE.md`, `DOCUMENTATION_LICENSE.md`, and `THIRD_PARTY_NOTICES.md` before reusing or exporting repository material.
4. Read `fitness_analysis.yaml` (DuckDB) and `fitness_ontology.yaml` together. Their `.starrocks.yaml` counterparts use the same concepts for StarRocks.
5. Read `ontology_bindings.yaml` to distinguish mapped concepts from conceptual or workflow-only links.
6. Read `fitness_ontology.yaml`, `RECOVERY_RULES.md`, and `TRAINING_COACH_AGENT.md` before explaining any alert or proposing a plan change.

## Data and privacy boundaries

- `warehouse/build.py`, `warehouse/duckdb_seed.sql`, `warehouse/starrocks_seed.sql`, and `dashboard/index.html` are the fictional first-run path.
- `personal_duckdb/`, `personal_starrocks/`, `personal_starrocks.zip`, `warehouse/starrocks_personal_seed.sql`, and `dashboard/personal-preview.html` contain the owner's real, identifiable fitness data, shared for this project. They are not anonymized. A generated HTML file can expose embedded health data.
- `coros_import/private_data/`, credentials, tokens, raw provider responses, and another athlete's records must remain private and untracked. Never copy a private import into public fixtures or generated HTML intended for publication without that athlete's explicit consent.
- Do not add API keys, passwords, live StarRocks connection strings, or local keychain material to source files, examples, logs, or screenshots.

## Model and rule semantics

- Preserve the distinction between an actual workout, its source-platform records, and a proposed plan action. Deduplicate source activities before totals.
- Keep measured running distance separate from HYROX rule-reference distance; keep official race time separate from watch time. Missing values are not zero.
- COROS `activity.training_focus` is a completed session's primary focus label. It is not measured time in a heart-rate zone and cannot classify the intensity of a future planned action.
- Metrics live in the semantic model. Concepts, relationships, and their bindings live in the ontology. Configurable review conditions and evidence gates live in `fitness_ontology.yaml`. The markdown guides explain those choices.
- DOSI validates and queries the semantic model and maps ontology concepts. The rule catalog does not run automatically in DOSI. Do not describe an Agent workflow, reminder, draft generator, or plan approval as implemented unless there is a tested evaluator and persistence path.
- A review signal is not a diagnosis. Present values, personal baseline or provider range, observation date, source, effective rule version, and missing evidence. Never infer rest from an empty calendar date or a verified race distance from watch GPS distance.
- The athlete approves any proposed plan change. Preserve the approved plan and do not write a draft to COROS or Garmin automatically.

## Working in this repository

- Keep English as the default UI and documentation language; preserve the English/Chinese UI toggle. Model names, SQL fields, and concept identifiers remain in English.
- `warehouse/build.py` regenerates schema, seeds, and dialect model files. Check edits to generated files before running it.
- `dashboard/action_server.py` serves the current personal DuckDB and ontology rules on each page refresh. `dashboard/build.py` generates standalone HTML snapshots; rebuild those exports after changing data or the template. `dashboard/rebuild_from_snapshot.mjs` is a fallback for the bundled personal preview when the local DuckDB reader cannot open that snapshot.
- Run `dosi --model fitness_analysis.yaml --ontology fitness_ontology.yaml validate` and `.venv/bin/python warehouse/verify_duckdb.py` after changing the model or fixture. For StarRocks changes, also validate the StarRocks pair and review the acceptance SQL.
- When adding a rule, add its concept path, inputs, evidence gate, missing-data behavior, suggested human-reviewed action, and an acceptance question in `QUESTION_CATALOG_AND_ONBOARDING.md`. Keep the rule's implemented status accurate.
