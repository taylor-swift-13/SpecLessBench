"""Freeze concrete definitions and pending targets for six base families."""
import hashlib
import json
from pathlib import Path
from accounting import AUDIT, append, now, ROOT
from algorithms_common import CORE, GROUPS


def write(p, s):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8", newline="\n")


def main():
    manifest = {"schema_version": 1, "revision": "design-v0.3.1", "curator_only": True,
        "required_platforms": ["lean", "rocq", "compcert"], "final_target_proofs_required": False,
        "groups": [], "protected_files": [], "c_environment_header": "../qcip-core/common/io.h"}
    lean = ["import BasicDomain", "namespace SpecLessBenchBasic"]
    rocq = ["From SpecLessBenchBasic Require Import BasicNative BasicDomain."]
    compcert_domain = (CORE / "rocq/BasicDomain.v").read_text().replace("From Coq Require", "From Stdlib Require")
    write(CORE / "compcert/BasicDomain.v", compcert_domain)
    adapter = (ROOT / "benchmarks/tasks/qcip-core/compcert/Execution.v").read_text()
    adapter = adapter.replace("From SpecLessBench.QCIP Require Import Domain.", "Definition OutputWords : nat := 8192%nat.")
    write(CORE / "compcert/Execution.v", adapter)
    for i, (name,gid,prefix,level,witness) in enumerate(GROUPS):
        g = {"group_id": gid, "family": name, "family_index": i, "catalog_entry": prefix,
            "proof_level": level, "witness_level": witness, "revision": "design-v0.3.1",
            "cost_batch": "algorithms-v0.3", "tasks": [], "variants": []}
        for v in range(3):
            path = f"c/{name}/v{v}.c"
            write(CORE / path, f'#define EB_FAMILY {i}\n#define EB_STYLE {v}\n#include "../Algorithms.h"\n')
            g["variants"].append({"id": f"{name.upper()}_V{v}", "c": path,
                "lean": f"BasicNative.entry {i} {v}", "rocq": f"BasicNative.entry {i} {v}",
                "ast": f"compcert/ast/{name.upper()}_V{v}.v"})
        cc = ["From SpecLessBenchAlgorithms Require Import BasicDomain Execution."]
        for v in range(3):
            module = f"{name.upper()}_V{v}"
            cc.append(f"From SpecLessBenchAlgorithms.Generated Require Import {module}.")
            cc.append(f"Definition impl_{module} : implementation :=\n  {{| program := {module}.prog; input_symbol := {module}._eb_input; output_symbol := {module}._eb_output |}}.")
        for j, polarity in ((1, "EQ"), (2, "CEX")):
            task_id = prefix+"-"+polarity; theorem = task_id.replace("-", "_")
            predicate = "Equivalent" if j == 1 else "Counterexample"
            la = f"(entry {i} 0)"; lb = f"(entry {i} {j})"
            lean += [f"def {theorem} : Prop := {predicate} (valid {i}) {la} {lb}",
                f"def {theorem}_certificate : Prop := Certificate (valid {i}) {la} {lb}"]
            pending = f"lean/pending/{theorem}.lean.goal"
            write(CORE / pending, f"import BasicGoals\nopen SpecLessBenchBasic\ntheorem solve : {theorem}_certificate := by\n  -- pending final certificate; no proof supplied\n")
            rocq += [f"Theorem {theorem} : BasicNative.{predicate} (BasicDomain.valid {i}) (BasicNative.entry {i} 0) (BasicNative.entry {i} {j}).\nAbort.",
                f"Theorem {theorem}_certificate : BasicNative.Certificate (BasicDomain.valid {i}) (BasicNative.entry {i} 0) (BasicNative.entry {i} {j}).\nAbort."]
            a=f"impl_{name.upper()}_V0"; b=f"impl_{name.upper()}_V{j}"
            cc += [f"Theorem {theorem} : {predicate} (BasicDomain.valid {i}) BasicDomain.encode {a} {b}.\nAbort.",
                f"Theorem {theorem}_certificate : Certificate (BasicDomain.valid {i}) BasicDomain.encode {a} {b}.\nAbort."]
            g["tasks"].append({"id": task_id, "left": 0, "right": j, "expected_polarity": polarity,
                "label_status": "provisional; not proved", "theorem": theorem,
                "lean_goal": pending, "rocq_goal": "rocq/BasicGoals.v::"+theorem,
                "compcert_goal": f"compcert/{name.upper()}Goals.v::"+theorem,
                "final_proofs": {"lean": None, "rocq": None, "compcert": None}})
        write(CORE / f"compcert/{name.upper()}Goals.v", "\n\n".join(cc)+"\n")
        manifest["groups"].append(g)
    lean += ["end SpecLessBenchBasic"]
    write(CORE / "lean/BasicGoals.lean", "\n".join(lean)+"\n")
    write(CORE / "rocq/BasicGoals.v", "\n\n".join(rocq)+"\n")
    write(CORE / "rocq/BasicExtract.v", 'From Coq Require Import Extraction ExtrOcamlBasic ExtrOcamlNatInt ExtrOcamlZInt.\nFrom SpecLessBenchBasic Require Import BasicNative BasicDomain.\nExtraction Language OCaml.\nExtraction "BasicExtract.ml" BasicNative.entry BasicDomain.validb.\n')
    for folder in ("c", "lean", "rocq", "compcert"):
        for p in sorted((CORE / folder).rglob("*")):
            if p.is_file() and p.suffix in (".h", ".c", ".v", ".lean", ".goal"):
                manifest["protected_files"].append({"path": p.relative_to(CORE).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    header = ROOT / "benchmarks/tasks/qcip-core/common/io.h"
    manifest["io_header_sha256"] = hashlib.sha256(header.read_bytes()).hexdigest()
    dest = CORE / "groups.json"
    old = hashlib.sha256(dest.read_bytes()).hexdigest() if dest.exists() else None
    if old:
        archive = AUDIT / "registries" / (old+".json"); archive.parent.mkdir(exist_ok=True, parents=True)
        archive.write_bytes(dest.read_bytes())
    write(dest, json.dumps(manifest, indent=2)+"\n")
    append(AUDIT / "revisions.jsonl", {"schema_version": 1, "timestamp_utc": now(), "kind": "algorithm-tranche-revision",
        "revision": "design-v0.3.1", "old_registry_sha256": old, "new_registry_sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
        "groups": [g["group_id"] for g in manifest["groups"]], "source_hashes": manifest["protected_files"],
        "reason": "Materialize six existing candidate entries, all three platforms; final proofs deferred"})
    print("Six algorithm groups, twelve contexts and thirty-six platform instances prepared.")


if __name__ == "__main__": main()
