"""Rebuild the actual Clight factorial target and check its proof and assumptions."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from rocq_grader_core import allowed_assumptions
from sandbox import run_isolated, TOOLCHAINS
from single_task_runner import tree_digest
from verify_freeze import main as verify_freeze

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'benchmarks/tasks/algorithms-core/compcert'
COQC = TOOLCHAINS['compcert'] + '/bin/coqc'
COQCHK = TOOLCHAINS['compcert'] + '/bin/coqchk'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--timeout', type=int, default=600, help='per-check timeout in seconds')
    args = parser.parse_args(); run = args.run
    if (run/'SHA256SUMS').exists():
        listed=set()
        for row in (run/'SHA256SUMS').read_text().splitlines():
            digest, name=row.split('  ',1); rel=Path(name)
            if rel.is_absolute() or '..' in rel.parts or rel in listed: raise SystemExit('Invalid checksum path')
            listed.add(rel)
            if hashlib.sha256((run/rel).read_bytes()).hexdigest()!=digest: raise SystemExit('Checksum mismatch: '+name)
        actual={p.relative_to(run) for p in run.rglob('*') if p.is_file() and p.name!='SHA256SUMS'}
        if listed!=actual: raise SystemExit('Unlisted or missing reference file')
    cfg = json.loads((run / 'config.json').read_text()); kind = cfg['claim']
    if (run/'runner.py').exists() and hashlib.sha256((run/'runner.py').read_bytes()).hexdigest()!=cfg['runner_sha256']:
        raise SystemExit('Recorded runner mismatch')
    if cfg['platform'] != 'compcert': raise SystemExit('Not a CompCert run')
    style, pred, name = (1, 'Equivalent', 'R_FAC_EQ') if kind == 'equivalence' else (2, 'Counterexample', 'R_FAC_CEX')
    verify_freeze()
    source_goal = (SOURCE / 'FACTORIALGoals.v').read_text()
    target = f'{pred} (BasicDomain.valid 0) BasicDomain.encode impl_FACTORIAL_V0 impl_FACTORIAL_V{style}'
    if f'Theorem {name} : {target}.' not in source_goal: raise SystemExit('Frozen theorem mismatch')
    definitions = []
    for version in (0, style):
        match = re.search(rf'Definition impl_FACTORIAL_V{version} : implementation :=\n  \{{\|[^\n]+\|\}}\.', source_goal)
        if not match: raise SystemExit('Frozen implementation definition missing')
        definitions.append(match.group())
    for rel, digest in cfg['original_source_sha256'].items():
        if hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() != digest: raise SystemExit('Frozen source mismatch: ' + rel)
    original_task = run / 'private/task' if (run / 'private/task').exists() else run / 'task'
    if tree_digest(original_task) != cfg['task_digest']: raise SystemExit('Task digest mismatch')
    with tempfile.TemporaryDirectory(prefix='specless-compcert-original-') as temp:
        base = Path(temp); trusted = base/'trusted'; trusted.mkdir(); submission = base/'submission'; submission.mkdir()
        names = ['BasicDomain', 'Execution', 'FACTORIAL_V0', f'FACTORIAL_V{style}']
        for module in names:
            src = SOURCE / ('ast' if module.startswith('FACTORIAL_') else '') / (module + '.v')
            shutil.copyfile(src, trusted/(module+'.v'))
            subprocess.run([COQC, '-q', '-Q', str(trusted), 'Trusted', str(trusted/(module+'.v'))], check=True, timeout=180)
        goal_source = (original_task/'Obligation.v').read_text()
        (trusted/'Obligation.v').write_text(goal_source)
        subprocess.run([COQC, '-q', '-Q', str(trusted), 'Trusted', str(trusted/'Obligation.v')], check=True, timeout=180)
        shutil.copyfile(run/'Submission.v', submission/'Submission.v')
        trace=[]
        def check(argv, collect=None):
            r = run_isolated('compcert', trusted, submission, argv, timeout=args.timeout, collect=collect, phase='reference-check')
            trace.append(r)
            if r['status'] != 'exited' or r['exit_code'] != 0: raise SystemExit('Bridge check failed: ' + json.dumps(r))
            return r
        common = [COQC, '-q', '-noglob', '-Q', '/trusted', 'Trusted']
        r = check(common + ['-Q','/submission','Candidate','-Q','/work','Candidate','-o','/work/Submission.vo','/submission/Submission.v'], ['Submission.vo'])
        (trusted/'candidate').mkdir(); (trusted/'candidate/Submission.vo').write_bytes(r['artifacts']['Submission.vo'])
        bridge = (f'From Trusted Require Import BasicDomain Execution FACTORIAL_V0 FACTORIAL_V{style}.\n'
                  'From Candidate Require Import Submission.\n' + '\n'.join(definitions) + '\n'
                  f'Theorem checked_original : {target}.\nProof. exact Submission.solve. Qed.\n')
        (trusted/'Bridge.v').write_text(bridge)
        r = check(common + ['-Q','/trusted/candidate','Candidate','-Q','/work','Trusted','-o','/work/Bridge.vo','/trusted/Bridge.v'], ['Bridge.vo'])
        (trusted/'Bridge.vo').write_bytes(r['artifacts']['Bridge.vo'])
        check([COQCHK, '-bytecode-compiler','yes','-Q','/trusted','Trusted','-Q','/trusted/candidate','Candidate','Trusted.Bridge'])
        (trusted/'Audit.v').write_text('Set Printing Fully Qualified.\nFrom Trusted Require Import Bridge.\nPrint Assumptions Bridge.checked_original.\n')
        audit = check(common + ['-Q','/trusted/candidate','Candidate','-Q','/work','Trusted','-o','/work/Audit.vo','/trusted/Audit.v'], ['Audit.vo'])
        if audit.get('output_truncated') or not allowed_assumptions('compcert', audit['stdout']):
            raise SystemExit('Unapproved assumptions: '+audit['stdout'])
        evidence = {'theorem':name,'status':'accepted','source':'frozen sources rebuilt; original definitions and goal bridged by kernel',
                    'assumptions':audit['stdout'],'per_check_timeout_seconds':args.timeout,'coqchk_bytecode_compiler':True,
                    'grader_sha256':hashlib.sha256((ROOT/'scripts/pilot/rocq_grader_core.py').read_bytes()).hexdigest(),
                    'checks':[{k:r.get(k) for k in ('status','exit_code','resources','output_truncated')} for r in trace]}
        print(json.dumps(evidence, indent=2))

if __name__ == '__main__': main()
