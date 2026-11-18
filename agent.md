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

The dashboard builder runs its **own direct SQL** against DuckDB; it does not call DOSI. StarRocks can replace the warehouse for DOSI queries using the matching model, but the current watch importer still writes to DuckDB and the dashboard needs a DuckDB snapshot of StarRocks data. The ontology maps concepts, but DOSI does not automatically execute `fitness_ontology.yaml` as coaching rules. Distinguish a model-backed query, dashboard calculation, and Agent interpretation. Do not describe a proposed review workflow or reminder as an already running background coach.

### Help the user test the ontology

Offer a few plain-language questions from [the README](README.md#questions-to-try-with-an-agent) or [the full bilingual catalog](QUESTION_CATALOG_AND_ONBOARDING.md#reusable-question-catalog). The user need not know a metric name. For each question:

1. Resolve the authorized athlete, local date range and, when relevant, the saved goal and plan version. State any default interpretation of “recently” or “this week.”
2. Trace the question through `fitness_ontology.yaml` and `ontology_bindings.yaml`. Name the concepts used and distinguish a real DOSI mapping from a conceptual arrow or workflow description.
3. Read the linked metric definition in `fitness_analysis.yaml`; query the matching source records or use the DOSI query when supported. Show the generated SQL and executed result if claiming a DOSI-backed answer. The dashboard is not a DOSI query.
4. Apply the applicable review condition from `fitness_ontology.yaml` as an **Agent interpretation**, citing dates, values, baselines, threshold, source, rule version and missing evidence. Do not invent a stored assessment or run an unavailable evaluator.
5. Return an answer with the evidence and a human-reviewed next step. If a goal, verified race distance, structured plan intensity or sufficient history is absent, say exactly what cannot be checked.

Good prompts to offer include “Am I recovering okay lately?”, “Is my mileage increasing too fast?”, “Am I doing too many hard runs?”, “Which day should I take it easy?”, “Am I closer to my goal?”, and “Can I train hard after my race?”. Map them respectively to `RecoveryState` and evidence, `RunningObservation` and `WeeklyMileageIncreaseReview`, `TrainingSession` and `PolarizedHighIntensityReview`, `RecoveryState → Recommendation → PlannedAction`, `Goal → GoalCriterion → GoalProgressAssessment`, and `RaceEvent → PostRaceRecoveryReview`. For a plan-spacing question, inspect `ActionPlan → PlannedAction → HardEasySequenceReview`. Do not promise a personal goal or planned-action answer from the bundled personal snapshot: those records are not included. Use the fictional fixture to demonstrate versioned goals and plans, and label it fictional.

## If asked for training advice or alerts

Read [fitness_ontology.yaml](fitness_ontology.yaml), [RECOVERY_RULES.md](RECOVERY_RULES.md), [QUESTION_CATALOG_AND_ONBOARDING.md](QUESTION_CATALOG_AND_ONBOARDING.md), and [TRAINING_COACH_AGENT.md](TRAINING_COACH_AGENT.md). For each observation, show athlete, date range, source, metric value, personal baseline or provider range, threshold and rule version, missing inputs, and the suggested human-reviewed action. Separate facts from interpretations. Missing data is unknown, not zero; an empty calendar date does not prove rest. COROS `training_focus` is a completed session's label, not measured time in a heart-rate zone. Keep official race time distinct from watch time and measured distance distinct from rule-reference distance. Do not diagnose illness or silently alter an approved plan.

The owner-authorized snapshot in `personal_duckdb/`, `personal_starrocks/`, and `dashboard/personal-preview.html` is identifiable and separately [licensed](DATA_LICENSE.md). Synthetic data is the default onboarding path. Never expose another person's private import, an HTML export containing it, credentials, or local keychain contents.

## Process an athlete-approved alert action

The optional `dashboard/action_server.py` serves the dashboard on `127.0.0.1:8768`. A user-confirmed button creates an approved request under Git-ignored `dashboard/private_data/`; **the button does not itself run this Agent or modify a plan**. When the user asks you to process the requests:

1. Run `.venv/bin/python dashboard/agent_actions.py list` and select the pending request for the authorized athlete. Read its rule, action and `proposed_change` in `fitness_ontology.yaml` under `x_coaching_knowledge`, including `rule_bindings`, evidence gates and `recommendation_options`. The proposed change is a user-approved drafting request, not verified source data.
2. Requery the dated source observations; confirm the alert still applies. Resolve the athlete's current goal, plan version, target workout and available training days. Never infer a rest day from an empty calendar date. If any required evidence or target is missing, run `.venv/bin/python dashboard/agent_actions.py blocked REQUEST_ID --summary 'specific missing input'` and explain the gap to the user.
3. When the evidence and target are sufficient, create a **new local draft** JSON file inside `dashboard/private_data/`. Do not overwrite an approved plan. The file must include `request_id`, `athlete_id`, `source_rule`, `approved_action`, `status: "draft"`, `plan_id`, an integer `version`, nonempty dated `actions` (`date` and `kind` per item), and a nonempty `evidence` list. Preserve the previous plan version if one exists. A draft is a real local artifact, not a change sent to COROS or Garmin.
4. Only after writing and checking that file, run `.venv/bin/python dashboard/agent_actions.py complete REQUEST_ID --plan-file dashboard/private_data/PLAN.json --summary 'what changed'`. The local dashboard will then show the result. If execution fails, record `blocked`; do not mark a queued request complete merely because the button was clicked.

The user-confirmed action permits a draft; approval of any final schedule or external write remains a separate user decision. The bundled personal snapshot has no saved personal plan, so ask for its target workout or build a clearly labeled initial draft before claiming to have revised an existing plan.

## Completion check

Confirm that the dashboard file exists and opens, an import was previewed and confirmed, or a DOSI query validates and returns checkable SQL and results. State unavailable data and untested provider connections plainly. Use English-first UI guidance and offer Chinese if the user prefers it.
