"""Validate a literal claim and render branch-specific protected obligations.

This renders a kernel gate, not a complete isolated grader. No final theorem is
proved here. A proof of a bare Eq-or-Cex proposition is not an accepted target.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from accounting import ROOT


def literal_data(x):
    if type(x) is int: return True
    if isinstance(x,list): return all(literal_data(v) for v in x)
    if isinstance(x,dict): return all(type(k) is str and literal_data(v) for k,v in x.items())
    return False


def rows_of_ints(value,width):
    return isinstance(value,list) and all(isinstance(row,list) and len(row)==width and all(type(v) is int for v in row) for row in value)


def qcip_shape(family,x):
    if not isinstance(x,dict): return False
    if family=="bst": return rows_of_ints(x.get("initial"),2) and rows_of_ints(x.get("commands"),2)
    if family=="avl": return rows_of_ints(x.get("commands"),3)
    if family=="dijkstra": return type(x.get("vertices")) is int and type(x.get("start")) is int and rows_of_ints(x.get("edges"),3)
    if type(x.get("capacity")) is not int or not isinstance(x.get("commands"),list): return False
    return all(isinstance(cmd,list) and len(cmd)==2 and type(cmd[0]) is int and
        (type(cmd[1]) is int if cmd[0]==1 else isinstance(cmd[1],list) and all(type(b) is int for b in cmd[1])) for cmd in x["commands"])


def validate(request):
    manifest=json.loads((ROOT/"benchmarks/proof-interface/v1/manifest.json").read_text())
    if not isinstance(request,dict): raise ValueError("Submission must be a JSON object")
    base={"context_id","platform","claim","proof_module","proof_theorem"}
    if request.get("claim") not in ("equivalence","counterexample"): raise ValueError("Choose a literal branch; disjunction/conditional claims are rejected")
    extra={"input","left_observation","right_observation"} if request["claim"]=="counterexample" else set()
    if set(request)!=base|extra: raise ValueError("Missing/extra fields for the selected branch")
    if request["platform"] not in ("lean","rocq","compcert"): raise ValueError("Unknown platform")
    if not all(type(request[k]) is str and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*",request[k]) for k in ("proof_module","proof_theorem")):
        raise ValueError("Proof identifiers must be plain module/constant names")
    matches=[r for r in manifest["contexts"] if r["context_id"]==request["context_id"]]
    if len(matches)!=1: raise ValueError("Unknown context")
    context=matches[0]
    if extra:
        x=request["input"]
        if not literal_data(x): raise ValueError("Counterexample input must be first-order JSON integer data, not a program/choice term")
        if context["tranche"]=="algorithms":
            from differential_algorithms import valid
            admitted=isinstance(x,list) and all(type(v) is int for v in x) and valid(context["family_index"],x)
        elif context["tranche"]=="boundaries":
            from boundary_cases import valid_domain
            admitted=isinstance(x,list) and all(type(v) is int for v in x) and valid_domain(context["domain_index"],x)
        elif context["tranche"]=="stateful":
            from stateful_cases import valid_domain
            admitted=isinstance(x,list) and all(type(v) is int for v in x) and valid_domain(context["domain_index"],x)
        elif context["tranche"]=="systems":
            from systems_cases import valid_domain
            admitted=isinstance(x,list) and all(type(v) is int for v in x) and valid_domain(context["domain_index"],x)
        elif context["tranche"]=="base64":
            from base64_cases import valid_domain
            admitted=isinstance(x,list) and all(type(v) is int for v in x) and valid_domain(context["domain_index"],x)
        elif context["tranche"]=="classics":
            from classics_cases import valid_domain
            admitted=isinstance(x,list) and all(type(v) is int for v in x) and valid_domain(context["domain_index"],x)
        elif context["tranche"]=="graphsuite":
            from graphsuite_cases import valid_domain
            admitted=isinstance(x,list) and all(type(v) is int for v in x) and valid_domain(context["domain_index"],x)
        else:
            sys.path.insert(0,str(ROOT/"scripts/curation"))
            from check_qcip_core import valid
            fields={"bst":{"initial","commands"},"avl":{"commands"},"ring":{"capacity","commands"},"dijkstra":{"vertices","start","edges"}}
            admitted=isinstance(x,dict) and set(x)==fields[context["family"]] and qcip_shape(context["family"],x) and valid(context["family"],x)
        if not admitted: raise ValueError("Counterexample outside frozen input domain")
        for key in ("left_observation","right_observation"):
            o=request[key]
            if not isinstance(o,dict) or set(o)!={"return","payload"} or type(o["return"]) is not int or o["return"]!=0:
                raise ValueError("Observation must contain literal main return 0 and payload")
            if not isinstance(o["payload"],list) or len(o["payload"])>8191 or not all(type(v) is int and -(2**31)<=v<2**31 for v in o["payload"]):
                raise ValueError("Observation payload must be a bounded literal integer list")
        if request["left_observation"]==request["right_observation"]: raise ValueError("Counterexample observations are identical")
    return context


def seq(values,lean=False): return "["+(" , " if lean else "; ").join(str(v) if v>=0 else f"({v})" for v in values)+"]"


def input_term(context,x,lean):
    if context["tranche"] in ("algorithms","boundaries","stateful","systems","base64","classics","graphsuite"): return seq(x,lean)
    f=context["family"]; ns="SpecLessBench." if lean else "SpecLessBench.QCIP.Domain."
    dom={"bst":"BST","avl":"AVL","ring":"Ring","dijkstra":"Dijkstra"}[f]
    def listing(items): return "["+(" , " if lean else "; ").join(items)+"]"
    def ctor(name,*args): return "("+ns+dom+(".Command." if lean else ".")+name+" "+" ".join((str(a) if a>=0 else f"({a})") if type(a) is int else a for a in args)+")"
    if f=="bst":
        initial=listing([f"({k},{v})" for k,v in x["initial"]])
        commands=listing([ctor(("delete" if op==0 else "lookup") if lean else ("Delete" if op==0 else "Lookup"),k) for op,k in x["commands"]])
        fields={"initial":initial,"commands":commands}
    elif f=="avl":
        fields={"commands":listing([ctor(("insert" if op==0 else "lookup") if lean else ("Insert" if op==0 else "Lookup"),*([k,v] if op==0 else [k])) for op,k,v in x["commands"]])}
    elif f=="ring":
        labels=("write","read","force") if lean else ("Write","Read","Force")
        fields={"capacity":str(x["capacity"]),"commands":listing([ctor(labels[op],arg if op==1 else seq(arg,lean)) for op,arg in x["commands"]])}
    else:
        edges=[]
        for a,b,w in x["edges"]:
            if lean: edges.append(f"{{ source := {a}, destination := {b}, weight := {w} }}")
            else: edges.append(f"{{| {ns}{dom}.source := {a}; {ns}{dom}.destination := {b}; {ns}{dom}.weight := {w} |}}")
        fields={"vertices":str(x["vertices"]),"start":str(x["start"]),"edges":listing(edges)}
    if lean: return "{ "+", ".join(k+" := "+v for k,v in fields.items())+" }"
    return "{| "+"; ".join(ns+dom+"."+k+" := "+v for k,v in fields.items())+" |}"


def render(request,folder):
    context=validate(request); lean=request["platform"]=="lean"
    target=context["equivalence_goal"] if request["claim"]=="equivalence" else context["refutation_at_goal"]
    goal_module=context.get("goal_module","BranchTargets")
    expression=(context.get("lean_namespace","SpecLessBenchSubmission")+"." if lean else goal_module+".")+target
    if request["claim"]=="counterexample":
        expression+=" ("+input_term(context,request["input"],lean)+")"
        for key in ("left_observation","right_observation"):
            obs=request[key]; payload=obs["payload"]; prefix=seq([len(payload),*payload],lean)
            if request["platform"]=="compcert":
                term=f"(0%Z, ({prefix} ++ repeat 0%Z {8191-len(payload)}%nat))"
            else: term=prefix
            expression+=" ("+term+")"
    folder=Path(folder).resolve()
    if not folder.is_relative_to(ROOT.resolve()): raise ValueError("Output must stay in workspace")
    folder.mkdir(parents=True,exist_ok=True)
    proof=request["proof_module"]+"."+request["proof_theorem"]
    if lean:
        obligation=f"import {goal_module}\nnamespace SpecLessBenchObligation\ndef goal : Prop := "+expression+"\nend SpecLessBenchObligation\n"
        gate=f"import Obligation\nimport {request['proof_module']}\nexample : SpecLessBenchObligation.goal := {proof}\n"
        suffix="lean"
    else:
        imports="From "+("Stdlib" if request["platform"]=="compcert" else "Coq")+" Require Import ZArith List.\nRequire Import "+goal_module+".\nImport ListNotations.\nOpen Scope Z_scope.\n"
        obligation=imports+"Definition goal : Prop := "+expression+".\n"
        gate=f"Require Import Obligation {request['proof_module']}.\nDefinition checked_submission : Obligation.goal := {proof}.\n"
        suffix="v"
    (folder/("Obligation."+suffix)).write_text(obligation)
    (folder/("Gate."+suffix)).write_text(gate)
    (folder/"submission.json").write_text(json.dumps(request,indent=2)+"\n")
    return folder/("Obligation."+suffix)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request"); parser.add_argument("--output",required=True)
    args=parser.parse_args(); print(render(json.loads(Path(args.request).read_text()),args.output))

if __name__=="__main__": main()
