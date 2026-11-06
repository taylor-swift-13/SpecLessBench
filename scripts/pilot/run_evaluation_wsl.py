"""Run one isolated evaluation pair; the agent selects a checked claim branch."""
import argparse
import datetime as dt
import json
import os
import resource as process_resource
import shutil
import subprocess
import threading
import time
import uuid
from pathlib import Path

from grade_sealed import grade
from evaluation_prompts import VARIANTS, build_prompt
from audit_evaluation_costs import session_tokens
from prepare_evaluation import PACKAGES, ROCQ, COMPCERT, compile_lean, compile_rocq
from rocq_grader_core import COMPCERT_ROCQ_ASSUMPTIONS
from run_codex_wsl import AUTH, CODEX, CODE_HOST, LEAN, ROOT, SUPERVISOR, fingerprint_tree, now, sha
from selection import selection
from single_task_runner import tree_digest

BASE = Path.home()/'.local/share/speclessbench/runs/evaluation'
def dump(path, value):
    tmp = path.with_name(path.name+'.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')
    tmp.replace(path)


def literal_list(value):
    return (type(value) is list and len(value) <= 8192 and
            all(type(x) is int and -(2**63) <= x < 2**63 for x in value))


def render_claim(value, platform='lean'):
    if platform not in ('lean', 'rocq', 'compcert'):
        raise ValueError('No certified literal renderer for this platform')
    if type(value) is not dict:
        raise ValueError('Claim must be an object')
    if value == {'claim': 'equivalence'}:
        return 'Task.equivalent'
    if set(value) != {'claim', 'input', 'left', 'right'} or value['claim'] != 'counterexample':
        raise ValueError('Choose exactly one literal branch')
    if not all(literal_list(value[k]) for k in ('input', 'left', 'right')):
        raise ValueError('Expected bounded literal integer lists')
    if value['left'] == value['right']:
        raise ValueError('Counterexample observations must differ')
    def term(values):
        if platform != 'lean':
            return '['+'; '.join('('+str(x)+')%Z' for x in values)+']'
        return '['+', '.join(str(x) if x >= 0 else '('+str(x)+')' for x in values)+']'
    if platform == 'compcert':
        observations = ['(0%Z, ('+term(value[k])+' ++ repeat 0%Z '+str(8192-len(value[k]))+'%nat))' for k in ('left', 'right')]
        return 'Task.refutationAt '+term(value['input'])+' '+' '.join(observations)
    return 'Task.refutationAt '+' '.join(term(value[k]) for k in ('input', 'left', 'right'))


def report_markdown(report):
    c=report['configuration'];v=report['resources']
    return ('# Evaluation report\n\n'
        +f"- Task: `{c['task_id']}` / {c['platform']}\n"
        +f"- Prompt: {c['prompt_protocol']['variant']} / {c['prompt_protocol']['revision']}\n"
        +f"- Prompt SHA-256: {c['prompt_protocol']['initial_prompt_sha256']}\n"
        +f"- Goal mode: {c.get('goal_mode', 'not configured')}\n"
        +f"- Native turns: {(report.get('native_goal_session') or {}).get('native_turn_count')}\n"
        +f"- Model: `{c['model']}`, {c['model_reasoning_effort']}\n"
        +f"- Result: **{report['result']['status']}**\n"
        +f"- Policy: {c.get('policy',report.get('execution_policy','legacy-one-shot'))}\n"
        +f"- Session: {report.get('session_id')}\n"
        +'- Manual resumes: 0\n'
        +f"- Stop: {report.get('stop_reason')}\n"
        +f"- Configured limit seconds: {c.get('total_budget_seconds',c.get('agent_timeout_seconds'))}\n"
        +f"- Agent / checker seconds: {v.get('agent_wall_seconds')} / {v.get('checker_wall_seconds')}\n"
        +f"- Tokens: {v.get('tokens')}\n"
        +f"- Agent cgroup peak bytes: {v.get('agent_max_cgroup_memory_peak_bytes')}\n"
        +'- Billing / hosted-model memory: unavailable\n')


