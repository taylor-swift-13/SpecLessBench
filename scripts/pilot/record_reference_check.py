"""Record a separately timed, source-level replay of a reference theorem."""
import argparse
import datetime as dt
import hashlib
import json
import subprocess
import tempfile
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CHECKER=ROOT/'scripts/pilot/verify_reference.py'


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('reference');args=parser.parse_args()
    ref=Path(args.reference).resolve();base=(ROOT/'benchmarks/reports').resolve()
    if not ref.is_relative_to(base) or not ref.is_dir():raise SystemExit('Invalid reference directory')
    if (ref/'verification.json').exists() or (ref/'verification.log').exists():raise SystemExit('Verification evidence already exists')
    start=dt.datetime.now(dt.timezone.utc).isoformat();t=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='reference-timing-') as tmp:
        timing=Path(tmp)/'time'
        result=subprocess.run(['/usr/bin/time','-f','%e %U %S %M','-o',str(timing),'python3',str(CHECKER),str(ref)],
                              cwd=ROOT,text=True,capture_output=True,timeout=600)
        elapsed=time.monotonic()-t
        if result.returncode:raise SystemExit('Replay failed:\n'+result.stdout+result.stderr)
        fields=timing.read_text().split()
        if len(fields)!=4:raise SystemExit('Missing timing evidence')
        log=result.stdout+result.stderr
        (ref/'verification.log').write_text(log,encoding='utf-8')
        info={'schema_version':1,'started_utc':start,'ended_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
              'status':'passed','checker_sha256':hashlib.sha256(CHECKER.read_bytes()).hexdigest(),
              'wall_seconds':elapsed,'tool_cpu_seconds':float(fields[1])+float(fields[2]),
              'max_process_rss_bytes':int(fields[3])*1024,
              'memory_scope':'GNU time maximum single-process RSS, not aggregate process-tree peak',
              'scope':'source rebuild, frozen target and binding axioms, original theorem bridge and submitted proof'}
        (ref/'verification.json').write_text(json.dumps(info,indent=2)+'\n',encoding='utf-8')
    files=sorted(p for p in ref.iterdir() if p.is_file() and p.name!='SHA256SUMS')
    (ref/'SHA256SUMS').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in files))
    print(json.dumps(info,sort_keys=True))


if __name__=='__main__':main()
