"""Build an honest, deduplicated project cost ledger from recorded telemetry.

Provider cumulative counters are deduplicated by session and overlapping time
intervals. Wall-clock windows and instrumented command intervals are unions,
not sums of nested or concurrently running command durations. Missing history
and infrastructure memory remain null; the output is not a complete bill.
"""
import datetime as dt,hashlib,json
from pathlib import Path
from accounting import ROOT,AUDIT,now
from cost_attribution import effective_commands

KEYS=('input_tokens','cached_input_tokens','cache_write_input_tokens','output_tokens','reasoning_output_tokens','total_tokens')
def timestamp(value):return dt.datetime.fromisoformat(value.replace('Z','+00:00'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def union_seconds(intervals):
    intervals=sorted(intervals);merged=[]
    for start,end in intervals:
        if end<start:raise ValueError('negative interval')
        if merged and start<=merged[-1][1]:merged[-1]=(merged[-1][0],max(end,merged[-1][1]))
        else:merged.append((start,end))
    return sum((e-s).total_seconds()for s,e in merged),len(merged)

def provider_union(sessions):
    totals={k:0 for k in KEYS};merged_count=0;overlap_count=0
    for session,intervals in sessions.items():
        merged=[]
        for start,stop,first,last in sorted(intervals,key=lambda r:r[0]):
            assert all(first[k]<=last[k] for k in KEYS),(session,'non-monotonic counter')
            if merged and start<=merged[-1][1]:
                overlap_count+=1
                assert all(merged[-1][2][k]<=first[k]<=merged[-1][3][k] for k in KEYS),(session,'inconsistent overlap')
                if stop>merged[-1][1]:
                    assert all(merged[-1][3][k]<=last[k] for k in KEYS),(session,'counter reset')
                    merged[-1]=(merged[-1][0],stop,merged[-1][2],last)
            else:merged.append((start,stop,first,last))
        for start,stop,first,last in merged:
            for k in KEYS:totals[k]+=last[k]-first[k]
        merged_count+=len(merged)
    return totals,merged_count,overlap_count

def main():
    batches=[];skipped=[];windows=[];sessions={}
    for path in sorted(AUDIT.glob('batch-*.json')):
        b=json.loads(path.read_text(encoding='utf-8'));base=b.get('baseline')or{};end=b.get('latest_snapshot')or{}
        if not base.get('usage') or not end.get('usage') or not base.get('session_id') or not end.get('provider_timestamp'):
            skipped.append(path.name);continue
        assert base['session_id']==end['session_id']
        diff={k:end['usage'][k]-base['usage'][k]for k in KEYS}
        assert all(v>=0 for v in diff.values()) and diff==b['provider_token_delta'],path.name
        assert diff['total_tokens']==diff['input_tokens']+diff['output_tokens']
        assert diff['cached_input_tokens']<=diff['input_tokens'] and diff['reasoning_output_tokens']<=diff['output_tokens']
        start=timestamp(base['provider_timestamp']);stop=timestamp(end['provider_timestamp']);assert start<=stop
        sessions.setdefault(base['session_id'],[]).append((start,stop,base['usage'],end['usage']))
        started=b.get('request_started_utc');elapsed=b.get('elapsed_request_wall_seconds_to_snapshot')
        if started and elapsed is not None:
            ws=timestamp(started);windows.append((ws,ws+dt.timedelta(seconds=elapsed)))
        batches.append({'batch_id':b['batch_id'],'record':path.relative_to(ROOT).as_posix(),'sha256':sha(path),
            'provider_interval_start_utc':base['provider_timestamp'],'provider_interval_end_utc':end['provider_timestamp'],
            'request_started_utc':started,'request_wall_seconds_to_snapshot':elapsed,
            'provider_delta':diff,'usage_status':b.get('usage_status'),'session_id':base['session_id']})
    totals,merged_count,overlap_count=provider_union(sessions)
    seconds,window_count=union_seconds(windows)
    commands=effective_commands();command_windows=[];invalid=0
    command_path=AUDIT/'commands.jsonl';command_bytes=command_path.read_bytes()
    assert len(command_bytes.splitlines())==len(commands), 'Command log changed during cost snapshot; retry.'
    corrections_path=AUDIT/'attribution-corrections.jsonl'
    for row in commands:
        try:command_windows.append((timestamp(row['started_utc']),timestamp(row['ended_utc'])))
        except (KeyError,TypeError,ValueError):invalid+=1
    command_seconds,command_window_count=union_seconds(command_windows)
    memory=[r for r in commands if r.get('max_process_rss_bytes') is not None]
    peak=max(memory,key=lambda r:r['max_process_rss_bytes'])if memory else None
    record={'schema_version':1,'generated_utc':now(),'complete_project_total_available':False,
       'scope':'observed construction and research batches; not proof-agent evaluation, not a complete bill',
       'batch_count':len(batches),'batch_records':batches,'skipped_batch_records':skipped,
       'token_observation':{'provider_interval_union':totals,'session_count':len(sessions),
          'merged_interval_count':merged_count,'overlapping_intervals_deduplicated':overlap_count,
          'scope':'provider-reported cumulative counters between each recorded baseline and latest snapshot; intervals merged within a session before subtraction',
          'limitations':['prefixes omit unrecorded history, gaps and final tails','windows may include other work in the same conversation; not exact task-only attribution',
             'cached input is a subset of input and reasoning output is a subset of output; do not add them twice',
             'shared authoring usage cannot be exactly assigned to implementation groups'],'complete':False},
       'time_observation':{'request_window_union_seconds':seconds,'request_window_count':len(windows),
          'merged_request_window_count':window_count,'instrumented_command_window_union_seconds':command_seconds,
          'instrumented_command_count':len(commands),'invalid_command_timestamps':invalid,
          'command_log_prefix_bytes':len(command_bytes),'command_log_prefix_sha256':hashlib.sha256(command_bytes).hexdigest(),
          'attribution_corrections_sha256':sha(corrections_path)if corrections_path.exists()else None,
          'merged_instrumented_command_window_count':command_window_count,
          'scope':'request start through recorded snapshot includes idle/wait; command interval union counts overlapping or nested commands once',
          'limitations':['windows and command logs omit historical work, uninstrumented actions and post-snapshot tails','elapsed time is not person-hours or total CPU time'],'complete':False},
       'memory_observation':{'max_observed_single_process_rss_bytes':peak['max_process_rss_bytes']if peak else None,
          'peak_attempt_id':peak['attempt_id']if peak else None,'peak_group_id':peak['group_id']if peak else None,
          'commands_with_rss':len(memory),'commands_without_rss':len(commands)-len(memory),
          'exact_concurrent_process_tree_peak_bytes':None,'hosted_model_inference_peak_bytes':None,
          'scope':'GNU time/wait4 maximum process high-water among instrumented commands and waited descendants; not the simultaneous process-tree sum',
          'limitations':['unmeasured commands or historical activity may have larger peaks','provider does not expose hosted inference memory'],'complete':False},
       'monetary_cost':None,'monetary_cost_reason':'Exact historical model identities and applicable billing rates are not consistently available.',
       'refresh':'python3 scripts/construction/summarize_total_cost.py'}
    path=AUDIT/'total-cost.json';path.write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'batch_count':len(batches),'provider_interval_union':totals,'request_window_union_seconds':seconds,
        'instrumented_command_window_union_seconds':command_seconds,'max_observed_single_process_rss_bytes':record['memory_observation']['max_observed_single_process_rss_bytes']}))
if __name__=='__main__':main()
