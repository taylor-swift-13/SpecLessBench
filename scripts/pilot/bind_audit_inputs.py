"""Hash build/audit dependency inputs omitted by the initial snapshot."""
import hashlib,json
from pathlib import Path
from private_paths import PRIVATE
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'benchmarks/pilot'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
fixed=['scripts/construction/build_three_platform.py','scripts/construction/export_compcert.py',
       'benchmarks/tasks/qcip-core/tasks.json','benchmarks/tasks/qcip-core/three-platform.json']
common=sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts/construction').glob('*_common.py'))
builds=sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts/construction').glob('build_*.py'))
registries=sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'benchmarks/tasks').glob('*-core/groups.json'))
paths=sorted(set(fixed+common+builds+registries));out=PRIVATE/'audit-inputs.json'
if out.exists():raise SystemExit('Audit-input addendum exists; verify rather than replace.')
record={'reason':'Bind source registries and build configuration used by the read-only platform audit.',
        'files':[{'path':name,'sha256':sha(ROOT/name)}for name in paths]}
out.write_text(json.dumps(record,indent=2)+'\n');manifest=json.loads((P/'manifest.json').read_text())
manifest['audit_inputs_sha256']=sha(out);manifest['audit_input_count']=len(paths)
(P/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
print('Bound',len(paths),'build and registry dependencies.')
