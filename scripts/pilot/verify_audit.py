"""Verify audit reports and privately archived logs without exposing labels."""
import hashlib,json
from pathlib import Path
from private_paths import PRIVATE
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'benchmarks/pilot'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for report,snapshot in [('platform-audit.json','manifest-at-platform-audit.json'),('interface-audit.json','manifest-at-interface-audit.json')]:
    audit=json.loads((P/report).read_text());assert audit['status']=='passed' and sha(P/snapshot)==audit['frozen_manifest_sha256']
    for row in audit['steps']:
        assert row['exit_code']==0 and sha(PRIVATE/'audit-logs'/(row['step']+'.log'))==row['log_sha256']
ast=json.loads((P/'ast-audit.json').read_text());assert ast['ast_count']==ast['byte_identical_count']==103 and not ast['mismatch_count']
obligations=json.loads((P/'obligation-audit.json').read_text())
assert obligations['status']=='passed' and obligations['equivalence_obligations']==obligations['literal_refutation_obligations']==213
obligation_logs=PRIVATE/'obligation-logs';index=obligation_logs/'manifest.json'
assert sha(index)==obligations['private_log_index_sha256']
for row in json.loads(index.read_text())['files']:assert sha(obligation_logs/row['name'])==row['sha256']
prototype=json.loads((P/'grader-prototype.json').read_text());assert prototype['status']=='synthetic-tests-passed' and not prototype['release_ready']
for row in prototype['components']:assert sha(ROOT/row['path'])==row['sha256']
for row in prototype['tests']:assert sha(ROOT/'scripts/pilot'/row['test'])==row['script_sha256'] and row['exit_code']==0
print('Platform/interface audits, 103 AST comparisons and synthetic grader evidence match.')
