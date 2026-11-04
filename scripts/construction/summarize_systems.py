"""Audit source/AST/test lineage and nonduplicated per-group construction costs."""
import gzip,hashlib,json,shutil
from pathlib import Path
from systems_common import ROOT,CORE,BUILD,GROUPS,LEAN,COQC,FIVE,REVISION
from accounting import AUDIT,append,now
from cost_attribution import effective_commands
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    reg=json.loads((CORE/'groups.json').read_text());meta=json.loads((CORE/'compcert/build.json').read_text())
    assert len(reg['groups'])==len(GROUPS) and len(meta['exports'])==3*len(GROUPS)
    for r in reg['protected_files']:assert sha(CORE/r['path'])==r['sha256'],r['path']
    for r in meta['exports']:assert sha(CORE/r['path'])==r['sha256'],r['path']
    commands=effective_commands();summaries=[]
    fixtures=json.loads((CORE/'fixtures.json').read_text())
    for g in reg['groups']:
        name=g['family'];gid=g['group_id'];report=json.loads((CORE/'evidence'/(name+'.json')).read_text())
        assert not report['smoke']and report['unexpected_disagreements']==0 and report['negative_distinguishing_inputs']>0
        assert not report['final_proof_attempted']and not report['clight_execution_tested']
        assert report['registry_sha256']==sha(CORE/'groups.json')
        assert report['generator_sha256']==sha(ROOT/'scripts/construction/differential_systems.py')
        assert report['corpus_generator_sha256']==sha(ROOT/'scripts/construction/systems_cases.py')
        assert report['fixtures_sha256']==sha(CORE/'fixtures.json')
        corpus=ROOT/report['corpus'];assert sha(corpus)==report['corpus_sha256']
        with gzip.open(corpus,'rt')as stream:cases=[json.loads(s)for s in stream]
        distinct={tuple(x) for x in cases}
        assert len(cases)==len(distinct)==report['case_count']
        source_cases=report['cases_by_origin'].get('source',0)
        fixture=fixtures.get(name,{})
        assert all(tuple(x) in distinct for x in fixture.get('inputs',[]))
        if 'samples' in fixture:
            assert source_cases > 0
            assert sum(x[7:]==fixture['samples'] for x in cases)>=source_cases
        else:
            assert source_cases==len(fixture.get('inputs',[]))
        path=AUDIT/'groups'/(gid+'.json');cost=json.loads(path.read_text());owned=[r for r in commands if r['group_id']==gid]
        envelopes=[r for r in owned if r.get('measurement_role')=='envelope']
        uncovered=[r for r in owned if r.get('measurement_role')!='envelope'and not any(e['started_utc']<=r['started_utc']and r['ended_utc']<=e['ended_utc']for e in envelopes)]
        cost['nonduplicated_tool_wall_seconds']=sum(r['wall_seconds']for r in envelopes+uncovered)
        for k in ('cpu_user_seconds','cpu_system_seconds'):cost['nonduplicated_'+k]=sum(r[k]or 0 for r in envelopes+uncovered)
        cost.update(shared_batch_id='systems-v0.6',one_record_per_implementation_group=True,semantic_contexts=2,platform_instances=6,
          cost_total_rule='all attempts: envelopes plus uncovered details; never add nested costs or multiply by platform/context',
          case_count=report['case_count'],program_executions=report['program_executions'],validity_evaluations=report['validity_evaluations'])
        path.write_text(json.dumps(cost,indent=2)+'\n')
        summaries.append({'group_id':gid,'family':name,'unique_inputs':report['case_count'],'program_executions':report['program_executions'],
          'validity_evaluations':report['validity_evaluations'],'duplicates_removed':report['duplicate_inputs_removed'],'negative_inputs':report['negative_distinguishing_inputs'],
          'source_derived_inputs':source_cases,
          'reference_event_counts':report['reference_status_histogram'],'unexpected_disagreements':0,'tool_wall_seconds':cost['nonduplicated_tool_wall_seconds'],
          'max_process_rss_bytes':cost['max_process_rss_bytes'],'cost_record':path.relative_to(ROOT).as_posix()})
    calls=json.loads((CORE/'call-graphs.json').read_text());assert len(calls['functions_and_calls'])==len(meta['exports'])
    for row in calls['functions_and_calls']:
        assert sha(CORE/row['ast'])==row['ast_sha256']and row['all_direct_callees_have_bodies']
        assert row['maximum_direct_call_edges']>=3
    manifest=ROOT/'benchmarks/proof-interface/v1/manifest.json';interface=json.loads(manifest.read_text())
    expected={t['id']for g in reg['groups']for t in g['tasks']}
    assert expected<={c['context_id']for c in interface['contexts']}
    for r in interface['files']:assert sha(manifest.parent/r['path'])==r['sha256'],r['path']
    assert interface['submission_validator_sha256']==sha(ROOT/'scripts/construction/submission_contract.py')
    assert interface['validation_evidence_sha256']==sha(manifest.parent/'validation.json')
    shared=[r for r in commands if r['group_id'].startswith('shared')and r['batch_id']=='systems-v0.6']
    summary={'schema_version':1,'revision':REVISION,'timestamp_utc':now(),'implementation_groups':len(GROUPS),'semantic_contexts':2*len(GROUPS),
      'platform_instances':6*len(GROUPS),'clight_ast_count':len(meta['exports']),'groups':summaries,'unique_inputs':sum(g['unique_inputs']for g in summaries),
      'program_executions':sum(g['program_executions']for g in summaries),'validity_evaluations':sum(g['validity_evaluations']for g in summaries),
      'event_count_scope':'multi-label reference operation/output events, not independent inputs; legacy per-run report field is reference_status_histogram',
      'coverage_scope':'selected successful full evidence; smoke and failed/repeated attempts remain in costs but do not inflate reported coverage',
      'unexpected_disagreements':0,'final_proof_attempted':False,'labels_certified':False,'source_registry_sha256':sha(CORE/'groups.json'),'compcert_build_sha256':sha(CORE/'compcert/build.json'),
      'tools_at_audit':[{'path':str(p),'sha256':sha(Path(p))}for p in(LEAN,COQC,FIVE+'/clightgen',FIVE+'/coqc',shutil.which('gcc'),shutil.which('ocamlopt'))],
      'generator_dependencies':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}for p in(ROOT/'scripts/construction/differential_systems.py',ROOT/'scripts/construction/systems_cases.py',ROOT/'scripts/construction/systems_common.py')],
      'shared_usage_batch':'batch-systems-v0.6.json','exact_process_tree_peak_bytes':None,'hosted_inference_memory_bytes':None,
      'call_graphs_sha256':sha(CORE/'call-graphs.json'),
      'fixtures_sha256':sha(CORE/'fixtures.json'),
      'local_telemetry_scope':'prepare, compiler/execution commands, differential and audit envelopes instrumented; bootstrap, editing and tiny final metadata refreshes lack complete process telemetry',
      'uninstrumented_housekeeping_costs':None,'uninstrumented_housekeeping_reason':'bootstrap/editor overhead remains in shared request wall time; exact CPU/RSS and hosted inference memory unavailable',
      'shared_tool_wall_seconds':sum(r['wall_seconds']for r in shared),'shared_max_process_rss_bytes':max((r['max_process_rss_bytes']or 0 for r in shared),default=None),
      'cost_events_complete_through':max((r['ended_utc']for r in commands),default=None)}
    (AUDIT/'summary-systems-v0.6.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:summary[k]for k in('implementation_groups','semantic_contexts','platform_instances','unique_inputs','program_executions','validity_evaluations')}))
if __name__=='__main__':main()
