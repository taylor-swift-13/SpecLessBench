"""Append-only construction events and provider-reported usage snapshots.

No token estimates. A batch owns shared usage exactly once; group records
reference it rather than multiplying shared drafting/tooling cost by task count.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "benchmarks/construction"


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def append(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def event(kind, group, **kwargs):
    item = {"schema_version": 1, "timestamp_utc": now(), "kind": kind,
            "group_id": group, **kwargs}
    append(AUDIT / "events.jsonl", item)
    return item


def usage_snapshot(session, before_latest_request=False, marker="每个任务都要有 lean 版"):
    raw = Path(session).read_bytes()
    last = None
    baseline = None
    offset = 0
    matched_session = False
    session_id = None
    request_timestamp = None
    for line in raw.splitlines(keepends=True):
        offset += len(line)
        try:
            row = json.loads(line)
        except (ValueError, UnicodeDecodeError):
            continue
        payload = row.get("payload", {})
        if row.get("type") == "session_meta":
            assert Path(payload["cwd"]).resolve() == ROOT.resolve(), "Wrong construction session"
            matched_session = True
            session_id = payload.get("id")
        if row.get("type") == "response_item" and payload.get("role") == "user":
            if marker in str(payload.get("content", "")):
                baseline = last
                request_timestamp = row.get("timestamp")
        if row.get("type") == "event_msg" and payload.get("type") == "token_count" and payload.get("info"):
            last = {"provider_timestamp": row["timestamp"],
                    "usage": payload["info"]["total_token_usage"],
                    "session_prefix_bytes": offset,
                    "session_prefix_sha256": hashlib.sha256(raw[:offset]).hexdigest()}
    assert matched_session, "Session identity not checked"
    selected = baseline if before_latest_request else last
    assert selected is not None, "No provider usage event available"
    return {"source": "local Codex rollout event_msg/token_count total_token_usage",
            "session_id": session_id, "construction_request_timestamp": request_timestamp, **selected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["start", "snapshot"])
    parser.add_argument("--session", required=True)
    parser.add_argument("--batch", default="three-platform-v0.2")
    parser.add_argument("--request-marker", default="每个任务都要有 lean 版")
    parser.add_argument("--groups", nargs="*", default=["qcip-bst-delete", "qcip-avl-insert", "qcip-xizi-ring", "qcip-dijkstra"])
    args = parser.parse_args()
    AUDIT.mkdir(parents=True, exist_ok=True)
    assert "/" not in args.batch and "\\" not in args.batch
    path = AUDIT / ("batch-"+args.batch+".json")
    if args.action == "start":
        if path.exists():
            raise SystemExit("Batch already exists; start must not reset accounting")
        batch = {"schema_version": 1, "batch_id": args.batch,
            "status": "in-progress", "started_utc": now(),
            "groups": args.groups,
            "baseline": usage_snapshot(args.session, True, args.request_marker),
            "shared_usage_allocation": "record once here; never charge it once per pair/platform",
            "historical_before_batch": {"tokens": None, "wall_seconds": None, "peak_memory_bytes": None,
                "reason": "Earlier group-level authoring/tool costs were not instrumented; no reconstruction or zero fill"},
            "hosted_model_peak_memory_bytes": None,
            "hosted_model_memory_reason": "Provider does not expose inference memory telemetry",
            "model_identity": None, "model_identity_reason": "Exact provider model identifier not exposed by this chat runtime"}
        event("batch-start", None, batch_id=batch["batch_id"])
    else:
        batch = json.loads(path.read_text(encoding="utf-8"))
    end = usage_snapshot(args.session, marker=args.request_marker)
    batch["latest_snapshot"] = end
    batch["request_started_utc"] = end["construction_request_timestamp"]
    if batch["request_started_utc"]:
        request_start = dt.datetime.fromisoformat(batch["request_started_utc"].replace("Z", "+00:00"))
        batch["elapsed_request_wall_seconds_to_snapshot"] = (dt.datetime.now(dt.timezone.utc)-request_start).total_seconds()
    batch["elapsed_wall_scope"] = "whole shared request, including model/tool/idle latency; not per-group authoring attribution"
    batch["provider_token_delta"] = {k: end["usage"][k] - batch["baseline"]["usage"][k]
                                     for k in end["usage"]}
    batch["usage_complete_through"] = end["provider_timestamp"]
    batch["usage_status"] = "prefix-only until a post-turn snapshot; final reply may not yet be counted"
    batch["reasoning_tokens_rule"] = "reasoning_output_tokens is a subset of output_tokens; do not add twice"
    path.write_text(json.dumps(batch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"batch": batch["batch_id"], "provider_token_delta": batch["provider_token_delta"],
                      "through": batch["usage_complete_through"]}))


if __name__ == "__main__":
    main()
