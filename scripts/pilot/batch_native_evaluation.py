"""One serial pass over Lean/Rocq, Goal off then on, with fresh isolated runs."""
import collections
import fcntl
import json
import os
import time
from pathlib import Path

from prepare_evaluation import PACKAGES
from run_evaluation_wsl import dump, now, run
from selection import selection
from verify_freeze import main as verify_freeze
from native_runtime_policy import (RUNTIME_CONFIG_SHA256, RUNTIME_SCOPE_REVISION, pair_runtime_hold,
                                  retained_storage_hold, runtime_config, storage_hold)

BASE=Path.home()/'.local/share/speclessbench/batches/native-luna-medium'


def jobs(contexts):
    return [{'task_id':r['pilot_id'],'platform':platform,'goal_mode':mode,
             'status':'pending-package','attempts':[],'reports':[]}
            for r in contexts for platform in ('lean','rocq') for mode in ('off','on')]


def summarize(reports):
    return {'completed':len(reports),'accepted':sum(r['result']['status']=='accepted' for r in reports),
            'tokens':{k:sum((r['resources'].get('tokens') or {}).get(k,0) for r in reports)
                      for k in ('input_tokens','cached_input_tokens','output_tokens')},
            'missing_usage':sum(r['resources'].get('tokens') is None for r in reports),
            'incomplete_usage':sum(not r['resources'].get('token_usage_complete',False) for r in reports),
            'agent_seconds':sum(r['resources'].get('agent_wall_seconds') or 0 for r in reports),
            'checker_seconds':sum(r['resources'].get('checker_wall_seconds') or 0 for r in reports),
            'wall_seconds':sum(r['resources'].get('total_wall_seconds') or 0 for r in reports),
            'native_turns':sum((r.get('native_goal_session') or {}).get('native_turn_count',0) for r in reports),
            'agent_memory_peak_bytes':max([r['resources'].get('agent_max_cgroup_memory_peak_bytes') or 0 for r in reports],default=0) or None,
            'checker_memory_peak_bytes':max([r['resources'].get('checker_max_cgroup_memory_peak_bytes') or 0 for r in reports],default=0) or None,
            'billing':None,'hosted_model_memory':None}


def main():
    os.umask(0o077);BASE.mkdir(parents=True,exist_ok=True)
    with (BASE.parent/'worker.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        verify_freeze();status=BASE/'status.json'
        state=json.loads(status.read_text()) if status.exists() else {
            'schema_version':1,'created_utc':now(),'model':'gpt-6-luna','reasoning_effort':'medium',
            'platforms':['lean','rocq'],'goal_modes':['off','on'],'concurrency':1,
            'time_limit_seconds':7200,'manual_resumes':False,'jobs':jobs(selection()[0])}

        def save(phase, *, stopped=False):
            state.update(phase=phase,worker_pid=None if stopped else os.getpid(),updated_utc=now())
            state['counts']=dict(collections.Counter(j['status'] for j in state['jobs']))
            state['ready_runs']=sum(j['status']=='pending-package' and (PACKAGES/j['task_id']/j['platform']/'registry.json').exists() for j in state['jobs'])
            state['unprepared_runs']=state['counts'].get('pending-package',0)-state['ready_runs']
            reports=[json.loads(Path(p).read_text()) for j in state['jobs'] for p in j['reports']]
            state['totals']=summarize(reports)
            state['by_condition']={platform+'/'+mode:summarize([r for r in reports if r['configuration']['platform']==platform and r['configuration']['goal_mode']==mode])
                                   for platform in ('lean','rocq') for mode in ('off','on')}
            dump(status,state)

        if state.get('paused'):
            save('paused',stopped=True);return
        interrupted=[j for j in state['jobs'] if j['status']=='running']
        if interrupted:
            for j in interrupted:j['status']='interrupted-needs-review'
            save('blocked-interrupted',stopped=True);return
        if any(j['status'] in ('infrastructure-error','interrupted-needs-review') for j in state['jobs']):
            save('blocked-needs-review',stopped=True);return
        while True:
            ready=[j for j in state['jobs'] if j['status']=='pending-package' and (PACKAGES/j['task_id']/j['platform']/'registry.json').is_file()]
            if not ready:
                if all(j['status']!='pending-package' for j in state['jobs']):
                    save('finished',stopped=True);return
                save('waiting-for-certified-packages');time.sleep(30);continue
            job=ready[0]

            def started(path):
                job['attempts'].append(str(path));job['current_run']=str(path);save('running')

            try:
                with (PACKAGES/'activity.lock').open('a') as activity:
                    fcntl.flock(activity,fcntl.LOCK_EX)
                    try:
                        hold=storage_hold() or retained_storage_hold() or pair_runtime_hold(job,state['jobs'])
                    except (OSError,RuntimeError) as error:
                        hold={'kind':'runtime','reason':'Runtime admission could not be verified; no attempt started',
                              'error_type':type(error).__name__}
                    if hold:
                        state['preflight_hold']=hold
                        state['prospective_runtime']={'revision':RUNTIME_SCOPE_REVISION,
                                                      'expected_config_sha256':RUNTIME_CONFIG_SHA256}
                        save('blocked-infrastructure-storage' if hold['kind']=='storage' else 'blocked-runtime-revision',stopped=True)
                        return
                    state.pop('preflight_hold',None)
                    job['status']='running';save('running')
                    directory,report=run(job['task_id'],job['platform'],timeout=7200,
                                         goal_mode=job['goal_mode'],on_run=started)
                report_path=str(directory/'report.json')
                result_status=report['result']['status']
                completed=result_status in ('accepted','rejected','timeout')
                job.pop('current_run',None)
                if completed:
                    job['reports'].append(report_path)
                    job['status']=result_status
                else:
                    job.setdefault('infrastructure_reports',[]).append(report_path)
                    job['status']='infrastructure-error'
                    job['detail']=report['result'].get('detail',result_status)
                with (BASE/'history.jsonl').open('a') as history:
                    history.write(json.dumps({'ended_utc':now(),'task_id':job['task_id'],
                                  'platform':job['platform'],'goal_mode':job['goal_mode'],
                                  'result':report['result'],'report':report_path,
                                  'included_in_completed_totals':completed})+'\n')
                    history.flush();os.fsync(history.fileno())
                if not completed:
                    save('blocked-infrastructure',stopped=True);return
                save('between-runs')
            except Exception as error:
                if job['status'] not in ('accepted','rejected','timeout'):
                    job['status']='infrastructure-error';job['detail']=type(error).__name__+': '+str(error)
                save('blocked-infrastructure',stopped=True);return


if __name__=='__main__':
    main()
