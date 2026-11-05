"""Publish a separately checked original-source Rocq factorial reference run."""
import argparse
import gzip
import hashlib
import json
import resource
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    args = parser.parse_args(); run = args.run
    report = json.loads((run / 'report.json').read_text()); cfg = report['configuration']
    start = time.monotonic()
    check = subprocess.run([sys.executable, str(ROOT / 'scripts/pilot/verify_factorial_rocq_original.py'), str(run)],
                           capture_output=True, text=True, timeout=600)
    check_wall = time.monotonic() - start
    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    if check.returncode: raise SystemExit('Independent verification failed: ' + check.stdout + check.stderr)
    target = ROOT / 'benchmarks/reports' / cfg['task_id'] / 'rocq' / cfg['claim'] / run.name
    if target.exists(): raise SystemExit('Reference already exists: ' + str(target))
    runner = ROOT / 'scripts/pilot/run_factorial_rocq_wsl.py'
    if hashlib.sha256(runner.read_bytes()).hexdigest() != cfg['runner_sha256']:
        raise SystemExit('Run-time runner differs from current file; recover the exact recorded runner first')
    target.mkdir(parents=True)
    for name in ('Submission.v', 'agent.stderr', 'codex-config.toml', 'config.json', 'events.jsonl',
                 'events.timestamps.jsonl', 'prompt.txt', 'report.json'):
        shutil.copyfile(run / name, target / name)
    shutil.copytree(run / 'private/task', target / 'task')
    shutil.copyfile(runner, target / 'runner.py')
    with (run / 'checker.json').open('rb') as src, gzip.open(target / 'checker.json.gz', 'wb') as dst:
        shutil.copyfileobj(src, dst)
    (target / 'verification.log').write_text(check.stdout + check.stderr)
    (target / 'verification.json').write_text(json.dumps({'wall_seconds': check_wall,
        'child_cpu_seconds': child.ru_utime + child.ru_stime,
        'max_child_process_rss_bytes': child.ru_maxrss * 1024,
        'memory_scope': 'largest individual child-process maximum RSS, not a concurrent process-tree peak',
        'checker_sha256': hashlib.sha256((ROOT / 'scripts/pilot/verify_factorial_rocq_original.py').read_bytes()).hexdigest()}, indent=2) + '\n')
    token = report.get('usage', [])
    (target / 'report.md').write_text('# Rocq factorial reference\n\n'
        f'- Goal: `{cfg["claim"]}`, task `{cfg["task_id"]}`, frozen original source.\n'
        f'- Model configured: `{cfg["model"]}` ({cfg["reasoning_effort"]}); server-resolved identity is unavailable.\n'
        '- Independent check: accepted after rebuilding original sources; `coqchk` passed and assumptions are closed.\n'
        f'- Agent wall time: {report["agent_wall_seconds"]:.2f} seconds.\n'
        f'- Agent resource and token records: `report.json`; usage: `{json.dumps(token)}`.\n'
        '- Hosted model memory and monetary cost: unavailable.\n'
        '- The raw run report calls its checker result `projected_result` and leaves `original_goal_result` pending; '
        'the independent original-source rebuild is recorded in `verification.log`.\n')
    rows=[]
    for path in sorted(target.rglob('*')):
        if path.is_file() and path.name != 'SHA256SUMS':
            rows.append(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+path.relative_to(target).as_posix())
    (target / 'SHA256SUMS').write_text('\n'.join(rows)+'\n')
    print(target)

if __name__ == '__main__': main()
