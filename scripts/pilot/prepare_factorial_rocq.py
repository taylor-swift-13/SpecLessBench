"""Prepare separate Rocq factorial reference problems without proving them."""
import json
import os
import shutil
import subprocess
from pathlib import Path

from private_paths import PRIVATE
from single_task_runner import tree_digest
from verify_freeze import main as verify_freeze

ROOT=Path(__file__).resolve().parents[2]
COQC=Path('/home/yangfp/.opam/qcp-8.20/bin/coqc')
ORIGINAL=ROOT/'benchmarks/tasks/algorithms-core/rocq'
BASE=ROOT/'_build/pilot-v1'

TASK='''From Coq Require Import ZArith List Bool.
Import ListNotations.
Open Scope nat_scope.
Definition words := list Z.
Definition iz (xs : words) (i : nat) := nth i xs 0%Z.
Definition finish (xs : words) := Z.of_nat (length xs)::xs.
Fixpoint factorial_rec n : Z := match n with O => 1%Z | S k => (Z.of_nat (S k)*factorial_rec k)%Z end.
Fixpoint factorial_acc (mutant : bool) n a : Z := match n with O => a | S k =>
  factorial_acc mutant k (a*Z.of_nat (if mutant then k else S k))%Z end.
Definition in_range v lo hi := Z.leb lo v && Z.leb v hi.
Definition valid (xs : words) := (Nat.eqb (length xs) 1 && in_range (iz xs 0) 0 12) = true.
Definition a (xs : words) : option words := Some (finish [factorial_rec (Z.to_nat (iz xs 0))]).
Definition b (xs : words) : option words := Some (finish [factorial_acc MUTANT (Z.to_nat (iz xs 0)) 1%Z]).
Definition equivalent : Prop := forall x, valid x -> exists o, a x=Some o /\\ b x=Some o.
Definition refutationAt (x oa ob : words) : Prop := valid x /\\ a x=Some oa /\\ b x=Some ob /\\ oa<>ob.
'''
BINDING='''From Coq Require Import ZArith List Bool.
From Trusted Require Import Task.
From SpecLessBenchBasic Require Import BasicNative BasicDomain.
Import ListNotations.
Definition rec_binding := forall n, Task.factorial_rec n = BasicNative.factorial_rec n.
Definition acc_binding := forall n a, Task.factorial_acc MUTANT n a = BasicNative.factorial_acc MUTANT n a.
Definition valid_binding := forall x, Task.valid x <-> BasicDomain.valid 0 x.
Definition a_binding := forall x, Task.a x = BasicNative.entry 0 0 x.
Definition b_binding := forall x, Task.b x = BasicNative.entry 0 STYLE x.
Definition target_binding := (Task.equivalent <-> BasicNative.Equivalent (BasicDomain.valid 0) (BasicNative.entry 0 0) (BasicNative.entry 0 STYLE)) /\\
  (forall x oa ob, Task.refutationAt x oa ob <-> BasicDomain.valid 0 x /\\ BasicNative.entry 0 0 x=Some oa /\\ BasicNative.entry 0 STYLE x=Some ob /\\ oa<>ob).
'''


def compile_file(folder,name,logical):
    subprocess.run([str(COQC),'-q','-Q',str(folder),logical,str(folder/(name+'.v'))],cwd=folder,check=True,timeout=120)


def main():
    verify_freeze();mapping=json.loads((PRIVATE/'mapping.json').read_text())['contexts']
    for kind,ctx,mutant,style in [('equivalence','R-FAC-EQ','false','1'),('counterexample','R-FAC-CEX','true','2')]:
        build=BASE/('factorial-rocq-'+kind)
        if build.exists():raise SystemExit('Existing output: preserve and inspect '+str(build))
        task=build/'task';original=build/'original';binding=build/'binding'
        for d in (task,original,binding):d.mkdir(parents=True)
        (task/'Task.v').write_text(TASK.replace('MUTANT',mutant))
        goal='Task.equivalent' if kind=='equivalence' else 'Task.refutationAt [1%Z] [1%Z;1%Z] [1%Z;0%Z]'
        (task/'Obligation.v').write_text('From Coq Require Import ZArith List.\nImport ListNotations.\nFrom Trusted Require Import Task.\nDefinition goal : Prop := '+goal+'.\n')
        compile_file(task,'Task','Trusted');compile_file(task,'Obligation','Trusted')
        for name in ('BasicNative.v','BasicDomain.v'):shutil.copyfile(ORIGINAL/name,original/name)
        compile_file(original,'BasicNative','SpecLessBenchBasic');compile_file(original,'BasicDomain','SpecLessBenchBasic')
        (binding/'Spec.v').write_text(BINDING.replace('MUTANT',mutant).replace('STYLE',style))
        subprocess.run([str(COQC),'-q','-Q',str(task),'Trusted','-Q',str(original),'SpecLessBenchBasic',str(binding/'Spec.v')],cwd=binding,check=True,timeout=120)
        row=next(x for x in mapping if x['source_context_id']==ctx)
        out={'pilot_id':row['pilot_id'],'platform':'rocq','claim':kind,'purpose':'reference',
             'public_sha256':tree_digest(task),'binding_status':'pending',
             'scope':'The projected goal and original-binding propositions type-check; no final proof exists.',
             'fixed_witness':None if kind=='equivalence' else {'input':[1],'left_observation':[1,1],'right_observation':[1,0]}}
        (build/'registry.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)


if __name__=='__main__':main()
