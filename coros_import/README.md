# Local COROS and Garmin importer

This local-only consent UI listens on `127.0.0.1:8767`. COROS holders authorize with COROS MCP on this computer. Garmin holders can use their own Personal API Key for a direct one-time import, or upload a Garmin Connect Activities CSV. Both paths preview first and write only after confirmation. This is not a remotely hosted collection site.

The importer writes to a local DuckDB file by default. It does not write directly to StarRocks; that server is an optional, separately configured warehouse path for DOSI queries.

## Start

From the project root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r coros_import/requirements.txt
.venv/bin/python coros_import/run_local.py
```

Open [http://127.0.0.1:8767/](http://127.0.0.1:8767/) on the same computer. The first page is **Import your activity data → Choose your watch**. Selecting a brand opens its configuration page; browser Back and **Change watch brand** return to the chooser. The COROS page offers account authorization and selected read categories. The Garmin page guides users through creating a Personal API Key, entering it locally, selecting dates, previewing activities, and confirming the import. **Use CSV export** remains available. Required inputs show an asterisk. The brand chooser is driven by the `providers` list in `static/index.html`, so a future watch can add a card and its own import page without changing the existing flows. A new brand also needs a server-side parser and mapping into `fitness_demo`.

Opening `static/index.html` directly as a `file://` URL supports **page preview only**: brand selection, brand-specific configuration, and language switching work without the server. Account connection and CSV import require the local app URL above.

For COROS, the fixed loopback callback is `http://127.0.0.1:8767/oauth/callback`. If COROS refuses that callback, the authorization service may need to allow this local redirect URI; the app will show an error rather than asking for a password.

The interface starts in English. Use **English / 中文** in the header to change the language; the choice is remembered in that browser. The semantic model and ontology keep their identifiers in English. The lineage preview also offers a bilingual interface.

