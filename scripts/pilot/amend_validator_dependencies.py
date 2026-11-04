"""Bind validator dependencies omitted by the first source snapshot.

The pilot's task definitions are unchanged. This explicit addendum is linked
from the public snapshot and cannot silently replace the original mapping.
"""
import hashlib,json
from pathlib import Path
from private_paths import PRIVATE
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'benchmarks/pilot-v1'
paths=['scripts/construction/differential_algorithms.py','scripts/construction/algorithms_common.py',
       'scripts/construction/accounting.py','scripts/construction/measure.py']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
public=json.loads((P/'manifest.json').read_text());out=PRIVATE/'validator-dependencies.json'
if out.exists():raise SystemExit('Dependency addendum already exists; verify rather than replace.')
record={'reason':'First freeze omitted validator import dependencies; no task or goal was changed.',
        'files':[{'path':name,'sha256':sha(ROOT/name)}for name in paths]}
out.write_text(json.dumps(record,indent=2)+'\n');public['validator_addendum_sha256']=sha(out);public['validator_dependency_count']=len(paths)
(P/'manifest.json').write_text(json.dumps(public,indent=2,ensure_ascii=False)+'\n')
print('Bound',len(paths),'previously omitted validator dependencies.')
