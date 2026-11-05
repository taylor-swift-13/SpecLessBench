"""Rebuild a Rocq factorial theorem from frozen sources and recheck its proof."""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from grade_sealed import grade
from single_task_runner import tree_digest
from verify_freeze import main as verify_freeze

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'benchmarks/tasks/algorithms-core/rocq'
COQC = '/home/yangfp/.opam/qcp-8.20/bin/coqc'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    args = parser.parse_args(); run = args.run
    if (run / 'SHA256SUMS').exists():
        listed = set()
        for row in (run / 'SHA256SUMS').read_text().splitlines():
            digest, name = row.split('  ', 1)
            rel = Path(name)
            if rel.is_absolute() or '..' in rel.parts or rel in listed: raise SystemExit('Invalid checksum path')
            listed.add(rel)
            if hashlib.sha256((run / rel).read_bytes()).hexdigest() != digest: raise SystemExit('Checksum mismatch: ' + name)
        actual = {p.relative_to(run) for p in run.rglob('*') if p.is_file() and p.name != 'SHA256SUMS'}
        if listed != actual: raise SystemExit('Unlisted or missing reference file')
    report = json.loads((run / 'report.json').read_text()); cfg = report['configuration']; kind = cfg['claim']
    if (run / 'runner.py').exists() and hashlib.sha256((run / 'runner.py').read_bytes()).hexdigest() != cfg['runner_sha256']:
        raise SystemExit('Recorded runner hash mismatch')
    if cfg.get('original_source_sha256') is None or report['projected_result']['status'] != 'accepted':
        raise SystemExit('No accepted original-source run')
    verify_freeze()
    source_goal = (SOURCE / 'BasicGoals.v').read_text()
    style, pred, theorem = (1, 'Equivalent', 'R_FAC_EQ') if kind == 'equivalence' else (2, 'Counterexample', 'R_FAC_CEX')
    target = f'BasicNative.{pred} (BasicDomain.valid 0) (BasicNative.entry 0 0) (BasicNative.entry 0 {style})'
    if f'Theorem {theorem} : {target}.' not in source_goal: raise SystemExit('Original theorem mismatch')
    for name in ('BasicNative', 'BasicDomain'):
        if hashlib.sha256((SOURCE / (name + '.v')).read_bytes()).hexdigest() != cfg['original_source_sha256'][name]:
            raise SystemExit('Original source hash mismatch: ' + name)
    task = run / 'private/task' if (run / 'private/task').exists() else run / 'task'
    if tree_digest(task) != cfg['task_digest']: raise SystemExit('Run task digest mismatch')
    expected = 'From Trusted Require Import BasicNative BasicDomain.\nDefinition goal : Prop := ' + target + '.\n'
    if (task / 'Obligation.v').read_text() != expected: raise SystemExit('Run target mismatch')
    with tempfile.TemporaryDirectory(prefix='specless-rocq-original-rebuild-') as tmp:
        folder = Path(tmp); trusted = folder / 'trusted'; trusted.mkdir()
        for name in ('BasicNative', 'BasicDomain'):
            shutil.copyfile(SOURCE / (name + '.v'), trusted / (name + '.v'))
            subprocess.run([COQC, '-q', '-Q', str(trusted), 'Trusted', str(trusted / (name + '.v'))], check=True, timeout=120)
        (trusted / 'Obligation.v').write_text(expected)
        subprocess.run([COQC, '-q', '-Q', str(trusted), 'Trusted', str(trusted / 'Obligation.v')], check=True, timeout=120)
        trace = []
        result = grade('rocq', trusted, tree_digest(trusted), run / 'Submission.v', timeout=120, trace=trace)
        if result['status'] != 'accepted': raise SystemExit('Rebuilt original theorem rejected: ' + json.dumps(result))
        print(json.dumps({'theorem': theorem, 'result': result, 'coqchk': 'passed', 'assumptions': 'Closed under the global context',
                          'source': 'freeze-verified source rebuilt independently', 'checker_stages': len(trace)}))

if __name__ == '__main__': main()
