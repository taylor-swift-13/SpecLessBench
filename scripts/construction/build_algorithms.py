"""Build native definitions and goal types; export/type-check all Clight ASTs."""
import hashlib
import json
import os
import shutil
from pathlib import Path
from algorithms_common import CORE, BUILD, LEAN, COQC, FIVE, GROUPS
from accounting import ROOT, AUDIT, append, now
from measure import measured


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    lean_dir = BUILD / "lean"; lean_dir.mkdir(parents=True, exist_ok=True)
    os.environ["LEAN_PATH"] = str(lean_dir)
    # measure adds the earlier library path too; expose the basic modules there.
    prior_lib = ROOT / "_build/three-platform/lean"
    for name in ("BasicNative", "BasicDomain", "BasicGoals", "BasicRunner"):
        measured([LEAN, "-o", str(lean_dir/(name+".olean")), str(CORE/"lean"/(name+".lean"))],
                 "shared-algorithms", "typecheck-"+name)
        shutil.copyfile(lean_dir/(name+".olean"), prior_lib/(name+".olean"))
        print("Lean definitions/goal types:",name,flush=True)
    native = BUILD / "rocq"; native.mkdir(exist_ok=True)
    paths = ["-Q",str(CORE/"rocq"),"SpecLessBenchBasic"]
    for name in ("BasicNative", "BasicDomain", "BasicGoals", "BasicExtract"):
        measured([COQC,*paths,str(CORE/"rocq"/(name+".v"))],"shared-algorithms-rocq","typecheck-"+name,cwd=native)
    driver = native/"driver.ml"
    text = (ROOT/"scripts/construction/rocq_driver.ml").read_text().replace("NativeExtract.entry","BasicExtract.entry")
    text = text.replace("(match BasicExtract.entry family style xs with", '(if style = 99 then print_endline (if BasicExtract.validb family xs then "1" else "0") else match BasicExtract.entry family style xs with')
    driver.write_text(text)
    for name in ("BasicExtract.mli","BasicExtract.ml"):
        measured(["ocamlopt","-I",str(native),"-c",str(native/name)],"shared-algorithms-rocq","compile-"+name,cwd=native)
    measured(["ocamlopt","-I",str(native),str(native/"BasicExtract.cmx"),str(driver),"-o",str(native/"runner")],
             "shared-algorithms-rocq","link-native-runner",cwd=native)
    ast = CORE/"compcert/ast"; ast.mkdir(parents=True,exist_ok=True)
    cc = BUILD/"compcert"; cc.mkdir(exist_ok=True)
    metadata = {"schema_version":1,"compcert":"3.17","rocq":"9.2","architecture":"x86_64-linux; little-endian; ptr64",
        "clightgen_sha256":sha(Path(FIVE)/"clightgen"),"exports":[],"final_proofs":False}
    for name,gid,_,_,_ in GROUPS:
        for v in range(3):
            module=name.upper()+f"_V{v}"; pre=cc/(module+".c"); out=ast/(module+".v")
            measured(["gcc","-E","-P","-std=c99",str(CORE/"c"/name/f"v{v}.c")],gid,"preprocess-for-clight",stdout_path=pre)
            measured([FIVE+"/clightgen","-clight","-normalize","-o",str(out),pre.name],gid,"export-clight",cwd=cc)
            measured([FIVE+"/coqc","-Q",str(ast),"SpecLessBenchAlgorithms.Generated",str(out)],gid,"typecheck-ast")
            metadata["exports"].append({"module":module,"preprocessed_sha256":sha(pre),"path":out.relative_to(CORE).as_posix(),"sha256":sha(out)})
        print("Exported Clight ASTs:",name,flush=True)
    for p in (CORE/"compcert").glob("*.v"): shutil.copyfile(p,cc/p.name)
    args=["-Q",str(cc),"SpecLessBenchAlgorithms","-Q",str(ast),"SpecLessBenchAlgorithms.Generated"]
    for name in ("BasicDomain","Execution"):
        measured([FIVE+"/coqc",*args,str(cc/(name+".v"))],"shared-algorithms-compcert","typecheck-"+name)
    for name,gid,_,_,_ in GROUPS:
        measured([FIVE+"/coqc",*args,str(cc/(name.upper()+"Goals.v"))],gid,"typecheck-compcert-goals")
    metadata["goal_types"]="passed; final targets unproved"
    metadata["native_versions"]={"lean":"4.34.0","rocq":"8.20.1"}
    (CORE/"compcert/build.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print("All native/CompCert definitions, 18 ASTs and 36 pending target types checked; no final proofs.")


if __name__=="__main__": main()
