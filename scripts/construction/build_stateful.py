"""Meter definition/target checks and real Clight exports; no final proofs."""
import hashlib,json,os,shutil
from pathlib import Path
from stateful_common import CORE,BUILD,LEAN,COQC,FIVE,GROUPS
from accounting import ROOT
from measure import measured
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ld=BUILD/"lean";ld.mkdir(parents=True,exist_ok=True);os.environ["LEAN_PATH"]=str(ld)
    for n in ("StatefulNative","StatefulDomain","StatefulGoals","StatefulRunner"):
        measured([LEAN,"-o",str(ld/(n+".olean")),str(CORE/"lean"/(n+".lean"))],"shared-stateful","typecheck-"+n)
        print("Lean checked",n,flush=True)
    nd=BUILD/"rocq";nd.mkdir(exist_ok=True);args=["-Q",str(CORE/"rocq"),"SpecLessBenchStatefulNative"]
    for n in ("StatefulNative","StatefulDomain","StatefulGoals","StatefulExtract"):
        measured([COQC,*args,str(CORE/"rocq"/(n+".v"))],"shared-stateful-rocq","typecheck-"+n,cwd=nd)
    text=(ROOT/"scripts/construction/rocq_driver.ml").read_text().replace("NativeExtract.entry","StatefulExtract.entry")
    text=text.replace("(match StatefulExtract.entry family style xs with",'(if style = 99 then print_endline (if StatefulExtract.valid_familyb family xs then "1" else "0") else match StatefulExtract.entry family style xs with')
    driver=nd/"driver.ml";driver.write_text(text)
    for n in ("StatefulExtract.mli","StatefulExtract.ml"):
        measured(["ocamlopt","-I",str(nd),"-c",str(nd/n)],"shared-stateful-rocq","compile-"+n,cwd=nd)
    measured(["ocamlopt","-I",str(nd),str(nd/"StatefulExtract.cmx"),str(driver),"-o",str(nd/"runner")],"shared-stateful-rocq","link-native-runner",cwd=nd)
    ast=CORE/"compcert/ast";ast.mkdir(parents=True,exist_ok=True);cc=BUILD/"compcert";cc.mkdir(exist_ok=True)
    metadata={"schema_version":1,"compcert":"3.17","rocq":"9.2","architecture":"x86_64-linux; little-endian; ptr64","clightgen_sha256":sha(Path(FIVE)/"clightgen"),"exports":[],"final_proofs":False}
    for name,gid,_,_ in GROUPS:
        for v in range(3):
            mod=name.upper()+f"_V{v}";pre=cc/(mod+".c");out=ast/(mod+".v")
            measured(["gcc","-E","-P","-std=c99",str(CORE/"c"/name/f"v{v}.c")],gid,"preprocess-for-clight",stdout_path=pre)
            measured([FIVE+"/clightgen","-clight","-normalize","-o",str(out),pre.name],gid,"export-clight",cwd=cc)
            measured([FIVE+"/coqc","-Q",str(ast),"SpecLessBenchStateful.Generated",str(out)],gid,"typecheck-ast")
            metadata["exports"].append({"module":mod,"preprocessed_sha256":sha(pre),"path":out.relative_to(CORE).as_posix(),"sha256":sha(out)})
        print("Exported Clight ASTs",name,flush=True)
    for p in (CORE/"compcert").glob("*.v"):shutil.copyfile(p,cc/p.name)
    args=["-Q",str(cc),"SpecLessBenchStateful","-Q",str(ast),"SpecLessBenchStateful.Generated"]
    for n in ("StatefulDomain","Execution"):
        measured([FIVE+"/coqc",*args,str(cc/(n+".v"))],"shared-stateful-compcert","typecheck-"+n)
    for name,gid,_,_ in GROUPS:
        measured([FIVE+"/coqc",*args,str(cc/(name.upper()+"Goals.v"))],gid,"typecheck-compcert-goals")
    metadata["goal_types"]="passed; final targets unproved";metadata["native_versions"]={"lean":"4.34.0","rocq":"8.20.1"}
    (CORE/"compcert/build.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print("Checked definitions, 9 actual Clight ASTs and all pending target types; no final proofs.")
if __name__=="__main__":main()
