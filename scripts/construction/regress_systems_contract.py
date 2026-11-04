"""Exercise all saved literal witness packages through the extended validator."""
import json

from accounting import ROOT
from submission_contract import validate


def main():
    batches = ("algorithms-v0.3", "boundaries-v0.4", "stateful-v0.5", "systems-v0.6")
    seen = set()
    for batch in batches:
        work = ROOT / "_build" / batch / "contract-checks"
        for path in work.rglob("submission.json"):
            request = json.loads(path.read_text())
            validate(request)
            seen.add((request["context_id"], request["platform"]))
    evidence = json.loads((ROOT / "benchmarks/proof-interface/v1/validation.json").read_text())
    assert len(seen) == evidence["valid_counterexample_packages"] == 66
    print("66 saved literal packages accepted by the extended validator.")


if __name__ == "__main__":
    main()
