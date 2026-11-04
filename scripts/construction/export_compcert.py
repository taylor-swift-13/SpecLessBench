"""Measured CompCert 3.17 Clight exports and target type-checks; no final proofs.

The v0.1 3.16 interface stays historical. Copies are compiled in a separate
9.2 namespace/build directory so native Rocq 8.20 artifacts are not overwritten.
"""
import hashlib
import json
import shutil
from pathlib import Path
from accounting import ROOT, AUDIT, append, now
from measure import measured

CORE = ROOT / "benchmarks/tasks/qcip-core"
BIN = Path("/home/yangfp/.opam/five/bin")
OUT = CORE / "compcert"
BUILD = ROOT / "_build/three-platform/compcert"


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ast = OUT / "ast"; ast.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    version, _ = measured([str(BIN / "clightgen"), "-version"], "shared-compcert", "version")
    assert b"3.17" in version
    c = json.loads((CORE / "tasks.json").read_text())
    record = {"schema_version": 1, "version": "3.17", "rocq_version": "9.2",
        "architecture": "x86_64-linux; ptr64; little-endian",
        "generator_sha256": sha(BIN / "clightgen"), "coqc_sha256": sha(BIN / "coqc"),
        "semantics": "Clight.step2", "options": ["-clight", "-normalize"], "exports": [],
        "final_target_proofs": False, "target_typecheck": "pending"}
    for f in c["families"]:
        gid = f["split_group_id"]
        for v in f["variants"]:
            name = v["ast_module"]
            pre = BUILD / (name+".c")
            measured(["gcc", "-E", "-P", "-std=c99", str(CORE / v["source"])], gid, "preprocess-for-clight", stdout_path=pre)
            dest = ast / (name+".v")
            measured([str(BIN / "clightgen"), "-clight", "-normalize", "-o", str(dest), pre.name], gid, "export-clight", cwd=BUILD)
            record["exports"].append({"variant": name, "group_id": gid,
                "c_entry": v["source"], "preprocessed_sha256": sha(pre),
                "ast": dest.relative_to(CORE).as_posix(), "ast_sha256": sha(dest)})
    for name in ("Domain.v", "Execution.v"):
        src = CORE / "rocq" / name
        text = src.read_text().replace("From Coq Require", "From Stdlib Require")
        if name == "Execution.v":
            text = text.replace("CompCert 3.16 interface design.", "CompCert 3.17 interface; checked with Rocq 9.2.")
            text = text.replace("Pending type-check against the locked CompCert installation and generated ASTs.",
                "Definitions only; final target proofs are intentionally deferred.")
            text = text.replace("Genv.globalenv p", "Clight.globalenv p")
        (OUT / name).write_text(text)
    for f in c["families"]:
        base = f["id"].upper()
        for suffix in ("Bindings", "Expected", "Certificates"):
            name = base+suffix+".v"
            shutil.copyfile(CORE / "rocq" / name, OUT / name)
    # Source copies in BUILD get .vo products; protected source files stay clean.
    for p in OUT.glob("*.v"): shutil.copyfile(p, BUILD / p.name)
    for p in ast.glob("*.v"): shutil.copyfile(p, BUILD / p.name)
    args = ["-Q", str(BUILD), "SpecLessBench.QCIP", "-Q", str(ast), "SpecLessBench.QCIP.Generated"]
    # ASTs are compiled in-place under the generated namespace; .vo files ignored.
    for row in record["exports"]:
        measured([str(BIN / "coqc"), "-Q", str(ast), "SpecLessBench.QCIP.Generated", str(CORE / row["ast"])],
            row["group_id"], "typecheck-clight-ast")
    for name in ("Domain", "Execution"):
        measured([str(BIN / "coqc"), *args, str(BUILD / (name+".v"))], "shared-compcert", "typecheck-"+name)
    for f in c["families"]:
        base = f["id"].upper()
        for suffix in ("Bindings", "Expected", "Certificates"):
            measured([str(BIN / "coqc"), *args, str(BUILD / (base+suffix+".v"))], f["split_group_id"], "typecheck-"+suffix)
        print("CompCert goals type-checked:", base, flush=True)
    record["target_typecheck"] = "passed; declarations end Abort; no final proof"
    record["source_registry_before_ast_sha256"] = sha(CORE / "three-platform.json")
    (OUT / "manifest.json").write_text(json.dumps(record, indent=2)+"\n")
    append(AUDIT / "revisions.jsonl", {"schema_version": 1, "timestamp_utc": now(),
        "kind": "compcert-environment-revision", "old_planned_version": "3.16", "new_version": "3.17",
        "rocq_version": "9.2", "reason": "Reuse installed toolchain; export concrete ASTs and check all goal types",
        "c_implementations_changed": False, "native_ports_changed": False,
        "manifest_sha256": sha(OUT / "manifest.json"), "task_proofs": None})
    print("16 actual ASTs and 12 CompCert context target types checked; no final theorem proved.")


if __name__ == "__main__": main()