def run(task_id, platform='compcert', timeout=None, on_run=None, prompt_variant='baseline', goal_mode='off'):
    timeout = timeout if timeout is not None else (14400 if platform == 'compcert' else 7200)
    if timeout <= 0:
        raise ValueError('Invalid time limit')
    if goal_mode not in ('on','off') or platform != 'compcert':
        raise ValueError('Native Goal probe currently supports CompCert only')
    os.umask(0o077)
    if task_id not in {r['pilot_id'] for r in selection()[0]}:
        raise ValueError('Task is not evaluation-eligible')
    if platform not in ('lean', 'rocq', 'compcert'):
        raise ValueError('No certified adapter for this platform yet')
    toolchain = {'lean': LEAN, 'rocq': ROCQ, 'compcert': COMPCERT}[platform]
    proof_name = 'Submission.lean' if platform == 'lean' else 'Submission.v'
    prompt, prompt_protocol, prompt_components = build_prompt(platform, prompt_variant, timeout)
    source = PACKAGES/task_id/platform
    meta = json.loads((source/'registry.json').read_text())
    if (meta['pilot_id'], meta['platform']) != (task_id, platform) or tree_digest(source/'task') != meta['public_sha256']:
        raise ValueError('Trusted package mismatch')
    if not AUTH.is_file() or not CODEX.is_file() or not CODE_HOST.is_file():
        raise RuntimeError('Codex authentication/executables unavailable')
    condition = 'goal-'+goal_mode
    parent = BASE/task_id/platform/condition/'attempts'
    parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    run_dir = parent/(dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:12])
    run_dir.mkdir(mode=0o700)
    if on_run:
        on_run(run_dir)
    private = run_dir/'private'; home = private/'home'; work = private/'work'; task = private/'task'
    for folder in (home, work):
        folder.mkdir(parents=True, mode=0o700)
    shutil.copytree(source/'task', task)
    dump(run_dir/'package.json', meta)
    started = now(); clock = time.monotonic(); trace = []; resources = None; usage = []
    result = {'status': 'infrastructure-error', 'detail': 'Run did not reach finalization'}
    claim = None
    cfg = {'purpose': 'evaluation', 'task_id': task_id, 'platform': platform,
           'model': 'gpt-6-luna', 'model_reasoning_effort': 'medium',
           'agent_timeout_seconds': timeout, 'total_budget_seconds': timeout,
           'budget_scope': 'Shared wall time across all agent rounds and checking',
           'policy': 'native-goal' if goal_mode=='on' else 'single-turn', 'goal_mode':goal_mode,
           'transport':'app-server', 'manual_resumes':False,
           'checker_stage_timeout_seconds': 600,
           'memory_limit_bytes': 3*1024**3, 'pids_limit': 512,
           'agent_version': subprocess.check_output([str(CODEX), '--version'], text=True).strip(),
           'task_package_sha256': meta['public_sha256'], 'tools_network': False,
           'model_network': True, 'provider': 'ChatGPT account',
           'runner_sha256': sha(Path(__file__).read_bytes()),
           'codex_executable_sha256': sha(CODEX.read_bytes()),
           'codex_code_host_sha256': sha(CODE_HOST.read_bytes()),
           'toolchain_version': subprocess.check_output([str(toolchain/('bin/lean' if platform == 'lean' else 'bin/coqc')), '--version'], text=True).strip(),
           'prompt_sha256': sha(prompt.encode()), 'prompt_protocol': prompt_protocol}
    cfg['native_driver_sha256'] = sha((ROOT/'scripts/pilot/goal_client.py').read_bytes())
    dump(run_dir/'config.json', cfg)
    config = '''default_permissions = "eval"
approval_policy = "never"
model = "gpt-6-luna"
model_reasoning_effort = "medium"
web_search = "disabled"
[features]
apps = false
memories = false
[permissions.eval]
extends = ":workspace"
[permissions.eval.filesystem]
"/home/runner/.codex/auth.json" = "deny"
[permissions.eval.network]
enabled = false
'''
    (home/'auth.json').touch(mode=0o600)
    (home/'config.toml').write_text(config); (run_dir/'codex-config.toml').write_text(config)
    (run_dir/'prompt.txt').write_text(prompt)
    dump(run_dir/'prompt-components.json', prompt_components)
    unit = 'specless-eval-'+uuid.uuid4().hex+'.scope'
    agent_seconds = None; agent_clock = None; checker_seconds = None; complete = False; invalid = 0; event_count = 0
    cgroup = None; session_id = None; round_index = 0; rounds = []; budget_clock = None
    agent_total = 0.0; checker_total = 0.0; stop_reason = None; native_summary = None
    try:
        preflight = time.monotonic()
        catalog = subprocess.run([str(CODEX), 'debug', 'models'], capture_output=True, timeout=60)
        data = json.loads(catalog.stdout); models = data.get('models', []) if isinstance(data, dict) else data
        selected = [m for m in models if m.get('slug') == cfg['model']]
        dump(run_dir/'model-catalog.json', {'captured_utc': now(), 'exit_code': catalog.returncode,
             'raw_catalog_sha256': sha(catalog.stdout), 'selected_models': selected,
             'scope': 'CLI catalog observation; not independent server response attestation'})
        if catalog.returncode or len(selected) != 1 or not any(x.get('effort') == 'medium' for x in selected[0].get('supported_reasoning_levels', [])):
            raise RuntimeError('Luna medium absent from CLI catalog')
        dump(run_dir/'environment.json', {'benchmark_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
             'git_status': subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).splitlines(),
             'toolchain_tree': fingerprint_tree(toolchain), 'preflight_seconds': time.monotonic()-preflight,
             'runner_dependencies': {p: sha((ROOT/p).read_bytes()) for p in (
                 'scripts/pilot/run_evaluation_wsl.py', 'scripts/pilot/prepare_evaluation.py', 'scripts/pilot/prepare_clight_evaluation.py', 'scripts/pilot/prepare_classics_evaluation.py',
                 'scripts/pilot/grade_sealed.py', 'scripts/pilot/lean_grader_core.py',
                 'scripts/pilot/TrustedLeanAudit.lean', 'scripts/pilot/rocq_grader_core.py',
                 'scripts/pilot/sandbox.py', 'scripts/pilot/resource_supervisor.py')},
             'full_environment_locked': False})
        cmd = ['/usr/bin/bwrap', '--unshare-all', '--share-net', '--die-with-parent', '--new-session',
               '--ro-bind', '/usr', '/usr', '--ro-bind', '/lib', '/lib', '--ro-bind', '/lib64', '/lib64', '--symlink', 'usr/bin', '/bin',
               '--dir', '/etc']
        for path in ('/etc/resolv.conf', '/etc/hosts', '/etc/nsswitch.conf', '/etc/ssl'):
            cmd += ['--ro-bind', path, path]
        cmd += ['--dir', '/home', '--dir', '/home/runner', '--bind', str(home), '/home/runner/.codex',
                '--ro-bind', str(AUTH), '/home/runner/.codex/auth.json', '--dir', '/opt',
                '--ro-bind', str(CODEX), '/opt/codex', '--ro-bind', str(CODE_HOST), '/opt/codex-code-mode-host',
                '--symlink', 'codex', '/opt/codex-linux-sandbox']
        if platform == 'lean':
            cmd += ['--ro-bind', str(LEAN), '/opt/lean']
        else:
            cmd += ['--dir', '/home/yangfp', '--dir', '/home/yangfp/.opam', '--ro-bind', str(toolchain), str(toolchain)]
        cmd += [
                '--ro-bind', str(task), '/task', '--bind', str(work), '/work', '--tmpfs', '/tmp', '--dev', '/dev', '--proc', '/proc',
                '--clearenv', '--setenv', 'HOME', '/home/runner', '--setenv', 'CODEX_HOME', '/home/runner/.codex',
                '--setenv', 'PATH', '/opt:'+('/opt/lean/bin' if platform == 'lean' else str(toolchain/'bin'))+':/usr/bin:/bin',
                '--setenv', 'LANG', 'C.UTF-8', '--setenv', 'TOKIO_WORKER_THREADS', '4', '--setenv', 'RAYON_NUM_THREADS', '4']
        if platform == 'lean':
            cmd += ['--setenv', 'LEAN_PATH', '/task:/work']
        else:
            cmd += ['--setenv', 'OCAMLFIND_CONF', str(toolchain/'lib/findlib.conf'), '--setenv', 'OCAMLPATH', str(toolchain/'lib')]
        for key in ('HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY', 'http_proxy', 'https_proxy', 'no_proxy'):
            if os.environ.get(key):
                from urllib.parse import urlsplit
                parsed = urlsplit(os.environ[key])
                if parsed.username or parsed.password:
                    raise RuntimeError('Credential-bearing proxy is unsupported')
                cmd += ['--setenv', key, os.environ[key]]
        cmd += ['--ro-bind',str(ROOT/'scripts/pilot/goal_client.py'),'/opt/goal_client.py',
                '--ro-bind',str(run_dir/'prompt.txt'),'/opt/prompt.txt']
        sandbox_prefix = cmd + ['--chdir','/work','--','/usr/bin/python3','/opt/goal_client.py',
                                '--goal-mode',goal_mode,'--prompt','/opt/prompt.txt']
        budget_clock = time.monotonic()
        feedback = prompt
        remaining = timeout-(time.monotonic()-budget_clock)
        if remaining <= 0:
            raise TimeoutError('Shared attempt time budget reached')
        complete = False; resources = None; cgroup = None; trace = []; checker_seconds = 0.0
        cmd = sandbox_prefix
        unit = 'specless-eval-'+uuid.uuid4().hex+'.scope'
        session_mismatch = False
        claim = None; agent_seconds = None
        (private/'resources.json').unlink(missing_ok=True)
        round_dir = run_dir/'rounds'/f'{round_index:03d}'
        round_dir.mkdir(parents=True, mode=0o700)
        (round_dir/'prompt.txt').write_text(feedback)
        round_prompt_sha256 = sha(feedback.encode())
        event_start = event_count; usage_start = len(usage); round_started = now()
        stderr_start = (run_dir/'agent.stderr').stat().st_size if (run_dir/'agent.stderr').exists() else 0
        dump(private/'supervisor.json', {'argv': cmd, 'timeout': remaining, 'memory_limit': 3*1024**3,
             'pids_limit': 512, 'report': str(private/'resources.json')})
        shutil.copyfile(private/'supervisor.json', round_dir/'supervisor.json')
        launch = ['/usr/bin/systemd-run', '--user', '--scope', '--quiet', '--unit', unit, '-p', 'MemoryMax=3221225472',
                  '-p', 'MemorySwapMax=0', '-p', 'TasksMax=512', '/usr/bin/python3', str(SUPERVISOR), str(private/'supervisor.json')]
        agent_clock = time.monotonic()
        with (run_dir/'events.jsonl').open('ab') as out, (run_dir/'events.timestamps.jsonl').open('a') as stamps, (run_dir/'agent.stderr').open('ab') as err:
            proc = subprocess.Popen(launch, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=err, start_new_session=True)
            def capture():
                nonlocal event_count, invalid, complete, session_id, session_mismatch, native_summary
                for line in proc.stdout:
                    out.write(line); out.flush(); event_count += 1
                    stamps.write(json.dumps({'line': event_count, 'round': round_index, 'received_utc': now()})+'\n'); stamps.flush()
                    try:
                        event = json.loads(line)
                        if event.get('type') == 'thread.started':
                            observed_id = event['thread_id']
                            if session_id is not None and observed_id != session_id:
                                invalid += 1
                                session_mismatch = True
                                complete = False
                                continue
                            session_id = observed_id
                        if event.get('type') == 'turn.completed':
                            complete = True
                            if event.get('usage'):
                                usage.append(event['usage'])
                        if event.get('type') == 'native.run.completed':
                            native_summary = event['summary']
                        if event.get('usage') and event.get('type') == 'native.usage':
                            usage.append(event['usage'])
                    except (ValueError, AttributeError):
                        invalid += 1
            reader = threading.Thread(target=capture, daemon=True); reader.start()
            while proc.poll() is None:
                if cgroup is None:
                    observed = subprocess.run(['systemctl', '--user', 'show', unit, '-p', 'ControlGroup', '--value'], capture_output=True, text=True, timeout=10)
                    if observed.returncode == 0 and observed.stdout.strip():
                        cgroup = Path('/sys/fs/cgroup')/observed.stdout.strip().lstrip('/')
                memory = {}
                if cgroup is not None:
                    for key, filename in (('memory_current_bytes', 'memory.current'), ('memory_peak_bytes', 'memory.peak')):
                        try:
                            memory[key] = int((cgroup/filename).read_text())
                        except OSError:
                            pass
                dump(run_dir/'live.json', {'phase': 'agent', 'updated_utc': now(), 'agent_seconds': time.monotonic()-agent_clock,
                     'session_id': session_id, 'round': round_index, 'remaining_seconds': max(0,timeout-(time.monotonic()-budget_clock)), 'cumulative_agent_seconds': agent_total+time.monotonic()-agent_clock, 'events': event_count, 'event_bytes': out.tell(), 'usage_events': usage, **memory})
                if time.monotonic()-agent_clock > remaining+10 or shutil.disk_usage(run_dir).free < 512*1024**2:
                    subprocess.run(['systemctl', '--user', 'stop', unit], capture_output=True, timeout=15)
                    proc.kill(); proc.wait(); break
                time.sleep(5)
            reader.join(timeout=15)
            if reader.is_alive():
                raise RuntimeError('Agent event stream did not close')
        if session_mismatch: raise RuntimeError('Resume returned a different session ID')
        agent_seconds = time.monotonic()-agent_clock
        if (private/'resources.json').exists():
            resources = json.loads((private/'resources.json').read_text())
        for name in (proof_name, 'claim.json'):
            (run_dir/name).unlink(missing_ok=True)
            candidate = work/name
            if candidate.is_file() and not candidate.is_symlink() and candidate.stat().st_size <= 1024*1024:
                shutil.copyfile(candidate, run_dir/name)
        dump(run_dir/'live.json', {'phase': 'checker', 'round': round_index, 'session_id':session_id, 'updated_utc': now(), 'agent_seconds': agent_seconds, 'events': event_count})
        if not resources or resources.get('status') == 'limits-not-enforced':
            raise RuntimeError('Cgroup supervision failed')
        if resources['status'] == 'timeout':
            result = {'status': 'timeout', 'detail': 'Shared attempt time budget reached'}
        elif resources.get('status') != 'exited' or resources.get('exit_code') != 0 or not complete:
            result = {'status': 'agent-error', 'detail': 'Agent did not complete successfully'}
        elif not (run_dir/'claim.json').is_file() or not (run_dir/proof_name).is_file():
            result = {'status': 'rejected', 'detail': 'Missing claim or proof'}
        else:
            check_clock = time.monotonic(); checker_seconds = None
            try:
                claim = json.loads((run_dir/'claim.json').read_text()); goal = render_claim(claim, platform)
            except (ValueError, UnicodeDecodeError) as error:
                result = {'status': 'rejected', 'detail': str(error)}
            else:
                trusted = private/('grading-'+str(round_index)); shutil.copytree(task, trusted)
                if platform == 'lean':
                    (trusted/'Obligation.lean').write_text('import Task\nnamespace Obligation\ndef goal : Prop := '+goal+'\nend Obligation\n')
                    compile_lean(trusted, 'Obligation', [trusted], timeout=max(1,min(180,timeout-(time.monotonic()-budget_clock))))
                else:
                    (trusted/'Obligation.v').write_text('From '+('Stdlib' if platform == 'compcert' else 'Coq')+' Require Import ZArith List.\nImport ListNotations.\nFrom Trusted Require Import Task.\nDefinition goal : Prop := '+goal+'.\n')
                    compile_rocq(trusted, 'Obligation', [(trusted, 'Trusted')], toolchain=toolchain, timeout=max(1,min(180,timeout-(time.monotonic()-budget_clock))))
                obligation = 'Obligation.lean' if platform == 'lean' else 'Obligation.v'
                shutil.copyfile(trusted/obligation, run_dir/obligation)
                result = grade(platform, trusted, tree_digest(trusted), run_dir/proof_name, timeout=max(1,min(600,int((timeout-(time.monotonic()-budget_clock))/(3 if platform == 'lean' else 4)))), trace=trace)
            checker_seconds = time.monotonic()-check_clock
        agent_total += agent_seconds or 0
        checker_total += checker_seconds or 0
        dump(round_dir/'checker.log', trace)
        for name in (proof_name, 'claim.json', 'Obligation.lean', 'Obligation.v'):
            f = run_dir/name
            if f.is_file(): shutil.copyfile(f, round_dir/name)
        record = {'round': round_index, 'session_id': session_id, 'result': result,
                  'started_utc': round_started, 'ended_utc': now(), 'configuration': cfg, 'round_prompt_sha256': round_prompt_sha256,
                  'provider_usage_events': usage[usage_start:],
                  'stderr_byte_start': stderr_start, 'stderr_byte_end': (run_dir/'agent.stderr').stat().st_size,
                  'started_event': event_start+1, 'ended_event': event_count,
                  'agent_seconds': agent_seconds, 'checker_seconds': checker_seconds,
                  'sandbox': resources, 'claim': claim, 'checker_max_cgroup_memory_peak_bytes': max([((t.get('resources') or {}).get('memory_peak_bytes') or 0) for t in trace],default=0)}
        dump(round_dir/'report.json', record); rounds.append(record)
        (round_dir/'SHA256SUMS').write_text(''.join(sha(f.read_bytes())+'  '+f.name+'\n' for f in sorted(round_dir.iterdir()) if f.is_file()))
        dump(run_dir/'rounds.json', rounds)
        subprocess.run(['systemctl', '--user', 'stop', unit], capture_output=True, timeout=20)
        if result['status'] == 'timeout':
            stop_reason = 'time-budget'
        elif native_summary is None:
            result = {'status':'infrastructure-error','detail':'Native client did not report a final lifecycle state'}
            stop_reason = 'native-client-error'
        else:
            stop_reason = 'accepted' if result['status']=='accepted' else native_summary['stop_reason']
        agent_seconds = agent_total; checker_seconds = checker_total
    except (Exception, KeyboardInterrupt) as error:
        result = {'status': 'timeout' if budget_clock is not None and time.monotonic()-budget_clock >= timeout else 'infrastructure-error', 'detail': type(error).__name__+': '+str(error)}
    finally:
        if resources is None and (private/'resources.json').exists():
            resources = json.loads((private/'resources.json').read_text())
        if resources is None and cgroup is not None:
            try:
                resources = {'status': 'interrupted-observation', 'memory_peak_bytes': int((cgroup/'memory.peak').read_text()),
                             'observed_utc': now(), 'memory_scope': 'Agent cgroup observed before interrupted-run cleanup; not hosted model memory'}
            except OSError:
                pass
        subprocess.run(['systemctl', '--user', 'stop', unit], capture_output=True, timeout=20)
        if budget_clock is not None and len(rounds) <= round_index and 'round_dir' in locals():
            current_agent = agent_seconds if agent_seconds is not None else (time.monotonic()-agent_clock if agent_clock else 0)
            current_checker = time.monotonic()-check_clock if 'check_clock' in locals() and checker_seconds is None else (checker_seconds or 0)
            for name in (proof_name,'claim.json'):
                f=work/name
                if f.is_file() and not f.is_symlink() and f.stat().st_size<=1024*1024: shutil.copyfile(f,round_dir/name)
            record={'round':round_index,'configuration':cfg,'round_prompt_sha256':round_prompt_sha256,'provider_usage_events':usage[usage_start:],'started_utc':round_started,'ended_utc':now(),'session_id':session_id,'result':result,'started_event':event_start+1,'ended_event':event_count,'agent_seconds':current_agent,'checker_seconds':current_checker,'sandbox':resources,'claim':claim}
            dump(round_dir/'report.json',record);dump(round_dir/'checker.log',trace);rounds.append(record)
            (round_dir/'SHA256SUMS').write_text(''.join(sha(f.read_bytes())+'  '+f.name+'\n' for f in sorted(round_dir.iterdir()) if f.is_file() and f.name!='SHA256SUMS'))
        if rounds:
            agent_seconds=sum(r.get('agent_seconds') or 0 for r in rounds)
            checker_seconds=sum(r.get('checker_seconds') or 0 for r in rounds)
        dump(run_dir/'rounds.json',rounds)
        (home/'auth.json').unlink(missing_ok=True)
        dump(run_dir/'checker.log', trace)
        costs = {'agent_wall_seconds': agent_seconds, 'checker_wall_seconds': checker_seconds,
                 'total_wall_seconds': time.monotonic()-clock, 'sandbox': resources, 'rounds': rounds, 'stop_reason': stop_reason,
                 'session_id': session_id,
                 'agent_max_cgroup_memory_peak_bytes': max([((r.get('sandbox') or {}).get('memory_peak_bytes') or 0) for r in rounds]+[((resources or {}).get('memory_peak_bytes') or 0)]) or None,
                 'checker_max_cgroup_memory_peak_bytes': max([((row.get('resources') or {}).get('memory_peak_bytes') or 0) for row in trace]+[v for r in rounds for v in [r.get('checker_max_cgroup_memory_peak_bytes') or 0]], default=0) or None,
                 'controller_peak_rss_bytes_linux': process_resource.getrusage(process_resource.RUSAGE_SELF).ru_maxrss*1024,
                 'obligation_compiler_costs': [json.loads(line) for line in (private/'compile-costs.jsonl').read_text().splitlines()] if (private/'compile-costs.jsonl').exists() else [],
                 'provider_usage_events': usage,
                 'tokens': session_tokens(usage),
                 'token_accounting': 'last-session-cumulative-event',
                 'monetary_cost': None, 'hosted_inference_memory_bytes': None}
        dump(run_dir/'resources.json', costs)
        report = {'schema_version': 2, 'started_utc': started, 'ended_utc': now(), 'configuration': cfg,
                  'result': result, 'resources': costs, 'submission_claim': claim,
                  'session_id': session_id, 'resume_count': round_index, 'stop_reason': stop_reason,
                  'native_goal_session':native_summary,
                  'checks': {'fixed_goal_gate': 'passed' if len(trace) > 1 and trace[1].get('exit_code') == 0 else 'not-passed-or-not-run',
                             'axiom_audit': 'passed' if len(trace) == (3 if platform == 'lean' else 4) and trace[-1].get('exit_code') == 0 else 'not-passed-or-not-run',
                             'independent_coqchk': ('passed' if len(trace) > 2 and trace[2].get('exit_code') == 0 else 'not-passed-or-not-run') if platform != 'lean' else None,
                             'allowed_axioms': ['propext', 'Classical.choice', 'Quot.sound'] if platform == 'lean' else (['compcert.*', *sorted(COMPCERT_ROCQ_ASSUMPTIONS)] if platform == 'compcert' else []),
                             'full_stage_output': 'checker.log'},
                  'proof_sha256': sha((run_dir/proof_name).read_bytes()) if (run_dir/proof_name).exists() else None,
                  'transcript': {'format': 'Codex app-server JSON-RPC with normalized observations', 'event_count': event_count, 'invalid_lines': invalid,
                                 'turn_completed': complete, 'events_flushed_live': True,
                                 'limitations': 'All CLI-emitted events are retained; hidden reasoning, tool output omitted by the CLI, and server-side resolved model metadata are not independently available.'}}
        dump(run_dir/'report.json', report)
        (run_dir/'report.md').write_text(report_markdown(report))
        dump(run_dir/'live.json', {'phase': 'finished', 'updated_utc': now(), 'result': result})
        files = sorted(p for p in run_dir.iterdir() if p.is_file() and p.name != 'SHA256SUMS')
        (run_dir/'SHA256SUMS').write_text(''.join(sha(p.read_bytes())+'  '+p.name+'\n' for p in files))
    return run_dir, report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', required=True)
    parser.add_argument('--platform', choices=('lean', 'rocq', 'compcert'), default='compcert')
    parser.add_argument('--timeout', type=int)
    parser.add_argument('--goal-mode', choices=('on','off'), required=True)
    parser.add_argument('--prompt-variant', choices=VARIANTS, default='baseline')
    args = parser.parse_args()
    directory, report = run(args.task, args.platform, timeout=args.timeout, prompt_variant=args.prompt_variant, goal_mode=args.goal_mode)
    print(json.dumps({'run_dir': str(directory), 'result': report['result']}))
