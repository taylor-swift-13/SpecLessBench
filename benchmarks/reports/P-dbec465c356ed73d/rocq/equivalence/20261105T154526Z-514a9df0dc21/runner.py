"""Run one isolated projected factorial Rocq obligation; this is not a gold proof."""
import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

from grade_sealed import grade
from single_task_runner import tree_digest

ROOT = Path(__file__).resolve().parents[2]
HOME = Path.home()
CODEX_DIR = HOME / '.nvm/versions/node/v20.17.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin'
COQ = HOME / '.opam/qcp-8.20'
PROMPT = ('Prove exactly the fixed Rocq theorem Obligation.goal in /task. '
          'Work only in /work. Write /work/Submission.v, importing '
          'From Trusted Require Import Obligation and defining Submission.solve : Obligation.goal. '
          'Use coqc -Q /task Trusted -Q /work Candidate /work/Submission.v to check. '
          'You may add helper lemmas. Do not use axioms, Admitted, or admit.')

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind', choices=['equivalence', 'counterexample'])
    parser.add_argument('--original', action='store_true', help='use the frozen original definitions and target')
    args = parser.parse_args()
    src = ROOT / '_build/pilot-v1' / ('factorial-rocq-' + ('original-' if args.original else '') + args.kind)
    meta = json.loads((src / 'registry.json').read_text())
    if tree_digest(src / 'task') != meta['public_sha256']:
        raise RuntimeError('Task package changed')
    os.umask(0o077)
    run = HOME / '.local/share/speclessbench/rocq-reference-runs' / (dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ-') + uuid.uuid4().hex[:12])
    run.mkdir(parents=True)
    private = run / 'private'; private.mkdir()
    task = private / 'task'; shutil.copytree(src / 'task', task)
    work = private / 'work'; work.mkdir()
    home = private / 'home'; home.mkdir()
    (home / 'auth.json').touch(mode=0o600)
    config = '''default_permissions = "eval"
approval_policy = "never"
model = "gpt-6.1-sol"
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
    (home / 'config.toml').write_text(config)
    (run / 'codex-config.toml').write_text(config)
    (run / 'prompt.txt').write_text(PROMPT + '\n')
    def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
    settings = {'model': 'gpt-6.1-sol', 'reasoning_effort': 'medium', 'platform': 'rocq',
                'claim': args.kind, 'task_id': meta['pilot_id'], 'goal': 'Obligation.goal',
                'task_digest': meta['public_sha256'], 'timeout_seconds': 3600,
                'model_identity_scope': 'CLI configuration; resolved server model not independently exposed',
                'codex_sha256': sha(CODEX_DIR / 'codex'), 'runner_sha256': sha(Path(__file__)),
                'codex_version': subprocess.check_output([str(CODEX_DIR / 'codex'), '--version'], text=True).strip(),
                'rocq_version': subprocess.check_output([str(COQ / 'bin/coqc'), '--version'], text=True).strip(),
                'original_goal_binding': 'original-source; independent reproducibility review pending' if args.original else 'pending; projected-goal acceptance alone is not gold',
                'original_source_sha256': meta.get('original_source_sha256'),
                'fixed_witness': meta.get('fixed_witness')}
    dump(run / 'config.json', settings)
    cmd = ['/usr/bin/bwrap', '--unshare-all', '--share-net', '--die-with-parent', '--new-session',
           '--ro-bind', '/usr', '/usr', '--ro-bind', '/lib', '/lib', '--ro-bind', '/lib64', '/lib64', '--symlink', 'usr/bin', '/bin',
           '--dir', '/etc', '--ro-bind', '/etc/resolv.conf', '/etc/resolv.conf', '--ro-bind', '/etc/hosts', '/etc/hosts',
           '--ro-bind', '/etc/nsswitch.conf', '/etc/nsswitch.conf', '--ro-bind', '/etc/ssl', '/etc/ssl',
           '--dir', '/home', '--dir', '/home/runner', '--dir', '/home/runner/.codex', '--bind', str(home), '/home/runner/.codex',
           '--ro-bind', str(HOME / '.codex/auth.json'), '/home/runner/.codex/auth.json',
           '--dir', '/opt', '--ro-bind', str(CODEX_DIR / 'codex'), '/opt/codex',
           '--ro-bind', str(CODEX_DIR / 'codex-code-mode-host'), '/opt/codex-code-mode-host', '--symlink', 'codex', '/opt/codex-linux-sandbox',
           '--ro-bind', str(COQ), '/opt/rocq', '--ro-bind', str(task), '/task', '--bind', str(work), '/work',
           '--tmpfs', '/tmp', '--dev', '/dev', '--proc', '/proc', '--clearenv',
           '--setenv', 'HOME', '/home/runner', '--setenv', 'CODEX_HOME', '/home/runner/.codex',
           '--setenv', 'PATH', '/opt:/opt/rocq/bin:/usr/bin:/bin', '--setenv', 'LANG', 'C.UTF-8',
           '--setenv', 'OCAMLFIND_CONF', '/opt/rocq/lib/findlib.conf', '--setenv', 'OCAMLPATH', '/opt/rocq/lib',
           '--setenv', 'TOKIO_WORKER_THREADS', '4', '--setenv', 'RAYON_NUM_THREADS', '4']
    from urllib.parse import urlsplit
    for key in ('HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY', 'http_proxy', 'https_proxy', 'no_proxy'):
        if os.environ.get(key):
            value = os.environ[key]
            if urlsplit(value).username or urlsplit(value).password: raise RuntimeError('Credential-bearing proxy')
            cmd += ['--setenv', key, value]
    cmd += ['--chdir', '/work', '--', '/opt/codex', 'exec', '--ephemeral', '--skip-git-repo-check', '--json', '-C', '/work', PROMPT]
    resource = private / 'resource.json'; supervisor = private / 'supervisor.json'
    dump(supervisor, {'argv': cmd, 'timeout': 3600, 'memory_limit': 3 * 1024**3, 'pids_limit': 512, 'report': str(resource)})
    unit = 'specless-rocq-' + uuid.uuid4().hex + '.scope'
    launch = ['/usr/bin/systemd-run', '--user', '--scope', '--quiet', '--unit', unit, '-p', 'MemoryMax=3221225472',
              '-p', 'MemorySwapMax=0', '-p', 'TasksMax=512', '/usr/bin/python3', str(ROOT / 'scripts/pilot/resource_supervisor.py'), str(supervisor)]
    print('RUN_DIR=' + str(run), flush=True)
    started = now(); clock = time.monotonic()
    try:
        with (run / 'events.jsonl').open('wb') as events, (run / 'events.timestamps.jsonl').open('w') as timestamps, (run / 'agent.stderr').open('wb') as err:
            proc = subprocess.Popen(launch, stdout=subprocess.PIPE, stderr=err, stdin=subprocess.DEVNULL, start_new_session=True)
            def capture():
                for index, line in enumerate(proc.stdout):
                    events.write(line); events.flush()
                    timestamps.write(json.dumps({'line': index + 1, 'received_utc': now()}) + '\n'); timestamps.flush()
            thread = threading.Thread(target=capture, daemon=True); thread.start()
            try: code = proc.wait(timeout=3630)
            except subprocess.TimeoutExpired:
                subprocess.run(['/usr/bin/systemctl', '--user', 'stop', unit], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                proc.kill(); proc.wait(); code = None
            thread.join(timeout=15)
    finally:
        subprocess.run(['/usr/bin/systemctl', '--user', 'stop', unit], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        (home / 'auth.json').unlink(missing_ok=True)
    duration = time.monotonic() - clock
    resources = json.loads(resource.read_text()) if resource.exists() else None
    events = [json.loads(line) for line in (run / 'events.jsonl').read_text().splitlines()]
    usage = [event['usage'] for event in events if event.get('type') == 'turn.completed' and event.get('usage')]
    submission = work / 'Submission.v'; trace = []
    if resources and resources.get('status') == 'exited' and resources.get('exit_code') == 0 and submission.is_file() and not submission.is_symlink():
        shutil.copyfile(submission, run / 'Submission.v')
        result = grade('rocq', task, meta['public_sha256'], run / 'Submission.v', trace=trace)
    else:
        result = {'status': 'agent-error', 'detail': 'Process failed, timed out, or produced no submission'}
    dump(run / 'checker.json', trace)
    dump(run / 'report.json', {'schema_version': 1, 'configuration': settings, 'started_utc': started, 'ended_utc': now(),
        'agent_wall_seconds': duration, 'supervisor_exit_code': code, 'resources': resources, 'usage': usage,
        'monetary_cost': None, 'hosted_model_memory_bytes': None, 'projected_result': result,
        'original_goal_result': 'pending', 'transcript': 'events.jsonl', 'limitations': 'Projected goal only; original binding is not proved. Provider metadata does not independently identify resolved model.'})
    print(json.dumps({'run': str(run), 'projected_result': result, 'original_goal_result': 'pending'}), flush=True)
    return 0 if result.get('status') == 'accepted' else 1

if __name__ == '__main__':
    sys.exit(main())
