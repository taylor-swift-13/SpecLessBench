"""Snapshot a mutable construction group before a repair; commit its revision.

This is a curation operation. It must never be available in solver sandboxes.
"""
import argparse
import hashlib
import json
import shutil
import uuid
from pathlib import Path
from accounting import ROOT, AUDIT, now, append


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    begin = sub.add_parser("begin")
    begin.add_argument("--group", required=True)
    begin.add_argument("--reason", required=True)
    begin.add_argument("files", nargs="+")
    end = sub.add_parser("commit")
    end.add_argument("--revision-id", required=True)
    end.add_argument("--new-revision", required=True)
    end.add_argument("--affected-contexts", nargs="+", required=True)
    args = parser.parse_args()
    base = AUDIT / "repairs"
    if args.action == "begin":
        rid = uuid.uuid4().hex[:12]; folder = base / rid; folder.mkdir(parents=True)
        record = {"schema_version": 1, "revision_id": rid, "group_id": args.group,
            "started_utc": now(), "reason": args.reason, "status": "editing", "files": []}
        for i, name in enumerate(args.files):
            path = (ROOT / name).resolve()
            assert path.is_relative_to(ROOT.resolve()) and path.is_file(), path
            saved = folder / f"{i}.before"
            shutil.copyfile(path, saved)
            record["files"].append({"path": path.relative_to(ROOT).as_posix(),
                "before_sha256": digest(path), "snapshot": saved.relative_to(ROOT).as_posix()})
        (folder / "revision.json").write_text(json.dumps(record, indent=2)+"\n")
        append(AUDIT / "revisions.jsonl", record)
        print(rid)
    else:
        folder = base / args.revision_id
        assert folder.resolve().is_relative_to(base.resolve())
        record = json.loads((folder / "revision.json").read_text())
        assert record["status"] == "editing"
        for f in record["files"]:
            f["after_sha256"] = digest(ROOT / f["path"])
        record.update(status="committed-tests-invalidated", new_revision=args.new_revision,
            affected_contexts=args.affected_contexts, ended_utc=now(),
            retest_required=True, label_revalidation_required=True)
        (folder / "revision.json").write_text(json.dumps(record, indent=2)+"\n")
        append(AUDIT / "revisions.jsonl", record)
        print("Revision retained; refresh bindings and rerun all affected platforms before freezing.")


if __name__ == "__main__":
    main()
