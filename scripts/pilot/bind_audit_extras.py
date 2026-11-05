"""Bind remaining build-support scripts required for reproducible audits."""
import hashlib,json
from pathlib import Path
from private_paths import PRIVATE
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'benchmarks/pilot';out=PRIVATE/'audit-extras.json'
if out.exists():raise SystemExit('Audit extras already exist.')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
scripts=[p for p in (ROOT/'scripts/construction').iterdir() if p.is_file() and p.suffix in ('.py','.ml')]
record={'reason':'Freeze construction scripts and the extracted-Rocq driver for the platform audit.',
        'files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}for p in sorted(scripts)]}
out.write_text(json.dumps(record,indent=2)+'\n');m=json.loads((P/'manifest.json').read_text())
m['audit_extras_sha256']=sha(out);m['audit_extra_count']=len(scripts)
(P/'manifest.json').write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
print('Bound',len(scripts),'support scripts.')
