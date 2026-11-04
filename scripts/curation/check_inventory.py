"""Check source-snapshot integrity and task-design references, without proving programs."""

import hashlib
import json
import re
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[2]
    bank = root / "benchmarks/source-material"
    imported = json.loads((bank / "import-manifest.json").read_text())
    index = json.loads((root / "benchmarks/complex-family-index.json").read_text())
    assert imported["source_file_count"] == len(imported["files"]) == 16
    for record in imported["files"] + imported["licenses"]:
        path = bank / record["destination"]
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == record["sha256"], f"Snapshot drift: {path}"

    assert len(index["families"]) == index["complex_family_entries"] == 10
    slots = []
    for family in index["families"]:
        assert len(family["slots"]) == 3, family["id"]
        slots.extend(family["slots"])
        for source in family["sources"]:
            assert (root / "benchmarks" / source).is_file(), source
    assert len(slots) == len(set(slots)) == index["complex_task_slots"] == 30

    core = root / "benchmarks/tasks/qcip-core"
    concrete = json.loads((core / "tasks.json").read_text())
    concrete_ids = [t["id"] for f in concrete["families"] for t in f["tasks"]]
    assert len(concrete_ids) == len(set(concrete_ids)) == 12
    assert set(concrete_ids) <= set(slots)
    assert all(t["reference_certificate"] is None for f in concrete["families"] for t in f["tasks"])
    for record in concrete["protected_files"]:
        actual = hashlib.sha256((core / record["path"]).read_bytes()).hexdigest()
        assert actual == record["sha256"], record["path"]
    evidence = json.loads((core / "evidence/native-check.json").read_text())
    current_manifest_sha = hashlib.sha256((core / "tasks.json").read_bytes()).hexdigest()
    if evidence["tasks_manifest_sha256"] != current_manifest_sha:
        migration=json.loads((root/"benchmarks/construction/rename-speclessbench.json").read_text())
        digest=evidence["tasks_manifest_sha256"]
        for r in migration["registry_rebindings"]:
            if r["path"]=="benchmarks/tasks/qcip-core/tasks.json" and r["before_sha256"]==digest:
                digest=r["after_sha256"]
        assert digest==current_manifest_sha

    if (root / "benchmarks/active-groups.json").exists():
        active = json.loads((root / "benchmarks/active-groups.json").read_text())
        assert len(active["groups"]) == active["implementation_groups"] == 33
        ids = [t for g in active["groups"] for t in g["contexts"]]
        assert len(ids) == len(set(ids)) == active["semantic_contexts"] == 71
        assert active["platform_instances"] == 213 and active["clight_ast_count"] == 103
        assert active["catalog_entries"] == 39 and active["catalog_context_slots"] == 93
        split={g['group_id']:g['split_group_id'] for g in active['groups']}
        assert split['boyer-moore-search']==split['first-match-search']
        assert split['all-pairs-shortest-path']==split['qcip-dijkstra']
        assert split['stable-counting-sort']==split['stable-record-sorting']
        assert hashlib.sha256((root/active['split_policy']).read_bytes()).hexdigest()==active['split_policy_sha256']
        extension=json.loads((root/"benchmarks/boundary-family-index.json").read_text())
        assert len(extension["new_entries"])==4 and sum(len(g["slots"])for g in extension["new_entries"])==8
        stateful=json.loads((root/"benchmarks/stateful-family-index.json").read_text())
        assert len(stateful["new_entries"])==3 and sum(len(g["slots"])for g in stateful["new_entries"])==6
        systems=json.loads((root/"benchmarks/systems-family-index.json").read_text())
        assert len(systems["new_entries"])==5
        assert {slot for g in systems["new_entries"] for slot in g["slots"]} == {
            context for group in active["groups"]
            if group["group_id"] in {entry["group_id"] for entry in systems["new_entries"]}
            for context in group["contexts"]
        }
        contract = root / active["proof_acceptance_contract"]
        manifest=json.loads(contract.read_text())
        assert {r["context_id"]for r in manifest["contexts"]}==set(ids)
        assert hashlib.sha256(contract.read_bytes()).hexdigest() == active["proof_acceptance_contract_sha256"]
        assert not active["bare_logical_disjunction_is_sufficient"]

    tex = (root / "paper/main.tex").read_text()
    bib = (root / "paper/references.bib").read_text()
    known_keys = set(re.findall(r"@\w+\{([^,]+),", bib))
    cited_keys = {
        key.strip() for group in re.findall(r"\\cite\w*\{([^}]+)\}", tex)
        for key in group.split(",")
    }
    assert not cited_keys - known_keys, f"Unknown citation keys: {cited_keys - known_keys}"
    environments = []
    for kind, name in re.findall(r"\\(begin|end)\{([^}]+)\}", tex):
        if kind == "begin":
            environments.append(name)
        else:
            assert environments and environments.pop() == name, f"Unbalanced environment: {name}"
    assert not environments, environments
    print(f"Source integrity: 16 C snapshots and {len(imported['licenses'])} license files match recorded SHA-256.")
    print("Design index: 10 complex entries / 30 unique slots; all indexed source snapshots exist.")
    print(f"Historical design: {index['base_family_entries'] + len(index['families'])} entries / {index['base_task_slots'] + len(slots)} slots.")
    if (root/"benchmarks/active-groups.json").exists():
        print(f"Current active: {active['implementation_groups']} groups / {active['semantic_contexts']} contexts / {active['platform_instances']} platform instances; plan {active['catalog_entries']} entries / {active['catalog_context_slots']} slots.")
    print("Concrete refinement: 4 families / 16 C entries / 12 unproved targets; native evidence matches manifest.")
    print(f"Paper references: {len(cited_keys)} citation keys resolved; LaTeX environments balanced.")
    print("These checks do not compile LaTeX or C, generate Clight, or check any proof.")


if __name__ == "__main__":
    main()
