"""Privately archive per-platform goal-typecheck logs and bind their hashes."""
import hashlib,json,os,shutil
from pathlib import Path
from private_paths import PRIVATE
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'benchmarks/pilot';source=ROOT/'_build/pilot-v1/obligation-audit';dest=PRIVATE/'obligation-logs'
if dest.exists():raise SystemExit('Obligation-log archive exists; verify rather than replace.')
dest.mkdir(mode=0o700);report_path=P/'obligation-audit.json';report=json.loads(report_path.read_text())
assert report['status']=='passed' and report['aggregate_compilation_units']==24
rows=[]
for row in report['compiled']:
    name='Check_'+row['module']+'_'+row['platform']+'.log';src=source/name;dst=dest/name
    shutil.copyfile(src,dst);os.chmod(dst,0o600);digest=hashlib.sha256(dst.read_bytes()).hexdigest()
    assert digest==hashlib.sha256(src.read_bytes()).hexdigest()
    rows.append({'name':name,'sha256':digest})
index=dest/'manifest.json';index.write_text(json.dumps({'files':rows},indent=2)+'\n');os.chmod(index,0o600)
report['private_log_index_sha256']=hashlib.sha256(index.read_bytes()).hexdigest()
report['private_log_count']=len(rows)
report_path.write_text(json.dumps(report,indent=2)+'\n')
print('Archived',len(rows),'goal-typecheck logs privately; no final proofs.')
