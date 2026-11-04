"""Run the integration audit under measurement; then refresh aggregate metadata."""
import json,sys
from boundaries_common import ROOT
from accounting import AUDIT,append,now
from measure import measured
def main():
    issue='BOUNDARY-AUDIT-HISTORICAL-SCHEMA'
    prior=[json.loads(s)for s in(AUDIT/'issues.jsonl').read_text().splitlines()]
    if not any(r['id']==issue for r in prior):
        append(AUDIT/'issues.jsonl',{'schema_version':1,'timestamp_utc':now(),'id':issue,'kind':'audit-tool-schema-compatibility','status':'resolved',
          'repair':'benchmarks/construction/repairs/21b05c9120bc/revision.json','programs_domains_targets_changed':False,
          'description':'Three initial audit invocations failed: two readers required batch_id absent in old command rows; the aggregator required a top-level AST count absent in old QCIP summaries. Defaults use the original QCIP batch and the actual pinned AST export list.',
          'failed_invocations':[{'command':'summarize_boundaries.py','error':'KeyError batch_id','reported_tool_wall_seconds':1.2882828},{'command':'summarize_algorithms.py','error':'KeyError batch_id','reported_tool_wall_seconds':1.2096408},{'command':'summarize_all.py','error':'KeyError clight_ast_count','reported_tool_wall_seconds':0.8435336}],
          'failed_process_cpu_seconds':None,'failed_process_peak_rss_bytes':None,'telemetry_gap':'initial metadata audit commands were not GNU-time wrapped; tool-reported wall scope differs from measured process wall',
          'shared_request_wall_includes_these_failures':True})
    for script in ('scripts/construction/summarize_algorithms.py','scripts/construction/summarize_boundaries.py','scripts/construction/summarize_all.py','scripts/construction/check_three_platform.py','scripts/curation/check_inventory.py'):
        output,_=measured([sys.executable,str(ROOT/script)],'shared-boundaries-audit',script.rsplit('/',1)[-1],role='envelope')
        print(output.decode(),end='',flush=True)
    current=[json.loads(s)for s in(AUDIT/'issues.jsonl').read_text().splitlines()]
    if not any(r['id']=='CMD-dc2158556b1a-resolution'for r in current):
        append(AUDIT/'issues.jsonl',{'schema_version':1,'timestamp_utc':now(),'id':'CMD-dc2158556b1a-resolution','resolves':'CMD-dc2158556b1a','kind':'resolution','status':'resolved',
          'repair':'benchmarks/construction/repairs/e2e0789d205b/revision.json','programs_domains_targets_changed':False,
          'description':'Move proof acceptance contract path assignment before its first read in the inventory checker; full inventory/source/proof-interface/paper-reference checks now pass.'})
    # Include all finished audit envelopes in the summary. These tiny metadata
    # refresh calls are explicitly outside the instrumented process-cost scope.
    from summarize_boundaries import main as boundary
    from summarize_all import main as aggregate
    boundary();aggregate()
if __name__=='__main__':main()
