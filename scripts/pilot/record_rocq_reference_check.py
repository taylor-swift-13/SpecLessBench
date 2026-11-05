"""Recheck a published Rocq reference and record the verification cost."""
import argparse
import hashlib
import json
import resource
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args(); report = args.report.resolve()
    if not report.is_relative_to(ROOT / 'benchmarks/reports'): raise SystemExit('Report outside reference directory')
    start = time.monotonic()
    check = subprocess.run([sys.executable, str(ROOT / 'scripts/pilot/verify_factorial_rocq_original.py'), str(report)],
                           capture_output=True, text=True, timeout=600)
    elapsed = time.monotonic() - start; child = resource.getrusage(resource.RUSAGE_CHILDREN)
    if check.returncode: raise SystemExit(check.stdout + check.stderr)
    (report / 'verification.log').write_text(check.stdout + check.stderr)
    info = {'wall_seconds': elapsed, 'child_cpu_seconds': child.ru_utime + child.ru_stime,
            'max_child_process_rss_bytes': child.ru_maxrss * 1024,
            'memory_scope': 'largest individual child-process maximum RSS, not a concurrent process-tree peak',
            'checker_sha256': hashlib.sha256((ROOT / 'scripts/pilot/verify_factorial_rocq_original.py').read_bytes()).hexdigest()}
    (report / 'verification.json').write_text(json.dumps(info, indent=2) + '\n')
    rows = [hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(report).as_posix()
            for p in sorted(report.rglob('*')) if p.is_file() and p.name != 'SHA256SUMS']
    (report / 'SHA256SUMS').write_text('\n'.join(rows) + '\n')
    print(json.dumps(info))

if __name__ == '__main__': main()
