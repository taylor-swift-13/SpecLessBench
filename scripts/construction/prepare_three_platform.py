"""Generate native pending targets and the shared implementation-group registry.

Existing C/CompCert targets are referenced unchanged. No goal is proved.
"""
import hashlib
import json
from pathlib import Path
from accounting import AUDIT, append, now

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "benchmarks/tasks/qcip-core"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    c = json.loads((CORE / "tasks.json").read_text())
    result = {"schema_version": 2, "revision": "design-v0.2", "curator_only": True,
        "required_platforms": ["lean", "rocq", "compcert"],
        "implementation_group_count": 4, "semantic_task_contexts": 12, "platform_instances": 36,
        "final_target_proofs_required_during_construction": False,
        "group_construction_mutable": True, "solver_implementations_mutable_after_freeze": False,
        "status": "source construction; differential-tested labels are provisional, CompCert AST export pending",
        "groups": [], "protected_files": []}
    ast_manifest = CORE / "compcert/manifest.json"
    compcert = json.loads(ast_manifest.read_text()) if ast_manifest.exists() else None
    if compcert:
        result["compcert_environment"] = {"version": compcert["version"], "rocq": compcert["rocq_version"],
            "manifest": "compcert/manifest.json", "manifest_sha256": sha(ast_manifest),
            "goal_typecheck": compcert["target_typecheck"]}
        result["status"] = "three-platform sources/ASTs and target types checked; differential labels provisional; final proofs deferred; accounting gaps explicit"
    lean = ["import Domain", "namespace EqualBench", "-- Checked proposition declarations, no theorem proofs."]
    rocq = ["From EqualBench.QCIP Require Import Domain.", "From EqualBenchNative Require Import Native."]
    for i, family in enumerate(c["families"]):
        fid = family["id"]; domain = family["domain"]; algo = "dijkstra" if fid == "dijkstra" else fid
        group = {"group_id": family["split_group_id"], "family": fid, "revision": "design-v0.2",
            "cost_record": f"../../construction/groups/{family['split_group_id']}.json",
            "shared_cost_batch": "three-platform-v0.2", "variants": [], "tasks": []}
        for v in range(4):
            name = f"{fid.upper()}_V{v}"
            group["variants"].append({"id": name, "lean": f"lean/Native.lean::{algo} {v}",
                "rocq": f"rocq_native/Native.v::{algo} {v}",
                "compcert_c": family["variants"][v]["source"], "compcert_ast": f"compcert/ast/{name}.v" if compcert else None,
                "port_status": "independent executable native re-encodings; no cross-language equivalence proof",
                "style_caveat": "native trees replace pointer identity with structural nodes; predecessor/successor strategy retained; source-level call/control metrics are platform-specific"})
        for j, task in enumerate(family["tasks"], 1):
            name = task["expected_theorem"]
            predicate = "Equivalent" if j < 3 else "Counterexample"
            lean_a = f"(fun x => {algo} 0 ({domain}.encode x))"
            lean_b = f"(fun x => {algo} {j} ({domain}.encode x))"
            statement = f"{predicate} {domain}.valid {lean_a} {lean_b}"
            lean += [f"def {name} : Prop := {statement}",
                     f"def {name}_certificate : Prop := Certificate {domain}.valid {lean_a} {lean_b}"]
            goal = f"import Goals\nopen EqualBench\ntheorem solve : EqualBench.{name}_certificate := by\n  -- Pending: supply a proof here; no sorry/axiom is supplied.\n"
            p = CORE / "lean/pending" / (name+".lean.goal")
            p.parent.mkdir(parents=True, exist_ok=True); p.write_text(goal)
            a = f"(fun x => {algo} 0 ({domain}.encode x))"
            b = f"(fun x => {algo} {j} ({domain}.encode x))"
            rocq += [f"Theorem {name} : {predicate} {domain}.valid {a} {b}.\nAbort.",
                     f"Theorem {name}_certificate : Certificate {domain}.valid {a} {b}.\nAbort."]
            group["tasks"].append({"context_id": task["id"], "left_variant": 0, "right_variant": j,
                "expected_polarity": task["expected_branch"], "label_status": "provisional; not kernel certified",
                "lean": {"statement": "lean/Goals.lean::"+name, "pending_theorem": p.relative_to(CORE).as_posix()},
                "rocq": {"pending_theorem": "rocq_native/Goals.v::"+name},
                "compcert": {"pending_theorem": ("compcert/"+fid.upper()+"Expected.v" if compcert else task["expected_goal_file"])+"::"+name,
                    "ast_status": "exported and type-checked; goal type checked, unproved" if compcert else "not exported; target interface not type-checked"},
                "proofs": {"lean": None, "rocq": None, "compcert": None}})
        result["groups"].append(group)
    lean += ["end EqualBench"]
    (CORE / "lean/Goals.lean").write_text("\n".join(lean)+"\n")
    (CORE / "rocq_native/Goals.v").write_text("\n\n".join(rocq)+"\n")
    for folder in (("lean", "rocq_native", "compcert") if compcert else ("lean", "rocq_native")):
        for p in sorted((CORE / folder).rglob("*")):
            if p.is_file() and (p.suffix in (".v", ".lean", ".goal")):
                result["protected_files"].append({"path": p.relative_to(CORE).as_posix(), "sha256": sha(p)})
    path = CORE / "three-platform.json"
    previous = sha(path) if path.exists() else None
    if previous:
        archive = AUDIT / "registries" / (previous+".json")
        archive.parent.mkdir(parents=True, exist_ok=True)
        if not archive.exists():
            archive.write_bytes(path.read_bytes())
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    append(AUDIT / "revisions.jsonl", {"schema_version": 1, "timestamp_utc": now(),
        "kind": "group-set-revision", "revision": "design-v0.2", "old_registry_sha256": previous,
        "new_registry_sha256": sha(path), "reason": "Add required Lean/native Rocq versions and all pending targets; no final proofs",
        "groups": [g["group_id"] for g in result["groups"]],
        "source_hashes": result["protected_files"], "c_registry_sha256": sha(CORE / "tasks.json")})
    print("4 groups / 12 contexts / 36 platform instances registered; final proofs not requested.")


if __name__ == "__main__":
    main()
