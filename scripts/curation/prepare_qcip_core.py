"""Materialize curator task bindings and freeze protected source hashes; no proofs.

Run --refresh only for an intentional task revision. Normal checks must compare
against tasks.json, never refresh it automatically.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "benchmarks/tasks/qcip-core"
FAMILIES = {
    "bst": ("BST", ["C-BST-SUCCESSOR", "C-BST-ROTATE", "C-BST-VALUE"], "qcip-bst-delete", "L3-L4", "W2"),
    "avl": ("AVL", ["C-AVL-STACK", "C-AVL-FACTOR", "C-AVL-MIDDLE"], "qcip-avl-insert", "L3-L4", "W2"),
    "ring": ("Ring", ["C-RING-COPY", "C-RING-REP", "C-RING-FULL"], "qcip-xizi-ring", "L3", "W1-W2"),
    "dijkstra": ("Dijkstra", ["C-DIJK-SCAN", "C-DIJK-HEAP", "C-DIJK-SEEN"], "qcip-dijkstra", "L4", "W2"),
}


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", required=True)
    parser.parse_args()
    manifest = {"schema_version": 1, "curator_only": True, "revision": "design-v0.1",
        "status": "source-concrete; AST export/type-check/reference certificates pending",
        "proofs_requested": False, "input_words": 8192, "output_words": 8192,
        "compcert_target_version": "3.16", "semantics": "Clight.step2; clightgen -normalize",
        "target_architecture": "x86_64-linux; must be locked and recorded at AST export",
        "families": [], "protected_files": []}
    for folder, (domain, ids, split, level, witness) in FAMILIES.items():
        variants = []
        for v in range(4):
            relative = f"{folder}/v{v}.c"
            write(CORE / relative, f'/* Fixed EqualBench implementation {folder.upper()}_V{v}. */\n#define EB_STYLE {v}\n#include "body.h"\n')
            variants.append({"id": f"{folder.upper()}_V{v}", "source": relative,
                "ast_module": f"{folder.upper()}_V{v}", "style_macro": v})
        bindings = ["(* Protected fixed program bindings. Generated ASTs are required.",
                    " * No Parameters/Axioms stand in for missing implementations. *)",
                    "From EqualBench.QCIP Require Import Domain Execution."]
        for v in variants:
            bindings.append(f'From EqualBench.QCIP.Generated Require Import {v["ast_module"]}.')
        for v in variants:
            m = v["ast_module"]
            bindings.append(f'Definition impl_{m} : implementation :=\n  {{| program := {m}.prog; input_symbol := {m}._eb_input;\n     output_symbol := {m}._eb_output |}}.')
        write(CORE / "rocq" / f"{folder.upper()}Bindings.v", "\n".join(bindings) + "\n")
        expected = ["(* Curator-only expected branch goals. Abort closes an UNPROVED",
                    " * declaration; it does not supply a certificate or an axiom. *)",
                    f"From EqualBench.QCIP Require Import Domain Execution {folder.upper()}Bindings."]
        public = ["(* Public disjunction goals. Packaging must rename variants neutrally",
                  " * and exclude curator IDs, expected branches, and witness seeds. *)",
                  f"From EqualBench.QCIP Require Import Domain Execution {folder.upper()}Bindings."]
        tasks = []
        task_levels = {"bst": ["L3", "L4", "W2"], "avl": ["L4", "L2", "W2"],
            "ring": ["L2-L3", "L3", "W1"], "dijkstra": ["L4", "L3-L4", "W2"]}[folder]
        for i, task_id in enumerate(ids, 1):
            a = f"impl_{folder.upper()}_V0"; b = f"impl_{folder.upper()}_V{i}"
            polarity = "equivalent" if i < 3 else "counterexample"
            predicate = "Equivalent" if i < 3 else "Counterexample"
            name = task_id.replace("-", "_")
            statement = f"{predicate} {domain}.valid {domain}.encode {a} {b}"
            expected += [f"Theorem {name} :\n  {statement}.\nAbort."]
            public += [f"Theorem task_{i:02d} :\n  Certificate {domain}.valid {domain}.encode {a} {b}.\nAbort."]
            tasks.append({"id": task_id, "left": variants[0]["id"], "right": variants[i]["id"],
                "expected_branch": polarity, "expected_theorem": name,
                "expected_statement": statement,
                "expected_goal_file": f"rocq/{folder.upper()}Expected.v",
                "public_goal_file": f"rocq/{folder.upper()}Certificates.v",
                "public_theorem": f"task_{i:02d}", "reference_certificate": None,
                "provisional_difficulty": task_levels[i - 1]})
        write(CORE / "rocq" / f"{folder.upper()}Expected.v", "\n\n".join(expected) + "\n")
        write(CORE / "rocq" / f"{folder.upper()}Certificates.v", "\n\n".join(public) + "\n")
        manifest["families"].append({"id": folder, "domain": domain, "split_group_id": split,
            "proof_level": level, "witness_level": witness, "variants": variants, "tasks": tasks,
            "call_closure": "all source-level callees have included bodies; generated AST audit pending"})
    for path in sorted(CORE.rglob("*")):
        if path.is_file() and path.suffix in {".h", ".c", ".v", ".txt"}:
            manifest["protected_files"].append({"path": path.relative_to(CORE).as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    write(CORE / "tasks.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print("Prepared 16 C entries, 12 expected goals and 12 disjunction goals; no proof attempted.")


if __name__ == "__main__":
    main()
