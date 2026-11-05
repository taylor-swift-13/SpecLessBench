"""Prepare factorial goals against the unchanged frozen Rocq implementation."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from single_task_runner import tree_digest
from verify_freeze import main as verify_freeze

ROOT = Path(__file__).resolve().parents[2]
COQC = Path('/home/yangfp/.opam/qcp-8.20/bin/coqc')
BASE = ROOT / '_build/pilot-v1'
SOURCE = ROOT / 'benchmarks/tasks/algorithms-core/rocq'

def main():
    verify_freeze()
    for kind, style, predicate in [('equivalence', 1, 'Equivalent'), ('counterexample', 2, 'Counterexample')]:
        prior = BASE / ('factorial-rocq-' + kind)
        target = BASE / ('factorial-rocq-original-' + kind)
        if target.exists(): raise SystemExit('Preserve existing output: ' + str(target))
        task = target / 'task'; source = target / 'source'
        task.mkdir(parents=True); source.mkdir()
        hashes = {}
        for name in ('BasicNative', 'BasicDomain'):
            src = SOURCE / (name + '.v')
            hashes[name] = hashlib.sha256(src.read_bytes()).hexdigest()
            shutil.copyfile(src, source / (name + '.v'))
            subprocess.run([str(COQC), '-q', '-Q', str(source), 'Trusted', str(source / (name + '.v'))], check=True, timeout=120)
            shutil.copyfile(source / (name + '.vo'), task / (name + '.vo'))
        # An isolated readable helper describes only this factorial family.
        shutil.copyfile(prior / 'task/Task.v', task / 'Task.v')
        (task / 'Obligation.v').write_text('From Trusted Require Import BasicNative BasicDomain.\nDefinition goal : Prop := BasicNative.' + predicate + ' (BasicDomain.valid 0) (BasicNative.entry 0 0) (BasicNative.entry 0 ' + str(style) + ').\n')
        subprocess.run([str(COQC), '-q', '-Q', str(task), 'Trusted', str(task / 'Obligation.v')], check=True, timeout=120)
        meta = json.loads((prior / 'registry.json').read_text())
        meta.update({'public_sha256': tree_digest(task), 'binding_status': 'original-source', 'original_source_sha256': hashes,
                     'fixed_witness': None, 'scope': 'The exact frozen source modules are compiled under the Trusted namespace; only factorial context and this goal are exposed.'})
        (target / 'registry.json').write_text(json.dumps(meta, indent=2) + '\n')
        print(json.dumps(meta), flush=True)

if __name__ == '__main__': main()
