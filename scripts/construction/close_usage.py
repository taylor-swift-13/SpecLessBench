"""One-shot local collector: close this request's usage after its final message.

Stops after five minutes. Never includes a later user request's usage. A missing
post-final provider event stays explicitly incomplete instead of being guessed.
"""
import argparse
import ctypes
import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path
from accounting import AUDIT, ROOT, now


def windows_peak_working_set():
    if sys.platform != "win32": return None
    class Counters(ctypes.Structure):
        _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong)] + [
            (name, ctypes.c_size_t) for name in ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
            "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]
    counters = Counters(); counters.cb = ctypes.sizeof(counters)
    handle = ctypes.windll.kernel32.GetCurrentProcess()
    ctypes.windll.psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(Counters), ctypes.c_ulong]
    ok = ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb)
    return counters.PeakWorkingSetSize if ok else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", required=True)
    args = parser.parse_args()
    path = AUDIT / "batch-three-platform-v0.2.json"
    batch = json.loads(path.read_text(encoding="utf-8"))
    request = batch["request_started_utc"]
    start = time.monotonic(); deadline = start+300; final = None; selected = None
    while time.monotonic() < deadline:
        for line in Path(args.session).read_text(encoding="utf-8").splitlines():
            try: e = json.loads(line)
            except ValueError: continue
            stamp = e.get("timestamp", ""); p = e.get("payload", {})
            if stamp < request: continue
            if e.get("type") == "response_item" and p.get("role") == "assistant" and p.get("phase") == "final":
                final = stamp
            if final and e.get("type") == "response_item" and p.get("role") == "user":
                break
            if final and stamp >= final and e.get("type") == "event_msg" and p.get("type") == "token_count" and p.get("info"):
                selected = {"provider_timestamp": stamp, "usage": p["info"]["total_token_usage"]}
                break
        if selected: break
        time.sleep(2)
    batch = json.loads(path.read_text(encoding="utf-8"))
    if selected:
        batch["latest_snapshot"] = {"source": "post-final provider token_count event, stopped before next request", **selected}
        batch["provider_token_delta"] = {k: v-batch["baseline"]["usage"][k] for k, v in selected["usage"].items()}
        batch["usage_complete_through"] = selected["provider_timestamp"]
        batch["usage_status"] = "post-final provider usage captured for this request"
    else:
        batch["usage_status"] = "incomplete: no unambiguous post-final provider usage before collector deadline/next request"
    batch["status"] = "construction-recorded; final target proofs deferred; historical accounting gaps remain"
    batch["collector"] = {"finished_utc": now(), "wall_seconds": time.monotonic()-start,
        "cpu_seconds": time.process_time(), "peak_working_set_bytes": windows_peak_working_set(),
        "memory_scope": "Windows collector process kernel peak working set; not inference or WSL tree memory",
        "final_message_observed_utc": final}
    path.write_text(json.dumps(batch, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(batch["usage_status"])


if __name__ == "__main__": main()
