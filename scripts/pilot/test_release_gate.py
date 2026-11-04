"""Every pilot task must fail closed until a release is explicitly certified."""
import json
from pathlib import Path
from release_gate import decide
ROOT=Path(__file__).resolve().parents[2]
manifest=json.loads((ROOT/'benchmarks/pilot-v1/manifest.json').read_text())
assert len(manifest['contexts'])==71
for row in manifest['contexts']:
    for platform in ('lean','rocq','compcert'):
        assert decide(row['pilot_id'],platform)=={'status':'unavailable','reason':'solver package and evaluator are not certified'}
assert decide('P-0000000000000000','lean')['status']=='unknown-task'
assert decide(manifest['contexts'][0]['pilot_id'],'other')['status']=='invalid-request'
print('All 213 unpublished task/platform entries fail closed; no proof ran.')
