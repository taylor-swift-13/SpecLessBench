"""Check the stored cost snapshot against its recorded source prefixes and paper."""
import hashlib,json
from accounting import ROOT
ledger=json.loads((ROOT/'benchmarks/construction/total-cost.json').read_text(encoding='utf-8'))
for row in ledger['batch_records']:
    assert hashlib.sha256((ROOT/row['record']).read_bytes()).hexdigest()==row['sha256'],row['record']
time=ledger['time_observation'];log=(ROOT/'benchmarks/construction/commands.jsonl').read_bytes()
prefix=log[:time['command_log_prefix_bytes']]
assert len(prefix)==time['command_log_prefix_bytes']
assert hashlib.sha256(prefix).hexdigest()==time['command_log_prefix_sha256']
mem=ledger['memory_observation'];job_path=ROOT/'benchmarks/construction/pilot-jobs.jsonl'
jobs=job_path.read_bytes() if job_path.exists() else b'';job_prefix=jobs[:mem['pilot_job_log_prefix_bytes']]
assert len(job_prefix)==mem['pilot_job_log_prefix_bytes'] and hashlib.sha256(job_prefix).hexdigest()==mem['pilot_job_log_prefix_sha256']
paper=(ROOT/'paper/main.tex').read_text(encoding='utf-8')
tokens=ledger['token_observation']['provider_interval_union']
assert f"{tokens['total_tokens']:,} total tokens" in paper
assert 'observed partial records' in paper
assert not ledger['complete_project_total_available']
print('Batch hashes, command-log prefix and paper cost snapshot match.')
