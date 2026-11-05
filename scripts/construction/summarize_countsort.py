"""Audit the selected full classical-algorithm runs and account for each group once."""
import gzip, hashlib, json, shutil
from pathlib import Path
from countsort_common import ROOT, CORE, GROUPS, LEAN, COQC, FIVE, REVISION
from accounting import AUDIT, now
from cost_attribution import effective_commands

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    registry = json.loads((CORE/'groups.json').read_text())
    build = json.loads((CORE/'compcert/build.json').read_text())
    assert len(registry['groups']) == 1 and len(build['exports']) == 3
    assert registry['io_header_sha256']==sha(ROOT/'benchmarks/tasks/qcip-core/common/io.h')
    for row in registry['protected_files']:
        assert sha(CORE/row['path']) == row['sha256'], row['path']
    for row in build['exports']:
        assert sha(CORE/row['path']) == row['sha256'], row['path']
    commands = effective_commands(); summaries = []
    for group in registry['groups']:
        name, gid = group['family'], group['group_id']
        report = json.loads((CORE/'evidence'/f'{name}.json').read_text())
        assert not report['smoke'] and not report['unexpected_disagreements']
        assert report['negative_distinguishing_inputs'] > 0 and not report['final_proof_attempted']
        assert not report['clight_execution_tested']
        assert report['registry_sha256'] == sha(CORE/'groups.json')
        assert report['generator_sha256'] == sha(ROOT/'scripts/construction/differential_countsort.py')
        assert report['corpus_generator_sha256'] == sha(ROOT/'scripts/construction/countsort_cases.py')
        corpus = ROOT/report['corpus']; assert sha(corpus) == report['corpus_sha256']
        with gzip.open(corpus, 'rt') as stream:
            cases = [tuple(json.loads(line)) for line in stream]
        assert len(cases) == len(set(cases)) == report['case_count']
        independent=json.loads((CORE/'evidence/oracles'/f'{name}.json').read_text())
        assert independent['case_count']==len(cases) and independent['unexpected_differences']==0
        assert independent['corpus_sha256']==report['corpus_sha256']
        assert independent['oracle_script_sha256']==sha(ROOT/'scripts/construction/audit_countsort_oracles.py')
        assert independent['reference_output_gzip_sha256']==sha(ROOT/independent['reference_output_gzip'])
        path = AUDIT/'groups'/f'{gid}.json'; cost = json.loads(path.read_text())
        owned = [r for r in commands if r['group_id'] == gid]
        envelopes = [r for r in owned if r.get('measurement_role') == 'envelope']
        uncovered = [r for r in owned if r.get('measurement_role') != 'envelope' and not any(e['started_utc'] <= r['started_utc'] and r['ended_utc'] <= e['ended_utc'] for e in envelopes)]
        for key in ('wall_seconds', 'cpu_user_seconds', 'cpu_system_seconds'):
            cost['nonduplicated_tool_wall_seconds' if key == 'wall_seconds' else 'nonduplicated_'+key] = sum(r[key] or 0 for r in envelopes + uncovered)
        cost.update(shared_batch_id='construction-continuation-v0.11', one_record_per_implementation_group=True,
                    semantic_contexts=len(group['tasks']), platform_instances=3*len(group['tasks']),
                    cost_total_rule='all attempts: envelopes plus uncovered details; do not add nested costs or multiply by context/platform',
                    case_count=report['case_count'], program_executions=report['program_executions'], validity_evaluations=report['validity_evaluations'])
        path.write_text(json.dumps(cost, indent=2)+'\n')
        summaries.append(dict(group_id=gid, family=name, unique_inputs=report['case_count'],
            program_executions=report['program_executions'], validity_evaluations=report['validity_evaluations'],
            duplicates_removed=report['duplicate_inputs_removed'], negative_inputs=report['negative_distinguishing_inputs'],
            source_derived_inputs=0, reference_event_counts=report['reference_status_histogram'],
            unexpected_disagreements=0, independent_oracle=independent['oracle'], tool_wall_seconds=cost['nonduplicated_tool_wall_seconds'],
            max_process_rss_bytes=cost['max_process_rss_bytes'], cost_record=path.relative_to(ROOT).as_posix()))
    manifest_path=ROOT/'benchmarks/proof-interface/manifest.json'; manifest=json.loads(manifest_path.read_text())
    assert {t['id'] for g in registry['groups'] for t in g['tasks']} <= {c['context_id'] for c in manifest['contexts']}
    for row in manifest['files']: assert sha(manifest_path.parent/row['path']) == row['sha256']
    assert manifest['submission_validator_sha256'] == sha(ROOT/'scripts/construction/submission_contract.py')
    assert manifest['validation_evidence_sha256'] == sha(manifest_path.parent/'validation.json')
    shared = [r for r in commands if r['group_id'].startswith('shared') and r['batch_id']=='construction-continuation-v0.11']
    count = sum(len(g['tasks']) for g in registry['groups'])
    summary=dict(schema_version=1, revision=REVISION, timestamp_utc=now(), implementation_groups=len(GROUPS),
        semantic_contexts=count, platform_instances=3*count, clight_ast_count=len(build['exports']), groups=summaries,
        unique_inputs=sum(g['unique_inputs'] for g in summaries), program_executions=sum(g['program_executions'] for g in summaries),
        validity_evaluations=sum(g['validity_evaluations'] for g in summaries), unexpected_disagreements=0,
        final_proof_attempted=False, labels_certified=False, source_registry_sha256=sha(CORE/'groups.json'),
        compcert_build_sha256=sha(CORE/'compcert/build.json'), shared_usage_batch='batch-construction-continuation-v0.11.json',
        coverage_scope='selected full runs only; smoke and failed attempts retained in costs',
        clight_execution_tested=False, exact_process_tree_peak_bytes=None, hosted_inference_memory_bytes=None,
        uninstrumented_housekeeping_costs=None,
        uninstrumented_scope='bootstrap, editing and preliminary direct compiler checks lack exact CPU and peak RSS; shared provider token counts are prefix-only and not allocated per group',
        shared_tool_wall_seconds=sum(r['wall_seconds'] for r in shared),
        shared_max_process_rss_bytes=max((r['max_process_rss_bytes'] or 0 for r in shared),default=None),
        tools_at_audit=[dict(path=str(p),sha256=sha(Path(p))) for p in (LEAN, COQC, FIVE+'/clightgen', FIVE+'/coqc', shutil.which('gcc'), shutil.which('ocamlopt'))])
    (AUDIT/'summary-countsort-v0.11.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ('implementation_groups','semantic_contexts','platform_instances','unique_inputs','program_executions')}))

if __name__ == '__main__': main()
