"""Prepare the first real, isolated Lean task from the frozen factorial pair.

The small projection contains only this pair. Lean checks its binding to the
frozen target using auxiliary correspondence lemmas; no task proof is attempted.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

from private_paths import PRIVATE
from single_task_runner import tree_digest
from verify_freeze import main as verify_freeze

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / '_build/pilot-v1/first-real-task'
ORIGINAL = ROOT / 'benchmarks/tasks/algorithms-core/lean'
LEAN = '/home/yangfp/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean'

TASK = '''import Lean
namespace Task
abbrev Words := List Int
def iz (xs : Words) (i : Nat) : Int := (xs[i]?).getD 0
def finish (xs : Words) : Words := Int.ofNat xs.length :: xs
def factorialRec : Nat → Int | 0 => 1 | n+1 => Int.ofNat (n+1) * factorialRec n
def factorialAcc : Nat → Int → Int
  | 0,a => a
  | n+1,a => factorialAcc n (a*Int.ofNat (n+1))
def inRange (v lo hi : Int) : Bool := lo ≤ v && v ≤ hi
def valid (xs : Words) : Prop := (xs.length == 1 && inRange (iz xs 0) 0 12) = true
def a (xs : Words) : Option Words := some (finish [factorialRec (iz xs 0).toNat])
def b (xs : Words) : Option Words := some (finish [factorialAcc (iz xs 0).toNat 1])
def equivalent : Prop := ∀ x, valid x → ∃ o, a x = some o ∧ b x = some o
def refutationAt (x oa ob : Words) : Prop := valid x ∧ a x = some oa ∧ b x = some ob ∧ oa ≠ ob
end Task
'''
PUBLIC_OBLIGATION = '''import Task
namespace Obligation
def goal : Prop := Task.equivalent
end Obligation
'''
PRIVATE_OBLIGATION = '''import BasicDomain
namespace Obligation
def goal : Prop := SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid 0) (SpecLessBenchBasic.entry 0 0) (SpecLessBenchBasic.entry 0 1)
end Obligation
'''
BINDING = '''import BasicDomain
import Task
theorem rec_eq (n : Nat) : Task.factorialRec n = SpecLessBenchBasic.factorialRec n := by
  induction n with
  | zero => rfl
  | succ n ih => simp [Task.factorialRec, SpecLessBenchBasic.factorialRec, ih]
theorem acc_eq (n : Nat) (a : Int) : Task.factorialAcc n a = SpecLessBenchBasic.factorialAcc false n a := by
  induction n generalizing a with
  | zero => rfl
  | succ n ih => simp [Task.factorialAcc, SpecLessBenchBasic.factorialAcc, ih]
theorem a_eq (x : Task.Words) : Task.a x = SpecLessBenchBasic.entry 0 0 x := by
  simp [Task.a, SpecLessBenchBasic.entry, Task.finish, SpecLessBenchBasic.finish, Task.iz, SpecLessBenchBasic.iz, rec_eq]
theorem b_eq (x : Task.Words) : Task.b x = SpecLessBenchBasic.entry 0 1 x := by
  simp [Task.b, SpecLessBenchBasic.entry, Task.finish, SpecLessBenchBasic.finish, Task.iz, SpecLessBenchBasic.iz, acc_eq]
example : Task.equivalent = SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid 0) (SpecLessBenchBasic.entry 0 0) (SpecLessBenchBasic.entry 0 1) := by
  unfold Task.equivalent SpecLessBenchBasic.Equivalent
  have va : Task.valid = SpecLessBenchBasic.valid 0 := by funext x; rfl
  rw [va, funext a_eq, funext b_eq]
example (x oa ob : Task.Words) : Task.refutationAt x oa ob = (SpecLessBenchBasic.valid 0 x ∧ SpecLessBenchBasic.entry 0 0 x = some oa ∧ SpecLessBenchBasic.entry 0 1 x = some ob ∧ oa ≠ ob) := by
  unfold Task.refutationAt
  rw [a_eq x, b_eq x]
  rfl
'''


def compile_file(directory, name, paths):
    env = dict(os.environ, LEAN_PATH=':'.join(str(p) for p in paths))
    result = subprocess.run([LEAN, '-j', '1', '-o', str(directory / (name + '.olean')),
                             str(directory / (name + '.lean'))], cwd=directory,
                            env=env, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(name + ':\n' + result.stdout + result.stderr)


def main():
    verify_freeze()
    if BUILD.exists():
        meta = json.loads((BUILD / 'registry.json').read_text())
        if tree_digest(BUILD / 'task') != meta['public_sha256'] or tree_digest(BUILD / 'grader') != meta['frozen_binding_dependency_sha256']:
            raise SystemExit('Existing task package was modified; inspect it before rebuilding.')
        print(json.dumps(meta))
        return
    public = BUILD / 'task'; hidden = BUILD / 'grader'; check = BUILD / 'binding'
    for d in (public, hidden, check): d.mkdir(parents=True)
    (public / 'Task.lean').write_text(TASK)
    (public / 'Obligation.lean').write_text(PUBLIC_OBLIGATION)
    compile_file(public, 'Task', [public])
    compile_file(public, 'Obligation', [public])
    for name in ('BasicNative.lean', 'BasicDomain.lean'):
        shutil.copyfile(ORIGINAL / name, hidden / name)
    compile_file(hidden, 'BasicNative', [hidden])
    compile_file(hidden, 'BasicDomain', [hidden])
    (hidden / 'Obligation.lean').write_text(PRIVATE_OBLIGATION)
    compile_file(hidden, 'Obligation', [hidden])
    (check / 'Binding.lean').write_text(BINDING)
    compile_file(check, 'Binding', [public, hidden])
    row = next(x for x in json.loads((PRIVATE / 'mapping.json').read_text())['contexts']
               if x['source_context_id'] == 'R-FAC-EQ')
    result = {'pilot_id': row['pilot_id'], 'platform': 'lean', 'claim': 'equivalence',
              'public_sha256': tree_digest(public), 'grader_sha256': tree_digest(public),
              'frozen_binding_dependency_sha256': tree_digest(hidden),
              'binding': 'lean-kernel-checked-correspondence', 'final_proof_attempted': False}
    (BUILD / 'registry.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__': main()
