# Release notes

## 2026-11-24 — Local coaching and training-plan update

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
- Updated local DuckDB and StarRocks DDL templates. The repository does **not** migrate an existing remote StarRocks database.

### Verification and limits

- DOSI validated the DuckDB model and ontology without issues or compile errors. Queries returned the saved personal threshold target and version 3 weekly planned mileage.
- Rebuilt the fictional DuckDB fixture with a compatible DuckDB version; `warehouse/verify_duckdb.py` passed all fixture and DOSI metric checks.
- Local dashboard rendering, bilingual tab switching, and reading changed DuckDB data on a new page render were checked. The local service returned HTTP 200.
- Refreshing `/dashboard` does not fetch new COROS data. Import watch data into the local database first. The coaching rule catalog is evaluated by the dashboard and Agent workflow; DOSI does not automatically execute or approve coaching actions.
