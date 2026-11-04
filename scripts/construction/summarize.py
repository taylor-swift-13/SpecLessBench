"""Materialize group-once construction results, issues and nonduplicated costs."""
import hashlib
import json
from pathlib import Path
from accounting import ROOT, AUDIT, now, append


def rows(p):
    return [json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []


def main():
    core = ROOT / "benchmarks/tasks/qcip-core"
    registry = json.loads((core / "three-platform.json").read_text())
    issues = rows(AUDIT / "issues.jsonl")
    existing = {x["id"] for x in issues}
    fixes = {
        "CMD-41e1d50cb05d": "Lean reserved names at/have renamed getOr/occupied; checked Native/Domain/Goals and differential tests passed",
        "CMD-b53748093185": "Rocq mutant argument explicitly typed bool; definition and target types checked",
        "CMD-f3494cc1b7c6": "Rocq write_at arguments explicitly typed words; definition and target types checked",
        "CMD-faec1d22a24d": "Clight.step2 needs Clight.globalenv p, not Genv.globalenv p; repair 61c3c7170831 retained before/after hashes; 16 ASTs and all targets rechecked",
    }
    for problem, resolution in fixes.items():
        if problem+"-resolution" not in existing:
            append(AUDIT / "issues.jsonl", {"schema_version": 1, "timestamp_utc": now(),
                "id": problem+"-resolution", "resolves": problem, "kind": "resolution", "status": "resolved",
                "resolution": resolution, "evidence": "benchmarks/construction/commands.jsonl",
                "before_source_hash": None,
                "before_hash_reason": "First unregistered authoring draft was not snapshotted; gap disclosed, not reconstructed",
                "after_native_lean_sha256": hashlib.sha256((core / "lean/Native.lean").read_bytes()).hexdigest(),
                "after_native_rocq_sha256": hashlib.sha256((core / "rocq_native/Native.v").read_bytes()).hexdigest()})
    manual = [
        ("ACCOUNTING-INITIAL-FORMAT", "resolved", "Initial usage reader assumed event_msg/user_message; desktop logs use response_item role=user. Corrected and provider baseline recovered."),
        ("ELAN-DEFAULT-DOWNLOAD", "resolved", "Default elan launcher attempted a 4.35 download; cancelled and pinned installed 4.34.0 binary. Initial discovery wall/RSS were not metered."),
        ("MANUSCRIPT-PATCH-CONTEXT", "resolved", "A multi-paragraph patch failed atomically on citation-order context. Replaced with checked paragraph-prefix rewrite; failed attempt retained in batch tokens; tool RSS unavailable."),
        ("HISTORICAL-TELEMETRY-GAP", "open-known-limitation", "Historical per-group authoring token/time/RSS, initial discovery process costs and hosted inference memory are unavailable. No zero-fill or estimates."),
    ]
    for key, status, text in manual:
        if key not in existing:
            append(AUDIT / "issues.jsonl", {"schema_version": 1, "timestamp_utc": now(), "id": key,
                "group_id": None, "kind": "construction-process-issue", "status": status, "description": text,
                "unmetered_memory_bytes": None, "cost_source": "provider usage in batch; subprocess metrics unavailable for this initial/tool-level event"})
    commands = rows(AUDIT / "commands.jsonl")
    groups = []
    for group in registry["groups"]:
        gid = group["group_id"]; family = group["family"]
        report = json.loads((core / "evidence" / (family+"-three-platform.json")).read_text())
        cost_path = AUDIT / "groups" / (gid+".json")
        cost = json.loads(cost_path.read_text())
        cost["one_record_per_implementation_group"] = True
        cost["pair_contexts"] = 3; cost["platform_instances"] = 9
        cost["case_count"] = report["case_count"]; cost["program_executions"] = report["program_executions"]
        # Command details enclosed by a whole-group envelope are nested costs.
        owned = [x for x in commands if x["group_id"] == gid]
        envs = [x for x in owned if x.get("measurement_role") == "envelope"]
        uncovered = [x for x in owned if x.get("measurement_role") != "envelope" and not any(
            e["started_utc"] <= x["started_utc"] and x["ended_utc"] <= e["ended_utc"] for e in envs)]
        cost["nonduplicated_tool_wall_seconds"] = sum(x["wall_seconds"] for x in envs+uncovered)
        cost["uncovered_detail_attempt_ids"] = [x["attempt_id"] for x in uncovered]
        cost["exact_process_tree_peak_bytes"] = None
        cost["accounting_completeness"] = "local commands measured; historical authoring, shared token attribution and hosted model memory incomplete"
        cost_path.write_text(json.dumps(cost, indent=2)+"\n")
        groups.append({"group_id": gid, "family": family, "case_count": report["case_count"],
            "program_executions": report["program_executions"], "negative_inputs": report["negative_distinguishing_inputs"],
            "unexpected_differences": report["positive_disagreements"],
            "tool_wall_seconds": cost["nonduplicated_tool_wall_seconds"],
            "max_process_rss_bytes": cost["max_process_rss_bytes"],
            "exact_tree_peak_bytes": None, "model_tokens": None,
            "cost_file": cost_path.relative_to(ROOT).as_posix()})
    shared = [x for x in commands if x["group_id"].startswith("shared")
              and x.get("batch_id", "three-platform-v0.2") == "three-platform-v0.2"]
    summary = {"schema_version": 1, "revision": "design-v0.2", "updated_utc": now(),
        "implementation_groups": 4, "semantic_contexts": 12, "platform_instances": 36,
        "groups": groups, "total_family_inputs": sum(g["case_count"] for g in groups),
        "total_program_executions": sum(g["program_executions"] for g in groups),
        "unexpected_differences": sum(g["unexpected_differences"] for g in groups),
        "shared_tool_wall_seconds": sum(x["wall_seconds"] for x in shared),
        "shared_max_process_rss_bytes": max((x["max_process_rss_bytes"] or 0 for x in shared), default=None),
        "token_cost_source": "batch-three-platform-v0.2.json; shared usage counted once",
        "compcert": json.loads((core / "compcert/manifest.json").read_text()) if (core / "compcert/manifest.json").exists() else {"status": "pending"},
        "proofs_of_final_targets_attempted": False, "labels_certified": False,
        "all_historical_costs_known": False, "exact_concurrent_tree_memory_known": False}
    (AUDIT / "summary-qcip-v0.2.json").write_text(json.dumps(summary, indent=2)+"\n")
    if (AUDIT / "summary-algorithms-v0.3.json").exists():
        from summarize_all import main as combine_batches
        combine_batches()
    else:
        (AUDIT / "summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    print(json.dumps({k: summary[k] for k in ("implementation_groups", "platform_instances", "total_family_inputs", "total_program_executions", "unexpected_differences")}))


if __name__ == "__main__": main()