The app uses the [official COROS MCP endpoint and OAuth instructions](https://support.coros.com/hc/en-us/articles/53181619102996-Build-on-COROS-MCP). The account's region can be selected if the global gateway fails. COROS controls the account-level consent screen; the checkboxes here restrict which MCP read tools this app calls. The app never asks for a COROS password, does not call write tools, and discards OAuth tokens after reading. It has no background sync.

## Storage and privacy

`private_data/` is excluded from Git. It contains an unrelated local DuckDB database, separate from the public synthetic `warehouse/running_demo.duckdb`. The optional HRV import retains only the official daily assessment and drops raw HRV sample points before preview and save. The importer stores a pseudonymous participant ID, the holder's chosen alias, consent scope, dates, and one JSON response per selected category. It also normalizes consented data into the private database’s `fitness_demo` tables, using the same schema and dataset names as the public DOSI model. The public warehouse remains synthetic. The public semantic model and synthetic fixtures remain unchanged by imports.

Structured responses have common identity and GPS fields removed. COROS can return prose instead of structured JSON; prose is preserved and may mention an activity location or other details. The consent screen says this. The local holder should review the scope before importing or sharing the private database.

Because this app is bound to loopback and keeps authorization sessions in memory, friends cannot use it from another phone or computer over the Internet. A remotely shared version needs a hosted HTTPS endpoint, user/session management, and secure per-user storage; do not expose this loopback server through a tunnel as a shortcut.

## Offline test

Run with `COROS_IMPORT_MOCK=1` to see the UI without connecting to COROS. Mock mode uses a synthetic preview and writes only synthetic data when confirmed. The local connect-preview-save path has been tested. The live COROS authorization and tool payloads have not been tested with another person's account.

## Garmin Personal API Key (default)

This path is for the key holder's **own Garmin account**. Create a key in [Garmin Connect's Personal API Key settings](https://connect.garmin.com/app/settings/personalApiToken), copy it when displayed, and paste it into the password field at `http://127.0.0.1:8767/`. Select a 1–31 day range and preview. Repeat for older periods. The key is posted to the loopback-only local app, exchanged for a short-lived bearer token, and neither credential is stored in the session, database, logs, source code, or URL. The browser field is cleared when the request starts. The activity response is reduced to the fields used by `fitness_demo` before the preview is held in memory. Imported records are written only when you click **Confirm import**. Avoid opening the page through an untrusted remote host or screen sharing while entering a key. The connection requires internet access to Garmin.

The direct connector reads activity summaries (date, sport, duration, distance, and optional heart rate, cadence, power, calories). It does not read FIT files, routes, sleep, VO₂ max, or Garmin training load. The Garmin API response mapping has been tested with representative payloads; live use still requires a valid Personal API Key.

## Garmin Connect CSV fallback

In Garmin Connect, export the Activities CSV, then choose it in the Garmin section. Choose kilometres or miles based on the export. This importer reads activity summaries: date, sport, duration, distance, and optional average heart rate, cadence, power, and calories. It does not currently read FIT files, Garmin sleep, VO₂ max, or Garmin training load; those fields remain NULL. A personal Garmin API key is not a multi-user authorization mechanism. Direct multi-user account linking needs Garmin Developer Program access.

Use the **same participant ID and alias** on later imports to combine COROS and Garmin data for one person. Each imported activity has a stable source ID. Reimporting the same CSV skips existing activities. A close cross-platform match is marked `possible_duplicate` and excluded from running totals until reviewed; the raw activity stays available.

## Optional: apply for direct Garmin access

This open-source project does **not** ship Garmin OAuth credentials or a multi-user Garmin API connector. If you want to run your own multi-user Garmin integration, [request Starter access for your own app](https://www.garmin.com/en-US/forms/StarterGarminConnectDeveloperAccess/). Once Garmin approves the request, its Developer Portal provides the detailed setup documentation. Garmin describes Starter Business access as limited-user, push-only, and without historical data; ask Garmin which access level fits your use case. The public application form requires JavaScript, so this project does not claim an exact list of form fields.

To build the direct connector after approval, the app will need its OAuth 2.0 configuration from the portal, permission for the Activity API, and a secure receiving endpoint for Garmin's data delivery. Add Health API access only if the product also imports daily health data. The exact credential names, callback settings, and payload contract must be confirmed in the approved Developer Portal before implementation. Keep client credentials and user tokens on a trusted server, never in the browser or public fork. The local demo neither collects these credentials nor exchanges them for Garmin data.

A [Personal API key](https://developer.garmin.com/gc-developer-program/personal/personal-faq/) is for the holder’s own data. It is not a way to authorize friends or other users to your app. Once you have an approved multi-user app, its API payloads can be mapped into the same `fitness_demo` activity and daily-health tables, but that connector still needs to be implemented and tested.

## Semantic table mapping

| Input | `fitness_demo` destination | What is available |
|---|---|---|
| COROS / Garmin activity | `workout_event`, `activity`, `running_observation_fact` | Running distance, duration, pace, optional average HR/cadence/power |
| COROS daily load | `athlete_daily_training_load` | Short/long load and ratio |
| COROS sleep | `athlete_daily_sleep` | Duration and available sleep score/stages |
| COROS resting HR | `athlete_daily_resting_hr` | Daily resting HR |
| COROS overnight HRV | `athlete_daily_hrv` | Official daily average, personal normal range, baseline and evaluation by wake date |
| COROS fitness | `fitness_measurement` / latest view | VO₂ max, threshold measures if returned |

The source activity summary does not supply per-sample heart-rate coverage or HR-zone time. A duration-weighted average HR from summary averages is an estimate, and the coverage field stays NULL. An imported activity is not labeled an official race automatically. No missing value is replaced by zero.

For data already saved before the normalization update, stop the server and run `.venv/bin/python coros_import/backfill.py`. The script creates `coros_import/private_data/coros_import.before-semantic-import.duckdb` before updating. The private database and backup must never be committed to Git.

Query the private DB with DOSI using `fitness_analysis.yaml` and a DuckDB connection to `coros_import/private_data/coros_import.duckdb`; `warehouse/running_demo.duckdb` contains only fictional examples.
