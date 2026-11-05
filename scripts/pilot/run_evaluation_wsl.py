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
from prepare_evaluation import PACKAGES, ROCQ, compile_lean, compile_rocq
from run_codex_wsl import AUTH, CODEX, CODE_HOST, LEAN, ROOT, SUPERVISOR, fingerprint_tree, now, sha
from selection import selection
from single_task_runner import tree_digest

BASE = Path.home()/'.local/share/speclessbench/runs/evaluation'
PROMPT = '''Determine whether the two fixed implementations in /task/Task.lean agree
on every Task.valid input. You have one implementation pair only. Work in /work.
Choose exactly one branch and write /work/claim.json:
  {"claim":"equivalence"}
or {"claim":"counterexample","input":[...],"left":[...],"right":[...]}
All arrays must be literal integer lists. The observations left/right are the
complete Words returned inside some, INCLUDING the leading payload length.
No witness is supplied. For equivalence create Submission.lean importing Task,
with Submission.solve : Task.equivalent. For a counterexample use
Submission.solve : Task.refutationAt <input literal> <left literal> <right literal>.
The checker independently renders the selected obligation and checks your proof
against it. A bare disjunction, conditional proof, unverified test, or mere claim
is insufficient. Helper definitions/lemmas in Submission.lean are allowed.
Do not modify implementations, domain or targets. No sorry or new axioms.
Lean is on PATH; LEAN_PATH=/task:/work. Test your Submission.lean before finishing.
'''
ROCQ_PROMPT = '''Determine whether the fixed implementations in /task/Task.v agree
on every Task.valid input. Work only in /work. Choose exactly one branch and write
/work/claim.json as {"claim":"equivalence"} or
{"claim":"counterexample","input":[...],"left":[...],"right":[...]}.
The arrays are literal integers; left/right include the leading payload length
returned inside Some. No expected branch or witness is supplied.
Write /work/Submission.v, starting with:
From Coq Require Import ZArith List.
From Trusted Require Import Task.
Import ListNotations.
Define the TOP-LEVEL theorem solve : Task.equivalent, or for a literal counterexample
solve : Task.refutationAt <input> <left> <right>. The file itself is the
Submission library: do not wrap it in a Module Submission. You may import
Coq ZArith/List and ListNotations for integer lists. Add helper lemmas if needed.
The checker independently renders the selected goal and checks solve and its
assumptions. No Admitted, admit, new axioms, bare disjunction, conditional proof,
or mere test results. Keep implementations, domain and observations unchanged.
Check using: coqc -Q /task Trusted -Q /work Candidate /work/Submission.v
Both claim.json and Submission.v are required even when claiming equivalence.
'''


def dump(path, value):
    tmp = path.with_name(path.name+'.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')
    tmp.replace(path)


def literal_list(value):
    return (type(value) is list and len(value) <= 8192 and
            all(type(x) is int and -(2**63) <= x < 2**63 for x in value))


def render_claim(value, platform='lean'):
    if platform not in ('lean', 'rocq'):
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
        if platform == 'rocq':
            return '['+'; '.join('('+str(x)+')%Z' for x in values)+']'
        return '['+', '.join(str(x) if x >= 0 else '('+str(x)+')' for x in values)+']'
    return 'Task.refutationAt '+' '.join(term(value[k]) for k in ('input', 'left', 'right'))


