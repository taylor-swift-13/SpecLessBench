"""Prepare stateful-rich implementation comparisons, without final proofs."""
import hashlib
import json
from accounting import ROOT,AUDIT,append,now
from stateful_common import CORE,GROUPS
def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')

def main():
    manifest={"schema_version":1,"revision":"design-v0.5.1","curator_only":True,
      "required_platforms":["lean","rocq","compcert"],"final_target_proofs_required":False,
      "groups":[],"protected_files":[],"c_environment_header":"../qcip-core/common/io.h"}
    lean=["import StatefulDomain","namespace EqualBenchStateful"]
    rocq=["From EqualBenchStatefulNative Require Import StatefulNative StatefulDomain."]
    write(CORE/"compcert/StatefulDomain.v",(CORE/"rocq/StatefulDomain.v").read_text().replace("From Coq Require","From Stdlib Require"))
    adapter=(ROOT/"benchmarks/tasks/qcip-core/compcert/Execution.v").read_text().replace("From EqualBench.QCIP Require Import Domain.","Definition OutputWords : nat := 8192%nat.")
    # The old disjunctive certificate is intentionally absent from the new interface.
    adapter=adapter[:adapter.index("Definition Certificate")]+"Definition RefutationAt {I : Type} (valid : I -> Prop) (encode : I -> list Z) (a b : implementation) (x : I) (oa ob : observation) : Prop :=\n  valid x /\\ run a (encode x) oa /\\ run b (encode x) ob /\\ oa <> ob.\n"
    write(CORE/"compcert/Execution.v",adapter)
    for i,(name,gid,contexts,level) in enumerate(GROUPS):
        g={"group_id":gid,"family":name,"family_index":i,"proof_level":level,"revision":"design-v0.5.1",
           "cost_batch":"stateful-v0.5","tasks":[],"variants":[]}
        cc=["From EqualBenchStateful Require Import StatefulDomain Execution."]
        for v in range(3):
            module=name.upper()+f"_V{v}"; path=f"c/{name}/v{v}.c"
            write(CORE/path,f'#define EB_FAMILY {i}\n#define EB_STYLE {v}\n#include "../'+"Stateful.h"+'"\n')
            g["variants"].append({"id":module,"c":path,"lean":f"StatefulNative.entry {i} {v}","rocq":f"StatefulNative.entry {i} {v}","ast":f"compcert/ast/{module}.v"})
            cc += [f"From EqualBenchStateful.Generated Require Import {module}.",f"Definition impl_{module} : implementation :=\n {{| program := {module}.prog; input_symbol := {module}._eb_input; output_symbol := {module}._eb_output |}}."]
        for tid,right,domain in contexts:
            t=tid.replace("-","_"); la=f"(entry {i} 0)";lb=f"(entry {i} {right})"
            lean += [f"def {t}_equivalence : Prop := Equivalent (valid {domain}) {la} {lb}",f"def {t}_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid {domain}) {la} {lb} x oa ob"]
            rocq += [f"Definition {t}_equivalence : Prop := StatefulNative.Equivalent (StatefulDomain.valid {domain}) (StatefulNative.entry {i} 0) (StatefulNative.entry {i} {right}).",f"Definition {t}_refutationAt (x oa ob : StatefulNative.words) : Prop := StatefulNative.RefutationAt (StatefulDomain.valid {domain}) (StatefulNative.entry {i} 0) (StatefulNative.entry {i} {right}) x oa ob."]
            a=f"impl_{name.upper()}_V0";b=f"impl_{name.upper()}_V{right}"
            cc += [f"Definition {t}_equivalence : Prop := Equivalent (StatefulDomain.valid {domain}) StatefulDomain.encode {a} {b}.",f"Definition {t}_refutationAt (x : StatefulDomain.words) (oa ob : observation) : Prop := RefutationAt (StatefulDomain.valid {domain}) StatefulDomain.encode {a} {b} x oa ob."]
            pending=f"lean/pending/{t}.lean.goal"
            write(CORE/pending,f"import StatefulGoals\nopen EqualBenchStateful\n-- Select equivalence or literal-witness refutation using the submission contract.\n-- Pending universal branch (no final proof supplied):\ntheorem solve : {t}_equivalence := by\n")
            g["tasks"].append({"id":tid,"left":0,"right":right,"domain_index":domain,"expected_polarity":"EQ" if right==1 else "CEX","label_status":"provisional; not proved","theorem":t,"lean_goal":pending,"rocq_goal":"rocq/StatefulGoals.v::"+t,"compcert_goal":f"compcert/{name.upper()}Goals.v::"+t,"final_proofs":{"lean":None,"rocq":None,"compcert":None}})
        write(CORE/f"compcert/{name.upper()}Goals.v","\n\n".join(cc)+"\n")
        manifest["groups"].append(g)
    write(CORE/"lean/StatefulGoals.lean","\n".join(lean+["end EqualBenchStateful"])+"\n")
    write(CORE/"rocq/StatefulGoals.v","\n\n".join(rocq)+"\n")
    runner=(ROOT/"benchmarks/tasks/algorithms-core/lean/BasicRunner.lean").read_text().replace("BasicDomain","StatefulDomain").replace("EqualBenchBasic","EqualBenchStateful").replace(".validB family",".validFamilyB family")
    write(CORE/"lean/StatefulRunner.lean",runner)
    write(CORE/"rocq/StatefulExtract.v",'From Coq Require Import Extraction ExtrOcamlBasic ExtrOcamlNatInt ExtrOcamlZInt.\nFrom EqualBenchStatefulNative Require Import StatefulNative StatefulDomain.\nExtraction Language OCaml.\nExtraction "StatefulExtract.ml" StatefulNative.entry StatefulDomain.valid_familyb.\n')
    for folder in ("c","lean","rocq","compcert"):
        for p in sorted((CORE/folder).rglob("*")):
            if p.is_file() and p.suffix in (".h",".c",".v",".lean",".goal"):
                manifest["protected_files"].append({"path":p.relative_to(CORE).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
    manifest["io_header_sha256"]=hashlib.sha256((ROOT/"benchmarks/tasks/qcip-core/common/io.h").read_bytes()).hexdigest()
    dest=CORE/"groups.json";old=hashlib.sha256(dest.read_bytes()).hexdigest() if dest.exists() else None
    if old:
        archive=AUDIT/"registries"/(old+".json");archive.parent.mkdir(parents=True,exist_ok=True);archive.write_bytes(dest.read_bytes())
    write(dest,json.dumps(manifest,indent=2)+"\n")
    append(AUDIT/"revisions.jsonl",{"schema_version":1,"timestamp_utc":now(),"kind":"stateful-tranche-revision","old_registry_sha256":old,"new_registry_sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),"groups":[g[1] for g in GROUPS],"reason":"Three implementation groups; stateful and error semantics retained in admitted input domain; final proofs deferred"})
    print("Prepared 3 groups, 6 contexts, 18 platform instances; no final proofs.")
if __name__=="__main__":main()
