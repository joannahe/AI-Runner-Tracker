// Exercise the rendered Attention tab without a browser or personal data.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('./index.html',import.meta.url),'utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
assert.ok(script,'generated dashboard script missing');
const setup=script.slice(0,script.indexOf('function render(){'));
assert.ok(setup.length>1000,'dashboard initialization marker missing');
function attention(athlete,end,lang='en',review){
  return vm.runInNewContext(setup+`\n${review?`DATA.coach_reviews.push(${JSON.stringify(review)});`:''}state.athlete=${JSON.stringify(athlete)};state.lang=${JSON.stringify(lang)};state.dates[5]={start:'2026-01-01',end:${JSON.stringify(end)}};alerts();`,{Date,console});
}
const saved=attention('demo_01','2026-04-22');
assert.match(saved,/AI COACH · SAVED WEEKLY REVIEW/);
assert.match(saved,/Review the updated three-day running goal/);
assert.match(saved,/2026-04-13 – 2026-04-19/);
assert.match(saved,/Two recorded run days against a three-day weekly target/);
const pending=attention('demo_01','2026-11-25');
assert.match(pending,/Last week’s review is not ready yet/);
assert.match(pending,/2026-11-16 – 2026-11-22/);
assert.doesNotMatch(pending,/Review the updated three-day running goal/);
assert.match(attention('demo_02','2026-04-22','zh'),/最近一周的复盘尚未生成/);
const provisional=attention('demo_01','2026-11-25','zh',{athlete_id:'demo_01',review_id:'provisional',status:'provisional',window_start_date:'2026-11-16',window_end_date:'2026-11-22',review_date:'2026-11-25',created_at_utc:'2026-11-25 05:24:49',data_watermark_date:'2026-11-23',summary:'仅依据现有记录的初步判断。'});
assert.match(provisional,/AI 教练 · 初步周复盘/);
assert.match(provisional,/导入完整性尚未核验/);
assert.match(provisional,/仅依据现有记录的初步判断/);
console.log('Saved, provisional, missing week, and athlete isolation passed.');
