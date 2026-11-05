"""Derive the evaluation set without altering the frozen pilot snapshot."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'benchmarks/pilot-v1'


def selection():
    manifest_bytes=(BASE/'manifest.json').read_bytes()
    policy=json.loads((BASE/'evaluation-policy.json').read_text())
    if hashlib.sha256(manifest_bytes).hexdigest()!=policy['frozen_manifest_sha256']:
        raise ValueError('Evaluation policy does not match frozen manifest')
    manifest=json.loads(manifest_bytes);excluded=set(policy['reference_only_families'])
    if not excluded or not excluded<={x['split_family'] for x in manifest['contexts']}:
        raise ValueError('Invalid reference family')
    eligible=[x for x in manifest['contexts'] if x['split_family'] not in excluded]
    reference=[x for x in manifest['contexts'] if x['split_family'] in excluded]
    if (len(eligible),len({x['split_family'] for x in eligible}),sum(len(x['platforms']) for x in eligible))!=(policy['evaluation_contexts'],policy['evaluation_families'],policy['evaluation_platform_instances']):
        raise ValueError('Evaluation counts do not match policy')
    return eligible,reference


if __name__=='__main__':
    eligible,reference=selection()
    print(json.dumps({'eligible_contexts':len(eligible),'eligible_families':len({x['split_family'] for x in eligible}),
                      'platform_instances':sum(len(x['platforms']) for x in eligible),
                      'reference_contexts':len(reference)},sort_keys=True))
