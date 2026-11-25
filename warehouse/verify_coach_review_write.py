"""Check append-only review persistence on a disposable synthetic DuckDB copy."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
with tempfile.TemporaryDirectory() as temporary:
    db = Path(temporary) / 'running_demo.duckdb'
    payload_path = Path(temporary) / 'review.json'
    shutil.copy2(ROOT / 'warehouse/running_demo.duckdb', db)
    payload = {
        'review': {
            'athlete_id': 'demo_01', 'review_id': 'review_write_test',
            'goal_id': 'synthetic_run_consistency', 'goal_version': 2,
            'plan_id': 'synthetic_running_plan', 'plan_version': 2,
            'review_date': '2026-04-22', 'window_start_date': '2026-04-13',
            'window_end_date': '2026-04-19', 'data_watermark_date': '2026-04-21',
            'rule_version': 'coach_v1', 'status': 'completed',
            'summary': 'Review the running goal.', 'created_at_utc': '2026-04-22 09:00:00',
        },
        'findings': [{
            'athlete_id': 'demo_01', 'review_id': 'review_write_test',
            'finding_id': 'frequency', 'rule_code': 'GoalProgressReview',
            'status': 'below_target', 'observed_value': 2, 'baseline_value': 3,
            'unit': 'days/week', 'evidence_date': '2026-04-19',
            'source_dataset': 'goal_progress_assessment',
            'source_record_id': 'synthetic_run_consistency_v2_weekly_run_days_2026-04-21',
            'evidence_status': 'sufficient', 'summary': 'Two days against three planned.',
        }],
        'proposals': [{
            'athlete_id': 'demo_01', 'review_id': 'review_write_test',
            'proposal_id': 'easy_run', 'plan_id': 'synthetic_running_plan',
            'plan_version': 2, 'action_id': 'run_20260419',
            'proposed_change': 'Review the easy run duration.',
            'decision_status': 'pending', 'decided_at_utc': None,
        }],
    }
    payload_path.write_text(json.dumps(payload))
    command = [sys.executable, str(ROOT / 'dashboard/save_coach_review.py'),
               '--db', str(db), '--input', str(payload_path)]
    subprocess.run(command, check=True, capture_output=True, text=True)
    repeated = subprocess.run(command, capture_output=True, text=True)
    assert repeated.returncode != 0 and 'already saved' in repeated.stderr
    with duckdb.connect(str(db), read_only=True) as conn:
        assert conn.execute("SELECT COUNT(*) FROM fitness_demo.coach_review WHERE review_id='review_write_test'").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM fitness_demo.coach_review_finding WHERE review_id='review_write_test'").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM fitness_demo.coach_review_proposal WHERE review_id='review_write_test' AND decision_status='pending'").fetchone()[0] == 1
        assert conn.execute("SELECT approval_status FROM fitness_demo.action_plan WHERE plan_id='synthetic_running_plan' AND plan_version=2").fetchone()[0] == 'pending'
print('Coach review write, duplicate rejection, and plan immutability passed.')
