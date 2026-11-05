"""Prepare a Lean factorial counterexample reference with a fixed witness.

The fixed input is [1], so this reference checks a concrete counterexample;
it is not a measurement of an agent's ability to discover the input.
"""
import json
import shutil
from pathlib import Path

from prepare_factorial import compile_file,verify_freeze,ORIGINAL
from private_paths import PRIVATE
from single_task_runner import tree_digest

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/'_build/pilot-v1/factorial-cex'
TASK='''import Lean
namespace Task
abbrev Words := List Int
def iz (xs : Words) (i : Nat) : Int := (xs[i]?).getD 0
def finish (xs : Words) : Words := Int.ofNat xs.length :: xs
def factorialRec : Nat → Int | 0 => 1 | n+1 => Int.ofNat (n+1) * factorialRec n
def factorialBad : Nat → Int → Int
  | 0,a => a
  | n+1,a => factorialBad n (a*Int.ofNat n)
def inRange (v lo hi : Int) : Bool := lo ≤ v && v ≤ hi
def valid (xs : Words) : Prop := (xs.length == 1 && inRange (iz xs 0) 0 12) = true
def a (xs : Words) : Option Words := some (finish [factorialRec (iz xs 0).toNat])
def b (xs : Words) : Option Words := some (finish [factorialBad (iz xs 0).toNat 1])
def equivalent : Prop := ∀ x, valid x → ∃ o, a x = some o ∧ b x = some o
def refutationAt (x oa ob : Words) : Prop := valid x ∧ a x = some oa ∧ b x = some ob ∧ oa ≠ ob
end Task
'''
OBLIGATION='''import Task
namespace Obligation
def goal : Prop := Task.refutationAt [1] [1,1] [1,0]
end Obligation
'''
BINDING='''import BasicDomain
import Task
theorem rec_eq (n : Nat) : Task.factorialRec n = SpecLessBenchBasic.factorialRec n := by
  induction n with
  | zero => rfl
  | succ n ih => simp [Task.factorialRec, SpecLessBenchBasic.factorialRec, ih]
theorem bad_eq (n : Nat) (a : Int) : Task.factorialBad n a = SpecLessBenchBasic.factorialAcc true n a := by
  induction n generalizing a with
  | zero => rfl
  | succ n ih => simp [Task.factorialBad, SpecLessBenchBasic.factorialAcc, ih]
theorem a_eq (x : Task.Words) : Task.a x = SpecLessBenchBasic.entry 0 0 x := by
  simp [Task.a, SpecLessBenchBasic.entry, Task.finish, SpecLessBenchBasic.finish, Task.iz, SpecLessBenchBasic.iz, rec_eq]
theorem b_eq (x : Task.Words) : Task.b x = SpecLessBenchBasic.entry 0 2 x := by
  simp [Task.b, SpecLessBenchBasic.entry, Task.finish, SpecLessBenchBasic.finish, Task.iz, SpecLessBenchBasic.iz, bad_eq]
example : Task.equivalent = SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid 0) (SpecLessBenchBasic.entry 0 0) (SpecLessBenchBasic.entry 0 2) := by
  unfold Task.equivalent SpecLessBenchBasic.Equivalent
  have va : Task.valid = SpecLessBenchBasic.valid 0 := by funext x; rfl
  rw [va, funext a_eq, funext b_eq]
example (x oa ob : Task.Words) : Task.refutationAt x oa ob = (SpecLessBenchBasic.valid 0 x ∧ SpecLessBenchBasic.entry 0 0 x = some oa ∧ SpecLessBenchBasic.entry 0 2 x = some ob ∧ oa ≠ ob) := by
  unfold Task.refutationAt
  rw [a_eq x, b_eq x]
  rfl
'''


def main():
    verify_freeze()
    if BUILD.exists():raise SystemExit('Existing output: preserve it and inspect before rebuilding')
    task=BUILD/'task';original=BUILD/'grader';binding=BUILD/'binding'
    for d in (task,original,binding):d.mkdir(parents=True)
    (task/'Task.lean').write_text(TASK);(task/'Obligation.lean').write_text(OBLIGATION)
    compile_file(task,'Task',[task]);compile_file(task,'Obligation',[task])
    for name in ('BasicNative.lean','BasicDomain.lean'):shutil.copyfile(ORIGINAL/name,original/name)
    compile_file(original,'BasicNative',[original]);compile_file(original,'BasicDomain',[original])
    (binding/'Binding.lean').write_text(BINDING);compile_file(binding,'Binding',[task,original])
    row=next(x for x in json.loads((PRIVATE/'mapping.json').read_text())['contexts'] if x['source_context_id']=='R-FAC-CEX')
    report={'pilot_id':row['pilot_id'],'platform':'lean','claim':'counterexample','purpose':'reference',
            'witness':{'input':[1],'left_observation':[1,1],'right_observation':[1,0]},
            'public_sha256':tree_digest(task),'grader_sha256':tree_digest(task),
            'frozen_binding_dependency_sha256':tree_digest(original),'binding':'lean-kernel-checked-correspondence',
            'scope':'Fixed literal witness; no claim of autonomous witness discovery.', 'final_proof_attempted':False}
    (BUILD/'registry.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
