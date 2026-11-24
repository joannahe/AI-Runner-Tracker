# Release notes

## Unreleased — [PR #2: Running plan and coaching dashboard](https://github.com/joannahe/AI-Runner-Tracker/pull/2)

### Running plan

- Activated the athlete-approved version 3 four-week plan. Version 1 remains in history; the unapproved version 2 draft was withdrawn.
- Added dated, bilingual warm-up, main-set, and cool-down segments with estimated distance, target pace, and target heart rate. The dashboard shows each session's running distance and weekly totals.
- Saved an athlete-selected threshold training target of 5:30–5:55/km at 155–165 bpm as a versioned pace-zone record. It is separate from the COROS threshold estimate. The December 2 threshold session uses this target; its estimated total is 8.0 km, making that week's planned total 28.0 km.
- DEKA FIT doubles has a personal running-distance range until the partner split is known.

### Dashboard and alerts

- Restored desktop tab navigation and fixed a rendering error in the Base tab. Verified all six tabs in English and Chinese.
- The local `/dashboard` service now reads DuckDB and the ontology rule catalog on **every page request**. The browser recalculates Attention checks from that response. Standalone HTML and the fictional `/demo` page remain offline exports.
- Improved Attention grouping by date and topic, combined checks from the same recovery signal, and added coach summaries with prominent key numbers and suggested actions.
- Import coverage is recorded as unverified until the source window has been reconciled; an imported batch alone does not prove a complete provider history.

### Semantic layer and warehouse

- Added planned action distance fields, segment records, relationships, and weekly planned-distance metrics to both DuckDB and StarRocks model definitions. Updated the ontology mapping for planned segments and intensity.
- Added `PlannedSegment` as an ontology concept linked to `PlannedAction`, with ordered warm-up, main-set, and cool-down targets. `PlannedAction` now exposes structured intensity, bilingual titles, and planned distance/range fields. Both DOSI 0.2.2 projects carry these additions in separate semantic model, ontology, and mapping files.
- Updated local DuckDB and StarRocks DDL templates. The repository does **not** migrate an existing remote StarRocks database.

### DOSI compatibility

- Built on the standalone DOSI 0.2.2 mappings merged in PR #1. The YAML model version `0.2.0.dev0` is the format declaration, not the installed CLI version.
- Validated the updated DuckDB and StarRocks three-file projects through their `fitness.mapping.yaml` entry points. `ontology_bindings.yaml` remains a human-readable audit, not the DOSI mapping file.

### Verification and limits

- DOSI validated both mapped projects without issues or compile errors; advisory field warnings and intentional conceptual edges remain. Queries returned the saved personal threshold target and version 3 weekly planned mileage.
- Rebuilt the fictional DuckDB fixture with a compatible DuckDB version; `warehouse/verify_duckdb.py` passed all fixture and DOSI metric checks.
- Local dashboard rendering, bilingual tab switching, and reading changed DuckDB data on a new page render were checked. The local service returned HTTP 200.
- Refreshing `/dashboard` does not fetch new COROS data. Import watch data into the local database first. The coaching rule catalog is evaluated by the dashboard and Agent workflow; DOSI does not automatically execute or approve coaching actions.

## 2026-11-24 — [PR #1: DOSI 0.2.2 mapping upgrade](https://github.com/joannahe/AI-Runner-Tracker/pull/1) (merged)

- Split each DuckDB and StarRocks project into separate Apache Ossie semantic model, ontology, and `fitness.mapping.yaml` files; added schema checks and switched validation and query commands to the mapping entry point.
- Added queryable `derived_by` ontology subtypes for high and low COROS load days, high-focus run activities, and high weekly mileage growth. The weekly growth path uses measured standalone and hybrid run segments plus independently verified import coverage.
- Added the warehouse weekly-distance view and coverage table. Refreshed the lineage and ontology views, fixture builder, and English/Chinese setup instructions.
- Confirmed both mapped projects and fixture metrics with DOSI 0.2.2. This merge did not migrate a live StarRocks database. Other coaching guidance in `ai_context.x_coaching_knowledge` remains separate from DOSI's executable subtype filters.

## 2026-11-18–19 — Coaching rule and alert updates already on `main`

- Consolidated configurable coaching review conditions, thresholds, evidence requirements, and suggested actions in the ontology rule catalog. These cover load ratio, weekly running-distance growth, training-intensity distribution, recovery signals, and plan-spacing reviews.
- Connected the local Attention page to that catalog and added human-approved proposed actions. Recovery checks gained combined assessment and dated evidence handling.
- These commits preceded the current PR and are already in `main`; their ontology changes will not appear in this PR's file diff. DOSI does not itself execute the coaching catalog as a rule engine.

## 2026-11-18 — Initial public release

- Published the English-first AI Runner Tracker with optional Chinese UI, a local DuckDB running dashboard, and separate fictional and owner-authorized personal data examples.
- Included guided COROS import through its MCP connection and a Garmin personal developer-credential path, with local storage as the default. StarRocks schema and seed packages were provided as an optional warehouse path.
- Published DuckDB and StarRocks DOSI semantic models and ontologies, lineage and concept views, metric verification scripts, and example questions for exploring running performance, training, recovery, capabilities, and goals.
- Added Agent setup guidance, architecture and onboarding documents, and separate licenses/notices for source code, documentation, personal data, and third-party components. Credentials were excluded from the published project.
