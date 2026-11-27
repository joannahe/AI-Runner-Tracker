"""Save a completed or provisional coaching review without changing an approved plan."""
import argparse
import json
import re
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parent.parent
TABLES = {
    'coach_review': ['athlete_id','review_id','goal_id','goal_version','plan_id','plan_version','review_date','window_start_date','window_end_date','data_watermark_date','rule_version','status','summary','next_step_text','summary_en','summary_zh','next_step_text_en','next_step_text_zh','created_at_utc'],
    'coach_review_finding': ['athlete_id','review_id','finding_id','rule_code','status','observed_value','baseline_value','unit','evidence_date','source_dataset','source_record_id','evidence_status','summary'],
    'coach_review_proposal': ['athlete_id','review_id','proposal_id','plan_id','plan_version','action_id','proposed_change','decision_status','decided_at_utc'],
}
def main():
    parser=argparse.ArgumentParser(description='Persist one dated, evidence-backed coach review')
    parser.add_argument('--db',type=Path,required=True)
    parser.add_argument('--input',type=Path,required=True)
    args=parser.parse_args()
    payload=json.loads(args.input.read_text())
    review=payload['review']; findings=payload['findings']; proposals=payload['proposals']
    assert review['status'] in ('completed', 'provisional') and review['rule_version'] and review['data_watermark_date']
    assert review['window_start_date']<=review['window_end_date']<=review['review_date']
    assert all(len(str(row.get('summary','')))<2048 for row in [review,*findings])
    assert isinstance(review.get('next_step_text'),str) and 0 < len(review['next_step_text'].strip()) < 2048
    assert all(not review.get(name) or (isinstance(review[name],str) and len(review[name])<2048) for name in ('summary_en','summary_zh','next_step_text_en','next_step_text_zh'))
    assert all(p['decision_status']=='pending' and p.get('decided_at_utc') is None for p in proposals)
    assert review['status'] != 'provisional' or (findings and not proposals)
    assert all(f['evidence_status'] for f in findings)
    assert len({f['finding_id'] for f in findings})==len(findings)
    assert len({p['proposal_id'] for p in proposals})==len(proposals)
    db=args.db.resolve()
    if not db.is_file(): raise FileNotFoundError(db)
    conn=duckdb.connect(str(db))
    conn.execute('BEGIN TRANSACTION')
    try:
        schema='fitness_demo'
        # The canonical build emits exactly these table statements for either a fresh fixture or a personal snapshot.
        ddl=(ROOT/'warehouse/duckdb_schema.sql').read_text()
        for table in TABLES:
            match=re.search(r'CREATE TABLE IF NOT EXISTS '+table+r' \(.*?\);',ddl,re.S)
            if not match: raise ValueError(f'missing DDL for {table}')
            conn.execute(f'CREATE SCHEMA IF NOT EXISTS {schema}')
            conn.execute(match.group().replace('CREATE TABLE IF NOT EXISTS '+table,'CREATE TABLE IF NOT EXISTS '+schema+'.'+table,1))
        # Add optional localized prose to earlier snapshots without changing saved reviews.
        columns={name for (name,) in conn.execute("SELECT column_name FROM information_schema.columns WHERE table_schema=? AND table_name='coach_review'",[schema]).fetchall()}
        for name in ('next_step_text','summary_en','summary_zh','next_step_text_en','next_step_text_zh'):
            if name not in columns:
                conn.execute(f'ALTER TABLE {schema}.coach_review ADD COLUMN {name} VARCHAR(2048)')
        key=(review['athlete_id'],review['review_id'])
        if conn.execute(f'SELECT COUNT(*) FROM {schema}.coach_review WHERE athlete_id=? AND review_id=?',key).fetchone()[0]:
            raise ValueError('review_id already saved; create a new review instead of overwriting history')
        goal=(review['athlete_id'],review['goal_id'],review['goal_version'])
        plan=(review['athlete_id'],review['plan_id'],review['plan_version'],review['goal_id'],review['goal_version'])
        if conn.execute(f'SELECT COUNT(*) FROM {schema}.athlete_goal WHERE athlete_id=? AND goal_id=? AND goal_version=?',goal).fetchone()[0]!=1: raise ValueError('goal version not found')
        if conn.execute(f'SELECT COUNT(*) FROM {schema}.action_plan WHERE athlete_id=? AND plan_id=? AND plan_version=? AND goal_id=? AND goal_version=?',plan).fetchone()[0]!=1: raise ValueError('plan version does not match goal version')
        for p in proposals:
            if (p['plan_id'],p['plan_version'])!=(review['plan_id'],review['plan_version']):raise ValueError('proposal plan version differs from reviewed plan')
            if p.get('action_id') and conn.execute(f'SELECT COUNT(*) FROM {schema}.planned_action WHERE athlete_id=? AND plan_id=? AND plan_version=? AND action_id=?',(review['athlete_id'],p['plan_id'],p['plan_version'],p['action_id'])).fetchone()[0]!=1:raise ValueError('proposed action not found in reviewed plan')
        for table,rows in [('coach_review',[review]),('coach_review_finding',findings),('coach_review_proposal',proposals)]:
            cols=TABLES[table]
            for row in rows:
                if table!='coach_review' and (row['athlete_id'],row['review_id'])!=key:raise ValueError('finding/proposal belongs to another review')
                if set(row)-set(cols):raise ValueError('unknown fields in '+table)
                conn.execute(f'INSERT INTO {schema}.{table} ('+','.join(cols)+') VALUES ('+','.join('?' for _ in cols)+')',[row.get(c) for c in cols])
        conn.execute('COMMIT')
    except Exception:
        conn.execute('ROLLBACK')
        raise
    finally:conn.close()
    print(json.dumps({'review_id':review['review_id'],'findings':len(findings),'proposals':len(proposals),'status':'saved'}))
if __name__=='__main__':main()
