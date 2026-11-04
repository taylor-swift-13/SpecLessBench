"""Meter definition/target checks and real Clight exports; no final proofs."""
import hashlib,json,os,shutil
from pathlib import Path
from boundaries_common import CORE,BUILD,LEAN,COQC,FIVE,GROUPS
from accounting import ROOT
from measure import measured
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ld=BUILD/"lean";ld.mkdir(parents=True,exist_ok=True);os.environ["LEAN_PATH"]=str(ld)
    for n in ("BoundaryNative","BoundaryDomain","BoundaryGoals","BoundaryRunner"):
        measured([LEAN,"-o",str(ld/(n+".olean")),str(CORE/"lean"/(n+".lean"))],"shared-boundaries","typecheck-"+n)
        print("Lean checked",n,flush=True)
    nd=BUILD/"rocq";nd.mkdir(exist_ok=True);args=["-Q",str(CORE/"rocq"),"EqualBenchBoundaryNative"]
    for n in ("BoundaryNative","BoundaryDomain","BoundaryGoals","BoundaryExtract"):
        measured([COQC,*args,str(CORE/"rocq"/(n+".v"))],"shared-boundaries-rocq","typecheck-"+n,cwd=nd)
    text=(ROOT/"scripts/construction/rocq_driver.ml").read_text().replace("NativeExtract.entry","BoundaryExtract.entry")
    text=text.replace("(match BoundaryExtract.entry family style xs with",'(if style = 99 then print_endline (if BoundaryExtract.valid_familyb family xs then "1" else "0") else match BoundaryExtract.entry family style xs with')
    driver=nd/"driver.ml";driver.write_text(text)
    for n in ("BoundaryExtract.mli","BoundaryExtract.ml"):
        measured(["ocamlopt","-I",str(nd),"-c",str(nd/n)],"shared-boundaries-rocq","compile-"+n,cwd=nd)
    measured(["ocamlopt","-I",str(nd),str(nd/"BoundaryExtract.cmx"),str(driver),"-o",str(nd/"runner")],"shared-boundaries-rocq","link-native-runner",cwd=nd)
    ast=CORE/"compcert/ast";ast.mkdir(parents=True,exist_ok=True);cc=BUILD/"compcert";cc.mkdir(exist_ok=True)
    metadata={"schema_version":1,"compcert":"3.17","rocq":"9.2","architecture":"x86_64-linux; little-endian; ptr64","clightgen_sha256":sha(Path(FIVE)/"clightgen"),"exports":[],"final_proofs":False}
    for name,gid,_,_ in GROUPS:
        for v in range(3):
            mod=name.upper()+f"_V{v}";pre=cc/(mod+".c");out=ast/(mod+".v")
            measured(["gcc","-E","-P","-std=c99",str(CORE/"c"/name/f"v{v}.c")],gid,"preprocess-for-clight",stdout_path=pre)
            measured([FIVE+"/clightgen","-clight","-normalize","-o",str(out),pre.name],gid,"export-clight",cwd=cc)
            measured([FIVE+"/coqc","-Q",str(ast),"EqualBenchBoundary.Generated",str(out)],gid,"typecheck-ast")
            metadata["exports"].append({"module":mod,"preprocessed_sha256":sha(pre),"path":out.relative_to(CORE).as_posix(),"sha256":sha(out)})
        print("Exported Clight ASTs",name,flush=True)
    for p in (CORE/"compcert").glob("*.v"):shutil.copyfile(p,cc/p.name)
    args=["-Q",str(cc),"EqualBenchBoundary","-Q",str(ast),"EqualBenchBoundary.Generated"]
    for n in ("BoundaryDomain","Execution"):
        measured([FIVE+"/coqc",*args,str(cc/(n+".v"))],"shared-boundaries-compcert","typecheck-"+n)
    for name,gid,_,_ in GROUPS:
        measured([FIVE+"/coqc",*args,str(cc/(name.upper()+"Goals.v"))],gid,"typecheck-compcert-goals")
    metadata["goal_types"]="passed; final targets unproved";metadata["native_versions"]={"lean":"4.34.0","rocq":"8.20.1"}
    (CORE/"compcert/build.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print("Checked definitions, 24 actual Clight ASTs and all pending target types; no final proofs.")
if __name__=="__main__":main()
