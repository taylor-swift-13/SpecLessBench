"""Copy one private, completed theorem run into a public reference directory.

The source run remains private. This publishes the task, proof and interaction
trace, so the theorem must no longer be treated as a blind evaluation item.
"""
import argparse
import hashlib
import json
import re
import shutil
import tarfile
from pathlib import Path

from single_task_runner import tree_digest

ROOT=Path(__file__).resolve().parents[2]
OUTPUT=ROOT/'benchmarks/reports'
FILES=('report.json','report.md','config.json','codex-config.toml','environment.json','model-catalog.json','prompt.txt',
       'events.jsonl','events.timestamps.jsonl','agent.stderr','checker.log',
       'resources.json')
SECRET=re.compile(rb'(?i)(?:sk-[A-Za-z0-9_-]{20,}|bearer\s+[A-Za-z0-9._-]{20,}|"(?:access_token|refresh_token|api_key)"\s*:\s*"[^"\s]{10,}")')


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run_dir');args=parser.parse_args()
    run=Path(args.run_dir)
    if run.is_symlink() or not run.is_dir():raise SystemExit('Expected a real private run directory')
    report=json.loads((run/'report.json').read_text());cfg=report['configuration']
    task=cfg['task_id'];platform=cfg['platform'];claim=cfg['claim']
    if cfg.get('purpose')!='reference':raise SystemExit('Only reference runs may be published here')
    if cfg.get('model')!='gpt-6.1-sol':raise SystemExit('Only GPT-6.1 Sol runs may be published here')
    if not re.fullmatch(r'P-[0-9a-f]{16}',task) or platform!='lean' or claim not in ('equivalence','counterexample'):
        raise SystemExit('Unsupported task or goal')
    if not re.fullmatch(r'[0-9]{8}T[0-9]{6}Z-[0-9a-f]{12}',run.name):raise SystemExit('Invalid run id')
    names=list(FILES)
    if report.get('proof_sha256') is not None:
        names.append('Submission.lean')
    elif report.get('result',{}).get('status')=='accepted':
        raise SystemExit('An accepted run must contain a proof')
    for name in names:
        p=run/name
        if p.is_symlink() or not p.is_file():raise SystemExit('Missing or unsafe file: '+name)
        if SECRET.search(p.read_bytes()):raise SystemExit('Possible credential found in '+name+'; review privately')
    if report.get('proof_sha256') is not None and digest(run/'Submission.lean')!=report['proof_sha256']:raise SystemExit('Proof checksum mismatch')
    events=(run/'events.jsonl').read_bytes().splitlines();timestamps=(run/'events.timestamps.jsonl').read_bytes().splitlines()
    if len(events)!=len(timestamps) or len(events)!=report['transcript']['event_count']:raise SystemExit('Event/timestamp count mismatch')
    if not all(json.loads(line)['line']==i for i,line in enumerate(timestamps,1)):raise SystemExit('Timestamp ordering mismatch')
    if tree_digest(run/'private/task')!=cfg['task_package_sha256']:raise SystemExit('Task package checksum mismatch')
    out=OUTPUT/task/platform/claim/run.name
    if out.exists():raise SystemExit('Reference already exists')
    out.mkdir(parents=True)
    for name in names:shutil.copyfile(run/name,out/name)
    with tarfile.open(out/'task.tar.gz','w:gz') as tar:
        for p in sorted((run/'private/task').iterdir()):
            if p.is_symlink() or not p.is_file():raise SystemExit('Unsafe task member')
            tar.add(p,arcname=p.name,recursive=False)
    files=sorted(p for p in out.iterdir() if p.is_file())
    (out/'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in files))
    print(out)


if __name__=='__main__':main()
