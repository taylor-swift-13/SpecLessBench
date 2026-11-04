"""Append attribution corrections; never rewrite original command events."""
import json
from boundaries_common import GROUPS
from accounting import AUDIT,append,now
def main():
    owned={g[1]for g in GROUPS};rows=[json.loads(s)for s in(AUDIT/'commands.jsonl').read_text().splitlines()]
    affected=[r for r in rows if(r['group_id']in owned or r['group_id'].startswith('shared-boundaries'))and r['batch_id']!='boundaries-v0.4']
    correction={'schema_version':1,'timestamp_utc':now(),'id':'BOUNDARY-COST-BATCH-IMPORT','kind':'construction-telemetry-attribution',
      'status':'corrected-by-append-only-override; remeasurement follows','original_batch_id':'algorithms-v0.3','correct_batch_id':'boundaries-v0.4',
      'affected_attempt_ids':[r['attempt_id']for r in affected],'repair':'benchmarks/construction/repairs/265486496115/revision.json',
      'programs_domains_targets_changed':False,'description':'Legacy helper module import mutated batch environment. Original timing/RSS remain valid and are charged once to actual boundary groups; do not also count these as algorithm shared tools.'}
    append(AUDIT/'issues.jsonl',correction);append(AUDIT/'attribution-corrections.jsonl',correction)
    print(len(affected),'original command records preserved with attribution override')
if __name__=='__main__':main()
