"""Check frozen three-platform assets, differential lineage and accounting.
No programs or proofs run here. Compilation evidence is checked separately.
"""
import hashlib
import json
import re
from pathlib import Path
from accounting import ROOT, AUDIT


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    core = ROOT / "benchmarks/tasks/qcip-core"
    reg = json.loads((core / "three-platform.json").read_text())
    assert reg["required_platforms"] == ["lean", "rocq", "compcert"]
    assert len(reg["groups"]) == 4
    assert sum(len(g["tasks"]) for g in reg["groups"]) == 12
    for f in reg["protected_files"]:
        assert sha(core / f["path"]) == f["sha256"], f["path"]
    cc = json.loads((core / "compcert/manifest.json").read_text())
    assert len(cc["exports"]) == 16 and cc["target_typecheck"].startswith("passed")
    assert sha(core / "compcert/manifest.json") == reg["compcert_environment"]["manifest_sha256"]
    old_c = json.loads((core / "tasks.json").read_text())
    for f in old_c["protected_files"]:
        assert sha(core / f["path"]) == f["sha256"], f["path"]
    for f in cc["exports"]:
        assert sha(core / f["ast"]) == f["ast_sha256"], f["ast"]
    count = 0
    for g in reg["groups"]:
        report = json.loads((core / "evidence" / (g["family"]+"-three-platform.json")).read_text())
        assert report["positive_disagreements"] == 0 and report["negative_distinguishing_inputs"] > 0
        assert not report["compcert_semantic_execution_tested"]
        corpus = ROOT / report["corpus"]
        assert corpus.is_file() and sha(corpus) == report["corpus_sha256"]
        # Preserve the exact earlier registry rather than rewriting old reports.
        prior_hash = report["source_registry_sha256"]
        archive = AUDIT / "registries" / (prior_hash+".json")
        assert sha(archive) == prior_hash
        prior = json.loads(archive.read_text())
        for f in prior["protected_files"]:
            assert sha(core / f["path"]) == f["sha256"], "Native program changed since differential run: "+f["path"]
        for t in g["tasks"]:
            assert set(t["proofs"].values()) == {None}
            assert (core / t["lean"]["pending_theorem"]).is_file()
        count += report["program_executions"]
    assert count == 363384
    lean = (core / "lean/Goals.lean").read_text()
    assert len(re.findall(r"^def C_", lean, re.M)) == 24
    assert not re.search(r"\b(sorry|axiom)\b", re.sub(r"--.*", "", lean))
    assert all((AUDIT / "groups" / (g["group_id"]+".json")).is_file() for g in reg["groups"])
    print("PASS: 4 groups / 12 contexts / 36 pending platform targets; 16 concrete Clight ASTs.")
    print("PASS: frozen source hashes, 363384 differential runs, corpus hashes and pre-AST registry lineage.")
    print("No final target proof checked; differential labels remain provisional; historical/hosted memory accounting gaps remain explicit.")


if __name__ == "__main__": main()
