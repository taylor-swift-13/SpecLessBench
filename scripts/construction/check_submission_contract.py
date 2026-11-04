"""Check literal claim validation and kernel type-check generated obligations.
No Submission module or Gate is proved or accepted during construction.
"""
import copy
import json
import os
from algorithms_common import ROOT,BUILD,CORE,LEAN,COQC,FIVE
from submission_contract import validate,render
from measure import measured


def main():
    old=ROOT/"benchmarks/tasks/qcip-core"
    seeds=json.loads((old/"curator-witnesses.json").read_text())
    observed=json.loads((old/"evidence/native-check.json").read_text())["witnesses"]
    samples=[]
    ids={"bst":"C-BST-VALUE","avl":"C-AVL-MIDDLE","ring":"C-RING-FULL","dijkstra":"C-DIJK-SEEN"}
    for family,context in ids.items():
        samples.append((context,seeds[family]["input"],observed[family]["reference_output"],observed[family]["mutant_output"]))
    for family,context in (("sum","R-SUM-CEX"),("search","R-STR-CEX")):
        report=json.loads((CORE/"evidence"/(family+".json")).read_text())["witness"]
        samples.append((context,report["input"],report["v0"],report["v2"]))
    contracts=ROOT/"benchmarks/proof-interface/v1"
    work=BUILD/"contract-checks"; work.mkdir(parents=True,exist_ok=True)
    counts={"valid_counterexample_packages":0,"rejected_malformed_packages":0,"unproved_obligations_checked":0}
    for platform in ("lean","rocq","compcert"):
        texts=[]
        for i,(context,x,left,right) in enumerate(samples):
            request={"context_id":context,"platform":platform,"claim":"counterexample","proof_module":"Submission","proof_theorem":"solve",
                "input":x,"left_observation":{"return":0,"payload":left[1:]},"right_observation":{"return":0,"payload":right[1:]}}
            validate(request); counts["valid_counterexample_packages"]+=1
            path=render(request,work/platform/context)
            text=path.read_text()
            if platform=="lean": text=text.replace("import BranchTargets\n","").replace("SpecLessBenchObligation",f"ContractCheck{i}")
            else: text=text.replace("Definition goal :",f"Definition goal_{i} :")
            texts.append(text)
            for mutation in ("bare-disjunction","nonliteral-witness","identical-observations","extra-field","invalid-identifier","wrong-container"):
                bad=copy.deepcopy(request)
                if mutation=="bare-disjunction": bad["claim"]="disjunction"
                elif mutation=="nonliteral-witness": bad["input"]="Classical.choice arbitraryInput"
                elif mutation=="identical-observations": bad["right_observation"]=bad["left_observation"]
                elif mutation=="extra-field": bad["arbitrary_target"]="Certificate"
                elif mutation=="invalid-identifier": bad["proof_module"]="Submission; admit"
                else:
                    if isinstance(bad["input"],list): bad["input"]=[[0]]
                    elif "initial" in bad["input"]: bad["input"]["initial"]={}
                    elif "commands" in bad["input"]: bad["input"]["commands"]={}
                    else: bad["input"]["edges"]={}
                try: validate(bad)
                except ValueError: counts["rejected_malformed_packages"]+=1
                else: raise AssertionError("Malformed submission accepted: "+mutation)
        suffix="lean" if platform=="lean" else "v"
        source=work/("ContractChecks_"+platform+"."+suffix)
        source.write_text(("import BranchTargets\n" if platform=="lean" else "")+"\n".join(texts))
        if platform=="lean":
            os.environ["LEAN_PATH"]=str(ROOT/"_build/three-platform/lean")+":"+str(contracts/"lean")
            measured([LEAN,str(source)],"shared-algorithms-interface","validate-literal-lean-obligations")
        elif platform=="rocq":
            args=["-Q",str(old/"rocq"),"SpecLessBench.QCIP","-Q",str(old/"rocq_native"),"SpecLessBenchNative",
                  "-Q",str(CORE/"rocq"),"SpecLessBenchBasic","-Q",str(contracts/"rocq"),""]
            measured([COQC,*args,str(source)],"shared-algorithms-interface","validate-literal-rocq-obligations")
        else:
            args=["-Q",str(ROOT/"_build/three-platform/compcert"),"SpecLessBench.QCIP",
                  "-Q",str(old/"compcert/ast"),"SpecLessBench.QCIP.Generated","-Q",str(BUILD/"compcert"),"SpecLessBenchAlgorithms",
                  "-Q",str(CORE/"compcert/ast"),"SpecLessBenchAlgorithms.Generated","-Q",str(contracts/"compcert"),""]
            measured([FIVE+"/coqc",*args,str(source)],"shared-algorithms-interface","validate-literal-compcert-obligations")
        counts["unproved_obligations_checked"]+=len(samples)
    counts.update(final_target_proofs_attempted=False,gate_proofs_supplied=False,
                  scope="validator and generated obligation types; solver isolation, proof-axiom auditing and full grading still pending")
    (contracts/"validation.json").write_text(json.dumps(counts,indent=2)+"\n")
    print(json.dumps(counts))

if __name__=="__main__": main()
