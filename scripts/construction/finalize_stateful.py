"""Measured integration audit and append-only resolution records; no proofs."""
import json,sys
from stateful_common import ROOT,CORE
from accounting import AUDIT,append,now
from measure import measured
def main():
    for script in ('scripts/construction/regress_stateful_contract.py','scripts/construction/summarize_algorithms.py','scripts/construction/summarize_boundaries.py',
      'scripts/construction/summarize_stateful.py','scripts/construction/summarize_all.py','scripts/construction/check_three_platform.py','scripts/curation/check_inventory.py'):
        out,_=measured([sys.executable,str(ROOT/script)],'shared-stateful-audit',script.rsplit('/',1)[-1],role='envelope')
        print(out.decode(),end='',flush=True)
    issues=[json.loads(s)for s in(AUDIT/'issues.jsonl').read_text().splitlines()];known={r['id']for r in issues}
    resolutions=[
      ('CMD-0557dc2c6f7f','2cd892e66976','Lean draft record syntax, XOR name and tuple numeral typing repaired in design-v0.5.1; all native definitions, target types and full tests pass.'),
      ('CMD-a5ce5ff887ec','95f817610488','Fixed Python for-clause typo in the call-graph auditor. All nine actual ASTs have closed direct-call graphs, with three to five call edges.'),
      ('CMD-e1a956a13251','90bfade295b4','Frame supplement pair/port results agreed, but its reused coverage gate lacked reset-after-error. Added reset/resume inputs and reran successfully; failed report/cost retained.'),
      ('frames-2026-11-03T150612588330+0000-reference-event-coverage-missing','90bfade295b4','Supplement now includes 32 reset-after-error events while preserving its 2592 multi-frame-feed events. Programs/domains/targets unchanged.')]
    for issue,repair,description in resolutions:
        assert issue in known,issue
        if issue+'-resolution'not in known:
            append(AUDIT/'issues.jsonl',{'schema_version':1,'timestamp_utc':now(),'id':issue+'-resolution','resolves':issue,'kind':'resolution','status':'resolved',
              'repair':f'benchmarks/construction/repairs/{repair}/revision.json','description':description,'final_proofs_attempted':False})
    if 'STATEFUL-MULTIFRAME-COVERAGE'not in known:
        append(AUDIT/'issues.jsonl',{'schema_version':1,'timestamp_utc':now(),'id':'STATEFUL-MULTIFRAME-COVERAGE','kind':'construction-coverage-audit','status':'resolved',
          'group_id':'incremental-frame-stream','main_multiframe_events':1,'supplement_multiframe_events':2592,'supplement_novel_inputs':3805,
          'programs_domains_targets_changed':False,'resolution':'Add disjoint deterministic supplemental inputs; both corpora and all failures/costs retained. No algorithmic mismatch inferred.'})
    # Include the completed audit envelopes. These tiny JSON refresh calls have
    # explicitly disclosed housekeeping telemetry gaps rather than fake zeros.
    from summarize_stateful import main as stateful
    from summarize_all import main as aggregate
    stateful();aggregate()
if __name__=='__main__':main()
