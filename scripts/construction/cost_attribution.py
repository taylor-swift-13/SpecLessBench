"""Resolve append-only telemetry attribution corrections without deleting costs."""
import json
from accounting import AUDIT
def effective_commands():
    rows=[json.loads(s)for s in(AUDIT/'commands.jsonl').read_text().splitlines()]
    overrides={}
    p=AUDIT/'attribution-corrections.jsonl'
    if p.exists():
        for line in p.read_text().splitlines():
            r=json.loads(line)
            for attempt in r['affected_attempt_ids']:overrides[attempt]=r['correct_batch_id']
    return [dict(r,batch_id=overrides.get(r['attempt_id'],r.get('batch_id','three-platform-v0.2')))for r in rows]
