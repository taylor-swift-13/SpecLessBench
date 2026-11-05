"""Generate explicit branch targets; bare logical disjunction is not a solve.

No program or domain is edited. This changes the future submission interface,
so existing differential evidence remains valid and all new goal types check.
"""
import hashlib
import json
from pathlib import Path
from algorithms_common import ROOT,BUILD,LEAN,COQC,FIVE,CORE
from accounting import AUDIT,append,now
from measure import measured


def write(p,text): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding="utf-8",newline="\n")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    output=ROOT/"benchmarks/proof-interface"
    lean=["import Domain", "import BasicDomain", "namespace SpecLessBenchSubmission"]
    native=["From Coq Require Import ZArith List.","From SpecLessBench.QCIP Require Import Domain.",
        "From SpecLessBenchNative Require Import Native.","From SpecLessBenchBasic Require Import BasicNative BasicDomain."]
    cc=["From Stdlib Require Import ZArith List.","From SpecLessBench.QCIP Require Import Domain Execution BSTBindings AVLBindings RINGBindings DIJKSTRABindings.",
        "From SpecLessBenchAlgorithms Require Import BasicDomain Execution FACTORIALGoals REVERSEGoals SUMGoals MATRIXGoals SEARCHGoals QUEUEGoals."]
    bindings=[]
    qcip=json.loads((ROOT/"benchmarks/tasks/qcip-core/three-platform.json").read_text())
    basics=json.loads((CORE/"groups.json").read_text())
    for g in qcip["groups"]:
        family=g["family"]; dom={"bst":"BST","avl":"AVL","ring":"Ring","dijkstra":"Dijkstra"}[family]
        for t in g["tasks"]:
            name=t["context_id"].replace("-","_"); right=t["right_variant"]
            lean_valid=f"SpecLessBench.{dom}.valid"; lean_type=f"SpecLessBench.{dom}.Input"
            la=f"(fun x => SpecLessBench.{family} 0 (SpecLessBench.{dom}.encode x))"
            lb=f"(fun x => SpecLessBench.{family} {right} (SpecLessBench.{dom}.encode x))"
            lean += [f"def {name}_equivalence : Prop := SpecLessBench.Equivalent {lean_valid} {la} {lb}",
                f"def {name}_refutationAt (x : {lean_type}) (oa ob : List Int) : Prop :=\n  {lean_valid} x ∧ {la} x = some oa ∧ {lb} x = some ob ∧ oa ≠ ob"]
            rv=f"Domain.{dom}.valid"; rt=f"Domain.{dom}.input"
            a=f"(fun x => Native.{family} 0 (Domain.{dom}.encode x))"; b=f"(fun x => Native.{family} {right} (Domain.{dom}.encode x))"
            native += [f"Definition {name}_equivalence : Prop := Native.Equivalent {rv} {a} {b}.",
                f"Definition {name}_refutationAt (x : {rt}) (oa ob : list Z) : Prop :=\n  {rv} x /\\ {a} x = Some oa /\\ {b} x = Some ob /\\ oa <> ob."]
            ex="SpecLessBench.QCIP.Execution"; cv=f"SpecLessBench.QCIP.Domain.{dom}.valid"; ct=f"SpecLessBench.QCIP.Domain.{dom}.input"
            enc=f"SpecLessBench.QCIP.Domain.{dom}.encode"; base=family.upper()
            ca=f"SpecLessBench.QCIP.{base}Bindings.impl_{base}_V0"; cb=f"SpecLessBench.QCIP.{base}Bindings.impl_{base}_V{right}"
            cc += [f"Definition {name}_equivalence : Prop := {ex}.Equivalent {cv} {enc} {ca} {cb}.",
                f"Definition {name}_refutationAt (x : {ct}) (oa ob : {ex}.observation) : Prop :=\n  {cv} x /\\ {ex}.run {ca} ({enc} x) oa /\\ {ex}.run {cb} ({enc} x) ob /\\ oa <> ob."]
            bindings.append({"context_id":t["context_id"],"group_id":g["group_id"],"family":family,"tranche":"qcip",
                "equivalence_goal":name+"_equivalence","refutation_at_goal":name+"_refutationAt"})
    for g in basics["groups"]:
        i=g["family_index"]; base=g["family"].upper()
        for t in g["tasks"]:
            name=t["id"].replace("-","_"); j=t["right"]
            la=f"SpecLessBenchBasic.entry {i} 0 x"; lb=f"SpecLessBenchBasic.entry {i} {j} x"
            lean += [f"def {name}_equivalence : Prop := SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid {i}) (SpecLessBenchBasic.entry {i} 0) (SpecLessBenchBasic.entry {i} {j})",
                f"def {name}_refutationAt (x oa ob : List Int) : Prop :=\n  SpecLessBenchBasic.valid {i} x ∧ {la} = some oa ∧ {lb} = some ob ∧ oa ≠ ob"]
            native += [f"Definition {name}_equivalence : Prop := BasicNative.Equivalent (BasicDomain.valid {i}) (BasicNative.entry {i} 0) (BasicNative.entry {i} {j}).",
                f"Definition {name}_refutationAt (x oa ob : list Z) : Prop :=\n  BasicDomain.valid {i} x /\\ BasicNative.entry {i} 0 x = Some oa /\\ BasicNative.entry {i} {j} x = Some ob /\\ oa <> ob."]
            ex="SpecLessBenchAlgorithms.Execution"; cv=f"SpecLessBenchAlgorithms.BasicDomain.valid {i}"; enc="SpecLessBenchAlgorithms.BasicDomain.encode"
            ca=f"SpecLessBenchAlgorithms.{base}Goals.impl_{base}_V0"; cb=f"SpecLessBenchAlgorithms.{base}Goals.impl_{base}_V{j}"
            cc += [f"Definition {name}_equivalence : Prop := {ex}.Equivalent ({cv}) {enc} {ca} {cb}.",
                f"Definition {name}_refutationAt (x : list Z) (oa ob : {ex}.observation) : Prop :=\n  {cv} x /\\ {ex}.run {ca} ({enc} x) oa /\\ {ex}.run {cb} ({enc} x) ob /\\ oa <> ob."]
            bindings.append({"context_id":t["id"],"group_id":g["group_id"],"family_index":i,"tranche":"algorithms",
                "equivalence_goal":name+"_equivalence","refutation_at_goal":name+"_refutationAt"})
    lean += ["end SpecLessBenchSubmission"]
    write(output/"lean/BranchTargets.lean","\n\n".join(lean)+"\n")
    write(output/"rocq/BranchTargets.v","\n\n".join(native)+"\n")
    write(output/"compcert/BranchTargets.v","\n\n".join(cc)+"\n")
    # Kernel declaration checks only, no final theorem proofs.
    measured([LEAN,"-o",str(output/"lean/BranchTargets.olean"),str(output/"lean/BranchTargets.lean")],"shared-algorithms-interface","check-lean-branch-targets")
    old=ROOT/"benchmarks/tasks/qcip-core"
    paths=["-Q",str(old/"rocq"),"SpecLessBench.QCIP","-Q",str(old/"rocq_native"),"SpecLessBenchNative",
           "-Q",str(CORE/"rocq"),"SpecLessBenchBasic"]
    measured([COQC,*paths,str(output/"rocq/BranchTargets.v")],"shared-algorithms-interface","check-rocq-branch-targets")
    ast_old=old/"compcert/ast"; ast_new=CORE/"compcert/ast"
    paths=["-Q",str(ROOT/"_build/three-platform/compcert"),"SpecLessBench.QCIP",
           "-Q",str(ast_old),"SpecLessBench.QCIP.Generated","-Q",str(BUILD/"compcert"),"SpecLessBenchAlgorithms",
           "-Q",str(ast_new),"SpecLessBenchAlgorithms.Generated"]
    measured([FIVE+"/coqc",*paths,str(output/"compcert/BranchTargets.v")],"shared-algorithms-interface","check-compcert-branch-targets")
    manifest={"schema_version":1,"version":"explicit-branch-v1","contexts":bindings,
        "accepted_modes":["equivalence","counterexample"],"bare_logical_disjunction_proof_accepted":False,
        "counterexample_requires_literal_input_and_observations":True,
        "final_target_proofs_attempted":False,"all_branch_target_types_checked":True,
        "files":[{"path":p.relative_to(output).as_posix(),"sha256":sha(p)} for p in sorted(output.rglob("*")) if p.suffix in (".lean",".v")]}
    write(output/"manifest.json",json.dumps(manifest,indent=2)+"\n")
    append(AUDIT/"issues.jsonl",{"schema_version":1,"id":"PROP-DISJUNCTION-ESCAPE","timestamp_utc":now(),
        "kind":"proof-interface-design","status":"resolved-contract-checked; kernel submission adapter still pending",
        "description":"A bare Prop Eq-or-exists-difference can be discharged nonconstructively for total functions without selecting an explicit checked outcome. It is not accepted as a solve.",
        "resolution":"Require literal submission mode; check equivalence directly or refutation specialized to JSON-literal input and concrete observations. Separate branch target types are kernel checked.",
        "programs_changed":False,"differential_rerun_required":False,"affected_context_count":24,
        "manifest_sha256":sha(output/"manifest.json"),"final_problem_proofs_attempted":False})
    print("24 contexts: separate equivalence and literal-witness refutation targets checked in all three platforms.")

if __name__=="__main__": main()
