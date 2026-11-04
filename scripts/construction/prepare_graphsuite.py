"""Prepare graphsuite-rich implementation comparisons, without final proofs."""
import hashlib
import json
from accounting import ROOT,AUDIT,append,now
from graphsuite_common import BATCH,CORE,GROUPS,REVISION
def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')

def main():
    manifest={"schema_version":1,"revision":REVISION,"curator_only":True,
      "required_platforms":["lean","rocq","compcert"],"final_target_proofs_required":False,
      "groups":[],"protected_files":[],"c_environment_header":"../qcip-core/common/io.h"}
    lean=["import GraphSuiteDomain","namespace SpecLessBenchGraphSuite"]
    rocq=["From SpecLessBenchGraphSuiteNative Require Import GraphSuiteNative GraphSuiteDomain."]
    write(CORE/"compcert/GraphSuiteDomain.v",(CORE/"rocq/GraphSuiteDomain.v").read_text().replace("From Coq Require","From Stdlib Require"))
    adapter=(ROOT/"benchmarks/tasks/qcip-core/compcert/Execution.v").read_text().replace("From SpecLessBench.QCIP Require Import Domain.","Definition OutputWords : nat := 8192%nat.")
    # The old disjunctive certificate is intentionally absent from the new interface.
    adapter=adapter[:adapter.index("Definition Certificate")]+"Definition RefutationAt {I : Type} (valid : I -> Prop) (encode : I -> list Z) (a b : implementation) (x : I) (oa ob : observation) : Prop :=\n  valid x /\\ run a (encode x) oa /\\ run b (encode x) ob /\\ oa <> ob.\n"
    write(CORE/"compcert/Execution.v",adapter)
    for i,(name,gid,contexts,level) in enumerate(GROUPS):
        g={"group_id":gid,"family":name,"family_index":i,"proof_level":level,"revision":REVISION,
           "cost_batch":BATCH,"split_group_id":"first-match-search" if name=="search" else gid,"tasks":[],"variants":[]}
        cc=["From SpecLessBenchGraphSuite Require Import GraphSuiteDomain Execution."]
        for v in range(3):
            module=name.upper()+f"_V{v}"; path=f"c/{name}/v{v}.c"
            write(CORE/path,f'#define EB_FAMILY {i}\n#define EB_STYLE {v}\n#include "../'+"GraphSuite.h"+'"\n')
            g["variants"].append({"id":module,"c":path,"lean":f"GraphSuiteNative.entry {i} {v}","rocq":f"GraphSuiteNative.entry {i} {v}","ast":f"compcert/ast/{module}.v"})
            cc += [f"From SpecLessBenchGraphSuite.Generated Require Import {module}.",f"Definition impl_{module} : implementation :=\n {{| program := {module}.prog; input_symbol := {module}._eb_input; output_symbol := {module}._eb_output |}}."]
        for tid,right,domain in contexts:
            t=tid.replace("-","_"); la=f"(entry {i} 0)";lb=f"(entry {i} {right})"
            lean += [f"def {t}_equivalence : Prop := Equivalent (valid {domain}) {la} {lb}",f"def {t}_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid {domain}) {la} {lb} x oa ob"]
            rocq += [f"Definition {t}_equivalence : Prop := GraphSuiteNative.Equivalent (GraphSuiteDomain.valid {domain}) (GraphSuiteNative.entry {i} 0) (GraphSuiteNative.entry {i} {right}).",f"Definition {t}_refutationAt (x oa ob : GraphSuiteNative.words) : Prop := GraphSuiteNative.RefutationAt (GraphSuiteDomain.valid {domain}) (GraphSuiteNative.entry {i} 0) (GraphSuiteNative.entry {i} {right}) x oa ob."]
            a=f"impl_{name.upper()}_V0";b=f"impl_{name.upper()}_V{right}"
            cc += [f"Definition {t}_equivalence : Prop := Equivalent (GraphSuiteDomain.valid {domain}) GraphSuiteDomain.encode {a} {b}.",f"Definition {t}_refutationAt (x : GraphSuiteDomain.words) (oa ob : observation) : Prop := RefutationAt (GraphSuiteDomain.valid {domain}) GraphSuiteDomain.encode {a} {b} x oa ob."]
            pending=f"lean/pending/{t}.lean.goal"
            write(CORE/pending,f"import GraphSuiteGoals\nopen SpecLessBenchGraphSuite\n-- Select equivalence or literal-witness refutation using the submission contract.\n-- Pending universal branch (no final proof supplied):\ntheorem solve : {t}_equivalence := by\n")
            g["tasks"].append({"id":tid,"left":0,"right":right,"domain_index":domain,"expected_polarity":"EQ" if right==1 else "CEX","label_status":"provisional; not proved","theorem":t,"lean_goal":pending,"rocq_goal":"rocq/GraphSuiteGoals.v::"+t,"compcert_goal":f"compcert/{name.upper()}Goals.v::"+t,"final_proofs":{"lean":None,"rocq":None,"compcert":None}})
        write(CORE/f"compcert/{name.upper()}Goals.v","\n\n".join(cc)+"\n")
        manifest["groups"].append(g)
    write(CORE/"lean/GraphSuiteGoals.lean","\n".join(lean+["end SpecLessBenchGraphSuite"])+"\n")
    write(CORE/"rocq/GraphSuiteGoals.v","\n\n".join(rocq)+"\n")
    runner=(ROOT/"benchmarks/tasks/algorithms-core/lean/BasicRunner.lean").read_text().replace("BasicDomain","GraphSuiteDomain").replace("SpecLessBenchBasic","SpecLessBenchGraphSuite").replace(".validB family",".validFamilyB family").replace(".iz fields", ".word fields")
    write(CORE/"lean/GraphSuiteRunner.lean",runner)
    write(CORE/"rocq/GraphSuiteExtract.v",'From Coq Require Import Extraction ExtrOcamlBasic ExtrOcamlNatInt ExtrOcamlZInt.\nFrom SpecLessBenchGraphSuiteNative Require Import GraphSuiteNative GraphSuiteDomain.\nExtraction Language OCaml.\nExtraction "GraphSuiteExtract.ml" GraphSuiteNative.entry GraphSuiteDomain.valid_familyb.\n')
    for folder in ("c","lean","rocq","compcert"):
        for p in sorted((CORE/folder).rglob("*")):
            if p.is_file() and p.suffix in (".h",".c",".v",".lean",".goal"):
                manifest["protected_files"].append({"path":p.relative_to(CORE).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
    manifest["io_header_sha256"]=hashlib.sha256((ROOT/"benchmarks/tasks/qcip-core/common/io.h").read_bytes()).hexdigest()
    dest=CORE/"groups.json";old=hashlib.sha256(dest.read_bytes()).hexdigest() if dest.exists() else None
    if old:
        archive=AUDIT/"registries"/(old+".json");archive.parent.mkdir(parents=True,exist_ok=True);archive.write_bytes(dest.read_bytes())
    write(dest,json.dumps(manifest,indent=2)+"\n")
    append(AUDIT/"revisions.jsonl",{"schema_version":1,"timestamp_utc":now(),"kind":"graphsuite-tranche-revision","old_registry_sha256":old,"new_registry_sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),"groups":[g[1] for g in GROUPS],"reason":"All-pairs distances, strongly connected components and substring search with fixed observation boundaries"})
    contexts=sum(len(group[2]) for group in GROUPS)
    print(f"Prepared {len(GROUPS)} groups, {contexts} contexts and {3*contexts} platform instances.")
if __name__=="__main__":main()
