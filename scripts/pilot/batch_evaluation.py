"""Durable serial evaluator. Unprepared instances wait; they are not failures."""
import argparse
import fcntl
import json
import os
import time
from pathlib import Path

from prepare_evaluation import PACKAGES
from run_evaluation_wsl import dump, now, run
from evaluation_prompts import VARIANTS
from selection import selection
from verify_freeze import main as verify_freeze

BASE = Path.home()/'.local/share/speclessbench/batches/luna-medium'


def make_jobs(contexts, variants):
    return [{'task_id': r['pilot_id'], 'platform': platform,
             'prompt_variant': variant, 'status': 'pending-package', 'attempts': [], 'reports': []}
            for r in contexts for platform in r['platforms'] for variant in variants]


def main(resume=False, prompt_variant='verification'):
    base = BASE if prompt_variant == 'verification' else BASE.with_name('luna-medium-'+prompt_variant)
    os.umask(0o077); base.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (BASE.parent/'worker.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        verify_freeze()
        state_file = base/'status.json'
        if state_file.exists():
            state = json.loads(state_file.read_text())
            if state.get('prompt_variant', prompt_variant) != prompt_variant:
                raise ValueError('Batch prompt variant mismatch')
            if state.get('paused'):
                if not resume:
                    print('Evaluation paused by user; no tasks launched.', flush=True); return
                state['paused'] = False
        else:
            state = {'schema_version': 1, 'created_utc': now(), 'model': 'gpt-6-luna', 'reasoning_effort': 'medium',
                     'time_limits_seconds': {'lean':7200,'rocq':7200,'compcert':14400}, 'max_resumes':9, 'max_rounds':10, 'concurrency': 1,
                     'jobs': make_jobs(selection()[0], VARIANTS if prompt_variant == 'both' else (prompt_variant,))}
        state['prompt_variant'] = prompt_variant
        for job in state['jobs']:
            job.setdefault('prompt_variant', prompt_variant)
        # A restarted controller must preserve, rather than silently repeat, interrupted attempts.
        interrupted = [j for j in state['jobs'] if j['status'] == 'running']
        for job in interrupted:
            job['status'] = 'interrupted-needs-review'
        def save(phase):
            state.update(worker_pid=os.getpid(), updated_utc=now(), phase=phase)
            counts = {}
            for job in state['jobs']:
                counts[job['status']] = counts.get(job['status'], 0)+1
            state['counts'] = counts
            state['ready_instances'] = sum(j['status'] == 'pending-package' and (PACKAGES/j['task_id']/j['platform']/'registry.json').exists() for j in state['jobs'])
            state['unprepared_instances'] = counts.get('pending-package', 0)-state['ready_instances']
            reports = [json.loads(Path(p).read_text()) for j in state['jobs'] for p in j.get('reports', [])]
            state['totals'] = {'attempts_with_reports': len(reports),
                'agent_seconds': sum(r['resources'].get('agent_wall_seconds') or 0 for r in reports),
                'checker_seconds': sum(r['resources'].get('checker_wall_seconds') or 0 for r in reports),
                'sum_attempt_wall_seconds': sum(r['resources'].get('total_wall_seconds') or 0 for r in reports),
                'reported_tokens': {k: sum((r['resources'].get('tokens') or {}).get(k, 0) for r in reports)
                                    for k in ('input_tokens', 'cached_input_tokens', 'output_tokens')},
                'attempts_missing_usage': sum(r['resources'].get('tokens') is None for r in reports),
                'max_agent_cgroup_memory_peak_bytes': max([((r['resources'].get('sandbox') or {}).get('memory_peak_bytes') or 0) if not r['resources'].get('agent_max_cgroup_memory_peak_bytes') else r['resources']['agent_max_cgroup_memory_peak_bytes'] for r in reports], default=0) or None,
                'monetary_cost': None, 'hosted_inference_memory_bytes': None}
            state['by_prompt_variant'] = {}
            for variant in VARIANTS:
                subset=[r for r in reports if r['configuration']['prompt_protocol']['variant']==variant]
                state['by_prompt_variant'][variant] = {
                    'attempts_with_reports':len(subset),
                    'accepted':sum(r['result']['status']=='accepted' for r in subset),
                    'reported_tokens':{k:sum((r['resources'].get('tokens') or {}).get(k,0) for r in subset)
                                       for k in ('input_tokens','cached_input_tokens','output_tokens')},
                    'attempts_missing_usage':sum(r['resources'].get('tokens') is None for r in subset),
                    'sum_attempt_wall_seconds':sum(r['resources'].get('total_wall_seconds') or 0 for r in subset),
                    'agent_seconds':sum(r['resources'].get('agent_wall_seconds') or 0 for r in subset),
                    'checker_seconds':sum(r['resources'].get('checker_wall_seconds') or 0 for r in subset),
                    'max_agent_cgroup_memory_peak_bytes':max([r['resources'].get('agent_max_cgroup_memory_peak_bytes') or 0 for r in subset],default=0) or None,
                    'max_checker_cgroup_memory_peak_bytes':max([r['resources'].get('checker_max_cgroup_memory_peak_bytes') or 0 for r in subset],default=0) or None,
                    'monetary_cost':None,'hosted_inference_memory_bytes':None}
            dump(state_file, state)
        if interrupted:
            save('blocked-interrupted-attempt'); return
        while True:
            ready = [j for j in state['jobs'] if j['status'] == 'pending-package' and
                     (PACKAGES/j['task_id']/j['platform']/'registry.json').is_file()]
            if not ready:
                if all(j['status'] not in ('pending-package', 'running') for j in state['jobs']):
                    save('finished'); return
                save('waiting-for-certified-packages'); time.sleep(30); continue
            job = ready[0]; job['status'] = 'running'
            save('running')
            def started(path):
                job['attempts'].append(str(path)); job['current_run'] = str(path); save('running')
            try:
                with (PACKAGES/'activity.lock').open('a') as activity:
                    fcntl.flock(activity, fcntl.LOCK_EX)
                    directory, report = run(job['task_id'], job['platform'], timeout=state.get('time_limits_seconds',{'lean':7200,'rocq':7200,'compcert':14400})[job['platform']], max_resumes=state.get('max_resumes',9), on_run=started, prompt_variant=job['prompt_variant'])
            except Exception as error:
                job['status'] = 'infrastructure-error'; job['detail'] = type(error).__name__+': '+str(error)
                save('blocked-infrastructure'); return
            job['status'] = report['result']['status']
            job.setdefault('reports', []).append(str(directory/'report.json'))
            job.pop('current_run', None)
            with (base/'history.jsonl').open('a') as history:
                history.write(json.dumps({'ended_utc': now(), 'task_id': job['task_id'], 'platform': job['platform'],
                                          'prompt_variant':job['prompt_variant'], 'result': report['result'], 'report': str(directory/'report.json')})+'\n')
                history.flush(); os.fsync(history.fileno())
            if job['status'] == 'infrastructure-error':
                save('blocked-infrastructure'); return
            save('between-jobs')


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument("--resume",action="store_true",help="Explicitly resume a user-paused batch")
    parser.add_argument('--prompt-variant', choices=(*VARIANTS,'both'), default='verification')
    args=parser.parse_args()
    main(resume=args.resume, prompt_variant=args.prompt_variant)
