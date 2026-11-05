"""Prepare isolated original Clight factorial goals, without proving them."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from single_task_runner import tree_digest
from verify_freeze import main as verify_freeze

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'benchmarks/tasks/algorithms-core/compcert'
BASE = ROOT / '_build/pilot-v1'
COQC = '/home/yangfp/.opam/five/bin/coqc'

def main():
    verify_freeze()
    for kind, style, pred in [('equivalence', 1, 'Equivalent'), ('counterexample', 2, 'Counterexample')]:
        target = BASE / ('factorial-compcert-original-' + kind)
        if target.exists(): raise SystemExit('Preserve existing output: ' + str(target))
        task = target / 'task'; task.mkdir(parents=True)
        sources = [SOURCE / 'BasicDomain.v', SOURCE / 'Execution.v', SOURCE / 'ast/FACTORIAL_V0.v', SOURCE / f'ast/FACTORIAL_V{style}.v']
        hashes = {}
        for src in sources:
            hashes[src.relative_to(ROOT).as_posix()] = hashlib.sha256(src.read_bytes()).hexdigest()
            shutil.copyfile(src, task / src.name)
            subprocess.run([COQC, '-q', '-Q', str(task), 'Trusted', str(task / src.name)], check=True, timeout=180)
        body = f'''From Trusted Require Import BasicDomain Execution FACTORIAL_V0 FACTORIAL_V{style}.
Definition left_impl : implementation :=
  {{| program := FACTORIAL_V0.prog; input_symbol := FACTORIAL_V0._eb_input; output_symbol := FACTORIAL_V0._eb_output |}}.
Definition right_impl : implementation :=
  {{| program := FACTORIAL_V{style}.prog; input_symbol := FACTORIAL_V{style}._eb_input; output_symbol := FACTORIAL_V{style}._eb_output |}}.
Definition goal : Prop := {pred} (BasicDomain.valid 0) BasicDomain.encode left_impl right_impl.
'''
        (task / 'Obligation.v').write_text(body)
        subprocess.run([COQC, '-q', '-Q', str(task), 'Trusted', str(task / 'Obligation.v')], check=True, timeout=180)
        meta = json.loads((BASE / ('factorial-rocq-' + kind) / 'registry.json').read_text())
        meta.update({'platform': 'compcert', 'public_sha256': tree_digest(task), 'binding_status': 'pending-original-goal-review',
                     'original_source_sha256': hashes, 'fixed_witness': None,
                     'scope': 'Actual frozen Clight ASTs and CompCert small-step semantics; original-goal correspondence must be checked.'})
        (target / 'registry.json').write_text(json.dumps(meta, indent=2) + '\n')
        print(json.dumps(meta), flush=True)

if __name__ == '__main__': main()
