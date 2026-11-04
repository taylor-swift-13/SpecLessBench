"""Check the combined inventory and record the resolved construction failures."""
import json
import sys

from accounting import AUDIT, append, now
from measure import measured
from systems_common import BATCH, GROUPS, ROOT


def main():
    scripts = (
        "scripts/construction/regress_systems_contract.py",
        "scripts/construction/summarize_systems.py",
        "scripts/construction/summarize_all.py",
        "scripts/construction/check_three_platform.py",
        "scripts/curation/check_inventory.py",
    )
    for script in scripts:
        out, _ = measured(
            [sys.executable, str(ROOT / script)],
            "shared-systems-audit",
            script.rsplit("/", 1)[-1],
            role="envelope",
        )
        print(out.decode(), end="", flush=True)

    known = {json.loads(line)["id"] for line in (AUDIT / "issues.jsonl").read_text().splitlines()}
    repairs = (
        ("CMD-253a51bed9d3", "83eba576182e",
         "Renamed a reserved Lean identifier. The repaired definitions pass type checking and differential testing."),
        ("CMD-f8f402c980cf", "5ce4bb16dc72",
         "Corrected the generated Lean runner's reference to the renamed word reader. All five groups pass the full corpus."),
    )
    for issue, repair, description in repairs:
        assert issue in known
        if issue + "-resolution" not in known:
            append(AUDIT / "issues.jsonl", {
                "schema_version": 1,
                "id": issue + "-resolution",
                "resolves": issue,
                "timestamp_utc": now(),
                "kind": "resolution",
                "status": "resolved",
                "repair": f"benchmarks/construction/repairs/{repair}/revision.json",
                "description": description,
                "final_proofs_attempted": False,
            })
    if "SYSTEMS-NUMERICAL-HEADER-BRANCH" not in known:
        append(AUDIT / "issues.jsonl", {
            "schema_version": 1,
            "id": "SYSTEMS-NUMERICAL-HEADER-BRANCH",
            "timestamp_utc": now(),
            "group_id": "shared-systems",
            "kind": "draft-source-review",
            "status": "resolved",
            "description": "Inspection caught the numerical include inside the lease wheel declaration guard. It was moved to the family dispatch before the revised C build.",
            "affected_revision": "design-v0.6.1",
        })

    from summarize_systems import main as systems
    from summarize_all import main as aggregate

    systems()
    aggregate()

    batch_path = AUDIT / f"batch-{BATCH}.json"
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    batch.setdefault("initial_groups", batch["groups"])
    batch["groups"] = [group_id for _, group_id, _, _ in GROUPS]
    batch["status"] = "construction-audited"
    batch_path.write_text(json.dumps(batch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
