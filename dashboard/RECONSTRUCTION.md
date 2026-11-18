# Dashboard reconstruction from the Datus export

Source reviewed: `running_capability.zip` supplied by the project owner, plus the separately pasted `app.jsx` entry file. The archive has 67 entries: `manifest.json`, an append-only `analysis/intent.md`, model exports, metric snapshots, and 18 saved metric query files. It has **no `render/` directory or JSX component source**. The manifest's `updated_at` is 2026-11-11, while the intent log continues through 2026-11-16; the archive is not a complete export of the current visual implementation.

The entry file establishes the shell: five tabs, separate week/month granularity for Daily and Performance, a shared date range defaulting to the last 12 weeks, English default, language switch, and a light Studio-style layout. The intent log specifies the five sections, metric meaning, charts, weekly KPI comparisons, box plots, and data caveats. The local HTML uses those as a reconstruction guide and reads the bundled DuckDB copy of the owner's StarRocks data.

## Implemented locally

- Light five-tab shell, language switch, common date range, short-range presets, and week/month switching where applicable.
- Generic page copy and an always-visible athlete selector above the title. Each chart, KPI, detail table, and latest-data date follows the selected athlete. The build can combine the bundled sample and one or more separate watch-import databases.
- Daily weekly/monthly KPI comparison, volume, frequency, load trends, and training detail.
- Performance pace, heart-rate, cadence trends and official 10K result.
- Running-form cadence, power, and estimated stride-length box plots by run, with canonical laps and outliers.
- Immediate hover, tap, and keyboard-focus details on trend charts and box plots. Tooltips show dates and series values; box plots also show lap count, quartiles, whiskers, and outlier count.
- Recovery load, load ratio, sleep, resting heart-rate, and latest provider recovery estimate.
- Long-term VO₂max, threshold, and heart-rate zone snapshots; uses the data fetch time only for date filtering and does not present it as the device calculation time.

## Differences from the Studio dashboard

The archive does not contain the original React components, chart configurations, CSS color constants, or `BlockHandle` integration. The local page uses standalone HTML/SVG, so visual details and some interactions are approximations. The intent log describes a pace-versus-heart-rate scatter, moving-average overlays, tone-coded insight points, detailed pace-zone distribution, and several chart controls that are not yet in this reconstruction. The personal database has no athlete pace-zone rows. The saved query files also predate some later revisions in the intent log.

For an exact replica, export the dashboard's `render/` directory, including the five tab components, `filters`, `shared`, `i18n`, and any chart assets. The model/query archive alone cannot recover the final JSX.
