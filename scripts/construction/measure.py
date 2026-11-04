"""Run one construction command with persistent logs and kernel RSS accounting."""
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import time
import uuid
from pathlib import Path
from accounting import AUDIT, ROOT, event, append


def measured(cmd, group, phase, cwd=None, stdin=None, timeout=300, stdin_path=None, stdout_path=None, role="detail"):
    attempt = uuid.uuid4().hex[:12]
    logs = AUDIT / "logs" / group
    logs.mkdir(parents=True, exist_ok=True)
    out = Path(stdout_path) if stdout_path else logs / (attempt + ".stdout")
    err = logs / (attempt + ".stderr")
    metrics = logs / (attempt + ".time")
    start = dt.datetime.now(dt.timezone.utc).isoformat()
    tick = time.monotonic()
    result = None
    failure = None
    input_file = Path(stdin_path).open("rb") if stdin_path else None
    with out.open("wb") as stdout, err.open("wb") as stderr:
        try:
            result = subprocess.run(["/usr/bin/time", "-f", "%e %U %S %M", "-o", str(metrics), "--", *cmd],
                cwd=cwd or ROOT, input=stdin, stdin=input_file, stdout=stdout, stderr=stderr,
                timeout=timeout, env=dict(os.environ, LC_ALL="C", LEAN_PATH=os.environ.get("LEAN_PATH",str(ROOT / "_build/three-platform/lean"))))
        except (subprocess.TimeoutExpired, OSError) as exc:
            failure = str(exc)
    if input_file:
        input_file.close()
    elapsed = time.monotonic() - tick
    raw = metrics.read_text().splitlines()[-1].split() if metrics.exists() and metrics.stat().st_size else []
    values = [float(z) for z in raw] if len(raw) == 4 else None
    item = {"schema_version": 1, "attempt_id": attempt, "group_id": group, "phase": phase,
        "batch_id": os.environ.get("SPECLESSBENCH_CONSTRUCTION_BATCH", "three-platform-v0.2"),
        "measurement_role": role,
        "started_utc": start, "ended_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "wall_seconds": elapsed, "argv": cmd, "cwd": str(cwd or ROOT),
        "exit_code": result.returncode if result else None, "failure": failure,
        "cpu_user_seconds": values[1] if values else None,
        "cpu_system_seconds": values[2] if values else None,
        "max_process_rss_bytes": int(values[3] * 1024) if values else None,
        "rss_scope": "GNU time / wait4 ru_maxrss: maximum single-process high-water across waited descendants; NOT simultaneous tree total",
        "exact_process_tree_peak_bytes": None, "tree_peak_unavailable_reason": "No writable dedicated cgroup",
        "stdout": out.relative_to(ROOT).as_posix(), "stderr": err.relative_to(ROOT).as_posix(),
        "stdin_sha256": hashlib.sha256(stdin).hexdigest() if stdin is not None else None,
        "stdin_path": Path(stdin_path).relative_to(ROOT).as_posix() if stdin_path else None}
    append(AUDIT / "commands.jsonl", item)
    path = AUDIT / "groups" / (group + ".json")
    summary = json.loads(path.read_text()) if path.exists() else {
        "schema_version": 1, "group_id": group, "attempt_ids": [], "tool_wall_seconds": 0,
        "cpu_user_seconds": 0, "cpu_system_seconds": 0, "max_process_rss_bytes": 0,
        "exact_process_tree_peak_bytes": None, "model_tokens": None,
        "model_tokens_reason": "shared authoring session usage is recorded once in the referenced batch",
        "shared_batch_id": item["batch_id"], "historical_cost_complete": False}
    summary["attempt_ids"].append(attempt)
    summary["tool_wall_seconds"] += elapsed if role == "detail" else 0
    if role == "envelope":
        summary["envelope_attempt_ids"] = summary.get("envelope_attempt_ids", []) + [attempt]
        summary["envelope_wall_seconds"] = summary.get("envelope_wall_seconds", 0) + elapsed
        summary["cost_total_rule"] = "Use envelope totals for covered attempts; detail wall/CPU are nested attribution, never add both"
    for key in ("cpu_user_seconds", "cpu_system_seconds"):
        summary[key] += (item[key] or 0) if role == "detail" else 0
        if role == "envelope":
            summary["envelope_"+key] = summary.get("envelope_"+key, 0) + (item[key] or 0)
    summary["max_process_rss_bytes"] = max(summary["max_process_rss_bytes"], item["max_process_rss_bytes"] or 0)
    summary["failed_attempts"] = summary.get("failed_attempts", 0) + int(item["exit_code"] != 0)
    summary["latest_updated_utc"] = item["ended_utc"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2) + "\n")
    if item["exit_code"] != 0:
        append(AUDIT / "issues.jsonl", {"schema_version": 1, "id": "CMD-"+attempt,
            "timestamp_utc": item["ended_utc"], "group_id": group, "kind": "construction-command-failed",
            "phase": phase, "attempt_id": attempt, "status": "open", "failure": failure,
            "stderr": item["stderr"], "revision": os.environ.get("SPECLESSBENCH_CONSTRUCTION_REVISION", "design-v0.2")})
        raise RuntimeError(f"{group}/{phase}: command failed; see {err}")
    return (b"" if stdout_path else out.read_bytes()), item


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", required=True)
    parser.add_argument("--phase", required=True)
    parser.add_argument("--role", choices=["detail", "envelope"], default="detail")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    cmd = args.command[1:] if args.command and args.command[0] == "--" else args.command
    _, item = measured(cmd, args.group, args.phase, role=args.role, timeout=3600)
    print(json.dumps({k: item[k] for k in ("attempt_id", "wall_seconds", "max_process_rss_bytes", "exit_code")}))


if __name__ == "__main__":
    main()