def run(task_id, platform='lean', timeout=3600, on_run=None):
    os.umask(0o077)
    if task_id not in {r['pilot_id'] for r in selection()[0]}:
        raise ValueError('Task is not evaluation-eligible')
    if platform not in ('lean', 'rocq'):
        raise ValueError('No certified adapter for this platform yet')
    toolchain = LEAN if platform == 'lean' else ROCQ
    proof_name = 'Submission.lean' if platform == 'lean' else 'Submission.v'
    prompt = PROMPT if platform == 'lean' else ROCQ_PROMPT
    source = PACKAGES/task_id/platform
    meta = json.loads((source/'registry.json').read_text())
    if (meta['pilot_id'], meta['platform']) != (task_id, platform) or tree_digest(source/'task') != meta['public_sha256']:
        raise ValueError('Trusted package mismatch')
    if not AUTH.is_file() or not CODEX.is_file() or not CODE_HOST.is_file():
        raise RuntimeError('Codex authentication/executables unavailable')
    parent = BASE/task_id/platform/'attempts'
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
           'agent_timeout_seconds': timeout, 'checker_stage_timeout_seconds': 600,
           'memory_limit_bytes': 3*1024**3, 'pids_limit': 512,
           'agent_version': subprocess.check_output([str(CODEX), '--version'], text=True).strip(),
           'task_package_sha256': meta['public_sha256'], 'tools_network': False,
           'model_network': True, 'provider': 'ChatGPT account',
           'runner_sha256': sha(Path(__file__).read_bytes()),
           'codex_executable_sha256': sha(CODEX.read_bytes()),
           'codex_code_host_sha256': sha(CODE_HOST.read_bytes()),
           'toolchain_version': subprocess.check_output([str(toolchain/('bin/lean' if platform == 'lean' else 'bin/coqc')), '--version'], text=True).strip(),
           'prompt_sha256': sha(prompt.encode())}
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
    unit = 'specless-eval-'+uuid.uuid4().hex+'.scope'
    agent_seconds = None; agent_clock = None; checker_seconds = None; complete = False; invalid = 0; event_count = 0
    cgroup = None
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
                 'scripts/pilot/run_evaluation_wsl.py', 'scripts/pilot/grade_sealed.py', 'scripts/pilot/lean_grader_core.py',
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
            cmd += ['--dir', '/home/yangfp', '--dir', '/home/yangfp/.opam', '--ro-bind', str(ROCQ), str(ROCQ)]
        cmd += [
                '--ro-bind', str(task), '/task', '--bind', str(work), '/work', '--tmpfs', '/tmp', '--dev', '/dev', '--proc', '/proc',
                '--clearenv', '--setenv', 'HOME', '/home/runner', '--setenv', 'CODEX_HOME', '/home/runner/.codex',
                '--setenv', 'PATH', '/opt:'+('/opt/lean/bin' if platform == 'lean' else str(ROCQ/'bin'))+':/usr/bin:/bin',
                '--setenv', 'LANG', 'C.UTF-8', '--setenv', 'TOKIO_WORKER_THREADS', '4', '--setenv', 'RAYON_NUM_THREADS', '4']
        if platform == 'lean':
            cmd += ['--setenv', 'LEAN_PATH', '/task:/work']
        else:
            cmd += ['--setenv', 'OCAMLFIND_CONF', str(ROCQ/'lib/findlib.conf'), '--setenv', 'OCAMLPATH', str(ROCQ/'lib')]
        for key in ('HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY', 'http_proxy', 'https_proxy', 'no_proxy'):
            if os.environ.get(key):
                from urllib.parse import urlsplit
                parsed = urlsplit(os.environ[key])
                if parsed.username or parsed.password:
                    raise RuntimeError('Credential-bearing proxy is unsupported')
                cmd += ['--setenv', key, os.environ[key]]
        cmd += ['--chdir', '/work', '--', '/opt/codex', 'exec', '--ephemeral', '--skip-git-repo-check', '--json', '-C', '/work', prompt]
        dump(private/'supervisor.json', {'argv': cmd, 'timeout': timeout, 'memory_limit': 3*1024**3,
             'pids_limit': 512, 'report': str(private/'resources.json')})
        launch = ['/usr/bin/systemd-run', '--user', '--scope', '--quiet', '--unit', unit, '-p', 'MemoryMax=3221225472',
                  '-p', 'MemorySwapMax=0', '-p', 'TasksMax=512', '/usr/bin/python3', str(SUPERVISOR), str(private/'supervisor.json')]
        agent_clock = time.monotonic()
        with (run_dir/'events.jsonl').open('wb') as out, (run_dir/'events.timestamps.jsonl').open('w') as stamps, (run_dir/'agent.stderr').open('wb') as err:
            proc = subprocess.Popen(launch, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=err, start_new_session=True)
            def capture():
                nonlocal event_count, invalid, complete
                for line in proc.stdout:
                    out.write(line); out.flush(); event_count += 1
                    stamps.write(json.dumps({'line': event_count, 'received_utc': now()})+'\n'); stamps.flush()
                    try:
                        event = json.loads(line)
                        if event.get('type') == 'turn.completed':
                            complete = True
                            if event.get('usage'):
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
                     'events': event_count, 'event_bytes': out.tell(), 'usage_events': usage, **memory})
                if time.monotonic()-agent_clock > timeout+45 or shutil.disk_usage(run_dir).free < 512*1024**2:
                    subprocess.run(['systemctl', '--user', 'stop', unit], capture_output=True, timeout=15)
                    proc.kill(); proc.wait(); break
                time.sleep(5)
            reader.join(timeout=15)
            if reader.is_alive():
                raise RuntimeError('Agent event stream did not close')
        agent_seconds = time.monotonic()-agent_clock
        if (private/'resources.json').exists():
            resources = json.loads((private/'resources.json').read_text())
        for name in (proof_name, 'claim.json'):
            candidate = work/name
            if candidate.is_file() and not candidate.is_symlink() and candidate.stat().st_size <= 1024*1024:
                shutil.copyfile(candidate, run_dir/name)
        dump(run_dir/'live.json', {'phase': 'checker', 'updated_utc': now(), 'agent_seconds': agent_seconds, 'events': event_count})
        if not resources or resources.get('status') == 'limits-not-enforced':
            raise RuntimeError('Cgroup supervision failed')
        if resources['status'] == 'timeout':
            result = {'status': 'timeout', 'detail': 'One-hour agent limit reached'}
        elif resources.get('status') != 'exited' or resources.get('exit_code') != 0 or not complete:
            result = {'status': 'agent-error', 'detail': 'Agent did not complete successfully'}
        elif not (run_dir/'claim.json').is_file() or not (run_dir/proof_name).is_file():
            result = {'status': 'rejected', 'detail': 'Missing claim or proof'}
        else:
            check_clock = time.monotonic()
            try:
                claim = json.loads((run_dir/'claim.json').read_text()); goal = render_claim(claim, platform)
            except (ValueError, UnicodeDecodeError) as error:
                result = {'status': 'rejected', 'detail': str(error)}
            else:
                trusted = private/'grading'; shutil.copytree(task, trusted)
                if platform == 'lean':
                    (trusted/'Obligation.lean').write_text('import Task\nnamespace Obligation\ndef goal : Prop := '+goal+'\nend Obligation\n')
                    compile_lean(trusted, 'Obligation', [trusted])
                else:
                    (trusted/'Obligation.v').write_text('From Coq Require Import ZArith List.\nImport ListNotations.\nFrom Trusted Require Import Task.\nDefinition goal : Prop := '+goal+'.\n')
                    compile_rocq(trusted, 'Obligation', [(trusted, 'Trusted')])
                obligation = 'Obligation.lean' if platform == 'lean' else 'Obligation.v'
                shutil.copyfile(trusted/obligation, run_dir/obligation)
                result = grade(platform, trusted, tree_digest(trusted), run_dir/proof_name, timeout=600, trace=trace)
            checker_seconds = time.monotonic()-check_clock
    except (Exception, KeyboardInterrupt) as error:
        result = {'status': 'infrastructure-error', 'detail': type(error).__name__+': '+str(error)}
    finally:
        if agent_clock is not None and agent_seconds is None:
            agent_seconds = time.monotonic()-agent_clock
        if resources is None and (private/'resources.json').exists():
            resources = json.loads((private/'resources.json').read_text())
        if resources is None and cgroup is not None:
            try:
                resources = {'status': 'interrupted-observation', 'memory_peak_bytes': int((cgroup/'memory.peak').read_text()),
                             'observed_utc': now(), 'memory_scope': 'Agent cgroup observed before interrupted-run cleanup; not hosted model memory'}
            except OSError:
                pass
        subprocess.run(['systemctl', '--user', 'stop', unit], capture_output=True, timeout=20)
        (home/'auth.json').unlink(missing_ok=True)
        dump(run_dir/'checker.log', trace)
        costs = {'agent_wall_seconds': agent_seconds, 'checker_wall_seconds': checker_seconds,
                 'total_wall_seconds': time.monotonic()-clock, 'sandbox': resources,
                 'checker_max_cgroup_memory_peak_bytes': max([((row.get('resources') or {}).get('memory_peak_bytes') or 0) for row in trace], default=0) or None,
                 'controller_peak_rss_bytes_linux': process_resource.getrusage(process_resource.RUSAGE_SELF).ru_maxrss*1024,
                 'provider_usage_events': usage,
                 'tokens': {key: sum(u.get(key, 0) for u in usage) for key in ('input_tokens', 'cached_input_tokens', 'output_tokens')} if usage else None,
                 'monetary_cost': None, 'hosted_inference_memory_bytes': None}
        dump(run_dir/'resources.json', costs)
        report = {'schema_version': 1, 'started_utc': started, 'ended_utc': now(), 'configuration': cfg,
                  'result': result, 'resources': costs, 'submission_claim': claim,
                  'checks': {'fixed_goal_gate': 'passed' if len(trace) > 1 and trace[1].get('exit_code') == 0 else 'not-passed-or-not-run',
                             'axiom_audit': 'passed' if len(trace) == (3 if platform == 'lean' else 4) and trace[-1].get('exit_code') == 0 else 'not-passed-or-not-run',
                             'independent_coqchk': ('passed' if len(trace) > 2 and trace[2].get('exit_code') == 0 else 'not-passed-or-not-run') if platform == 'rocq' else None,
                             'allowed_axioms': ['propext', 'Classical.choice', 'Quot.sound'] if platform == 'lean' else [],
                             'full_stage_output': 'checker.log'},
                  'proof_sha256': sha((run_dir/proof_name).read_bytes()) if (run_dir/proof_name).exists() else None,
                  'transcript': {'format': 'Codex CLI --json', 'event_count': event_count, 'invalid_lines': invalid,
                                 'turn_completed': complete, 'events_flushed_live': True,
                                 'limitations': 'All CLI-emitted events are retained; hidden reasoning, tool output omitted by the CLI, and server-side resolved model metadata are not independently available.'}}
        dump(run_dir/'report.json', report)
        (run_dir/'report.md').write_text('# Evaluation report\n\n'+
            f'- Task: `{task_id}` / {platform}\n- Model: `gpt-6-luna`, medium\n- Result: **{result["status"]}**\n'+
            f'- Agent / checker seconds: {agent_seconds} / {checker_seconds}\n- Tokens: {costs["tokens"]}\n'+
            f'- Cgroup peak bytes: {resources.get("memory_peak_bytes") if resources else None}\n- Billing / hosted-model memory: unavailable\n')
        dump(run_dir/'live.json', {'phase': 'finished', 'updated_utc': now(), 'result': result})
        files = sorted(p for p in run_dir.iterdir() if p.is_file() and p.name != 'SHA256SUMS')
        (run_dir/'SHA256SUMS').write_text(''.join(sha(p.read_bytes())+'  '+p.name+'\n' for p in files))
    return run_dir, report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', required=True)
    parser.add_argument('--platform', choices=('lean', 'rocq'), default='lean')
    args = parser.parse_args()
    directory, report = run(args.task, args.platform)
    print(json.dumps({'run_dir': str(directory), 'result': report['result']}))
