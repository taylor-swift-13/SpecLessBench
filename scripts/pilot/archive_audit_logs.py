"""Retain platform audit logs privately; filenames/content may reveal tasks."""
import hashlib,json,shutil
from pathlib import Path
from private_paths import PRIVATE
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'benchmarks/pilot-v1';src=ROOT/'_build/pilot-v1/platform-audit';dst=PRIVATE/'audit-logs'
if dst.exists():raise SystemExit('Audit-log archive exists; verify rather than replace.')
dst.mkdir(parents=True);rows=[]
for report in ('platform-audit.json','interface-audit.json'):
    for step in json.loads((P/report).read_text())['steps']:
        name=step['step']+'.log';data=(src/name).read_bytes();digest=hashlib.sha256(data).hexdigest()
        assert digest==step['log_sha256'];(dst/name).write_bytes(data);rows.append({'name':name,'sha256':digest})
(dst/'manifest.json').write_text(json.dumps({'files':rows},indent=2)+'\n')
print('Archived',len(rows),'sensitive platform logs under the private curator directory.')
