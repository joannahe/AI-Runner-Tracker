// Rebuild the personal preview when the installed DuckDB reader is older than the bundled snapshot.
// Uses the previously exported dashboard payload and the same project's StarRocks seed for HRV.
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const previous = readFileSync(join(here, 'personal-preview.html'), 'utf8');
const template = readFileSync(join(here, 'index.template.html'), 'utf8');
const match = previous.match(/<script>const DATA=([\s\S]*?);\s*const RULES=/);
if (!match) throw new Error('Existing personal dashboard payload not found');
const data = JSON.parse(match[1]);
const previousRules = previous.match(/;const RULES=([\s\S]*?);\s*const TEXT=/);
if (!previousRules) throw new Error('Existing ontology rule snapshot not found; rebuild with dashboard/build.py');
const sql = readFileSync(join(here, '../warehouse/starrocks_personal_seed.sql'), 'utf8');
const block = sql.match(/INSERT INTO `athlete_daily_hrv`[^;]*;/g) || [];
const decode = value => Buffer.from(value, 'base64').toString('utf8');
const toNumber = value => value === 'NULL' ? null : Number(value);
const rows = [];
const pattern = /^\(from_base64\('([^']+)'\), from_base64\('([^']+)'\), '(\d{4}-\d{2}-\d{2})', (\d+(?:\.\d+)?|NULL), (\d+(?:\.\d+)?|NULL), (\d+(?:\.\d+)?|NULL), (\d+(?:\.\d+)?|NULL), from_base64\('([^']+)'\), from_base64\('([^']+)'\)/;
for (const statement of block) {
  for (const line of statement.split('\n')) {
    const m = line.trim().match(pattern);
    if (!m) continue;
    rows.push({
      athlete_id: decode(m[1]), date: m[3], avg_ms: toNumber(m[4]),
      normal_low: toNumber(m[5]), normal_high: toNumber(m[6]),
      evaluation: decode(m[8]), status: decode(m[9])
    });
  }
}
if (rows.length < 100) throw new Error(`Only ${rows.length} HRV rows parsed; stopping to avoid an incomplete page`);
data.hrv = rows;
data.activity_focus = [];
for (const statement of sql.match(/INSERT INTO `activity`[^;]*;/g) || []) {
  for (const line of statement.split('\n')) {
    const date = line.match(/'((?:20\d{2})-\d{2}-\d{2})'/)?.[1];
    const fields = [...line.matchAll(/from_base64\('([^']+)'\)/g)].map(x => decode(x[1]));
    if (!date || fields.length < 8) continue;
    if (fields[2] !== 'running' || !['canonical', 'unique'].includes(fields[7])) continue;
    data.activity_focus.push({athlete_id: fields[0], id: fields[3], date, focus: fields[6]});
  }
}
data.meta.goal = {
  athlete_id: data.athletes[0]?.athlete_id,
  type: 'half_marathon',
  target_date: '2027-03-21',
  target_time_s: 7800,
  distance_km: 21.0975,
  status: 'demo_goal'
};
const encoded = JSON.stringify(data).replaceAll('<', '\\u003c');
writeFileSync(join(here, 'personal-preview.html'), template.replace('/* __DATA__ */', encoded).replace('/* __RULES__ */', previousRules[1]));
console.log(`Rebuilt personal-preview.html with ${rows.length} daily HRV assessments`);
