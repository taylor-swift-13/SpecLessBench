"""Prepare systems-rich implementation comparisons, without final proofs."""
import hashlib
import json
from accounting import ROOT,AUDIT,append,now
from systems_common import BATCH,CORE,GROUPS,REVISION
def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')

def main():
    manifest={"schema_version":1,"revision":REVISION,"curator_only":True,
      "required_platforms":["lean","rocq","compcert"],"final_target_proofs_required":False,
      "groups":[],"protected_files":[],"c_environment_header":"../qcip-core/common/io.h"}
    lean=["import SystemsDomain","namespace SpecLessBenchSystems"]
    rocq=["From SpecLessBenchSystemsNative Require Import SystemsNative SystemsDomain."]
    write(CORE/"compcert/SystemsDomain.v",(CORE/"rocq/SystemsDomain.v").read_text().replace("From Coq Require","From Stdlib Require"))
    adapter=(ROOT/"benchmarks/tasks/qcip-core/compcert/Execution.v").read_text().replace("From SpecLessBench.QCIP Require Import Domain.","Definition OutputWords : nat := 8192%nat.")
    # The old disjunctive certificate is intentionally absent from the new interface.
    adapter=adapter[:adapter.index("Definition Certificate")]+"Definition RefutationAt {I : Type} (valid : I -> Prop) (encode : I -> list Z) (a b : implementation) (x : I) (oa ob : observation) : Prop :=\n  valid x /\\ run a (encode x) oa /\\ run b (encode x) ob /\\ oa <> ob.\n"
    write(CORE/"compcert/Execution.v",adapter)
    for i,(name,gid,contexts,level) in enumerate(GROUPS):
        g={"group_id":gid,"family":name,"family_index":i,"proof_level":level,"revision":REVISION,
           "cost_batch":BATCH,"tasks":[],"variants":[]}
        cc=["From SpecLessBenchSystems Require Import SystemsDomain Execution."]
        for v in range(3):
            module=name.upper()+f"_V{v}"; path=f"c/{name}/v{v}.c"
            write(CORE/path,f'#define EB_FAMILY {i}\n#define EB_STYLE {v}\n#include "../'+"Systems.h"+'"\n')
            g["variants"].append({"id":module,"c":path,"lean":f"SystemsNative.entry {i} {v}","rocq":f"SystemsNative.entry {i} {v}","ast":f"compcert/ast/{module}.v"})
            cc += [f"From SpecLessBenchSystems.Generated Require Import {module}.",f"Definition impl_{module} : implementation :=\n {{| program := {module}.prog; input_symbol := {module}._eb_input; output_symbol := {module}._eb_output |}}."]
        for tid,right,domain in contexts:
            t=tid.replace("-","_"); la=f"(entry {i} 0)";lb=f"(entry {i} {right})"
            lean += [f"def {t}_equivalence : Prop := Equivalent (valid {domain}) {la} {lb}",f"def {t}_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid {domain}) {la} {lb} x oa ob"]
            rocq += [f"Definition {t}_equivalence : Prop := SystemsNative.Equivalent (SystemsDomain.valid {domain}) (SystemsNative.entry {i} 0) (SystemsNative.entry {i} {right}).",f"Definition {t}_refutationAt (x oa ob : SystemsNative.words) : Prop := SystemsNative.RefutationAt (SystemsDomain.valid {domain}) (SystemsNative.entry {i} 0) (SystemsNative.entry {i} {right}) x oa ob."]
            a=f"impl_{name.upper()}_V0";b=f"impl_{name.upper()}_V{right}"
            cc += [f"Definition {t}_equivalence : Prop := Equivalent (SystemsDomain.valid {domain}) SystemsDomain.encode {a} {b}.",f"Definition {t}_refutationAt (x : SystemsDomain.words) (oa ob : observation) : Prop := RefutationAt (SystemsDomain.valid {domain}) SystemsDomain.encode {a} {b} x oa ob."]
            pending=f"lean/pending/{t}.lean.goal"
            write(CORE/pending,f"import SystemsGoals\nopen SpecLessBenchSystems\n-- Select equivalence or literal-witness refutation using the submission contract.\n-- Pending universal branch (no final proof supplied):\ntheorem solve : {t}_equivalence := by\n")
            g["tasks"].append({"id":tid,"left":0,"right":right,"domain_index":domain,"expected_polarity":"EQ" if right==1 else "CEX","label_status":"provisional; not proved","theorem":t,"lean_goal":pending,"rocq_goal":"rocq/SystemsGoals.v::"+t,"compcert_goal":f"compcert/{name.upper()}Goals.v::"+t,"final_proofs":{"lean":None,"rocq":None,"compcert":None}})
        write(CORE/f"compcert/{name.upper()}Goals.v","\n\n".join(cc)+"\n")
        manifest["groups"].append(g)
    write(CORE/"lean/SystemsGoals.lean","\n".join(lean+["end SpecLessBenchSystems"])+"\n")
    write(CORE/"rocq/SystemsGoals.v","\n\n".join(rocq)+"\n")
    runner=(ROOT/"benchmarks/tasks/algorithms-core/lean/BasicRunner.lean").read_text().replace("BasicDomain","SystemsDomain").replace("SpecLessBenchBasic","SpecLessBenchSystems").replace(".validB family",".validFamilyB family").replace(".iz fields", ".word fields")
    write(CORE/"lean/SystemsRunner.lean",runner)
    write(CORE/"rocq/SystemsExtract.v",'From Coq Require Import Extraction ExtrOcamlBasic ExtrOcamlNatInt ExtrOcamlZInt.\nFrom SpecLessBenchSystemsNative Require Import SystemsNative SystemsDomain.\nExtraction Language OCaml.\nExtraction "SystemsExtract.ml" SystemsNative.entry SystemsDomain.valid_familyb.\n')
    for folder in ("c","lean","rocq","compcert"):
        for p in sorted((CORE/folder).rglob("*")):
            if p.is_file() and p.suffix in (".h",".c",".v",".lean",".goal"):
                manifest["protected_files"].append({"path":p.relative_to(CORE).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
    manifest["io_header_sha256"]=hashlib.sha256((ROOT/"benchmarks/tasks/qcip-core/common/io.h").read_bytes()).hexdigest()
    dest=CORE/"groups.json";old=hashlib.sha256(dest.read_bytes()).hexdigest() if dest.exists() else None
    if old:
        archive=AUDIT/"registries"/(old+".json");archive.parent.mkdir(parents=True,exist_ok=True);archive.write_bytes(dest.read_bytes())
    write(dest,json.dumps(manifest,indent=2)+"\n")
    append(AUDIT/"revisions.jsonl",{"schema_version":1,"timestamp_utc":now(),"kind":"systems-tranche-revision","old_registry_sha256":old,"new_registry_sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),"groups":[g[1] for g in GROUPS],"reason":"Graph, scoped bindings, leases, alignment and resampling with fixed observation boundaries"})
    print(f"Prepared {len(GROUPS)} groups, {2*len(GROUPS)} contexts and {6*len(GROUPS)} platform instances.")
if __name__=="__main__":main()
