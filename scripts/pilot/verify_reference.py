"""Verify a published reference report and recheck its proof locally."""
import argparse
import hashlib
import json
import subprocess
import tarfile
import tempfile
from pathlib import Path

from grade_sealed import grade
from single_task_runner import tree_digest


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('reference');args=parser.parse_args()
    root=Path(args.reference)
    if root.is_symlink() or not root.is_dir():raise SystemExit('Invalid reference directory')
    expected={}
    for line in (root/'SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1)
        if Path(name).name!=name or name in expected:raise SystemExit('Unsafe or duplicate manifest entry')
        expected[name]=digest
    actual={p.name for p in root.iterdir() if p.is_file() and p.name!='SHA256SUMS'}
    if set(expected)!=actual:raise SystemExit('Reference file list differs from manifest')
    for name,digest in expected.items():
        p=root/name
        if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise SystemExit('Checksum mismatch: '+name)
    report=json.loads((root/'report.json').read_text());events=(root/'events.jsonl').read_text().splitlines()
    if hashlib.sha256((root/'Submission.lean').read_bytes()).hexdigest()!=report['proof_sha256']:
        raise SystemExit('Proof does not match report')
    commit=report['benchmark_commit']
    if not isinstance(commit,str) or len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit):
        raise SystemExit('Invalid recorded commit')
    runner=subprocess.check_output(['git','show',commit+':scripts/pilot/run_codex_wsl.py'])
    if hashlib.sha256(runner).hexdigest()!=report['configuration']['runner_sha256']:
        raise SystemExit('Recorded runner does not match commit')
    times=[json.loads(x) for x in (root/'events.timestamps.jsonl').read_text().splitlines()]
    if len(events)!=report['transcript']['event_count'] or [x['line'] for x in times]!=list(range(1,len(events)+1)):
        raise SystemExit('Event timestamps do not match report')
    with tempfile.TemporaryDirectory(prefix='specless-reference-') as temp:
        package=Path(temp)
        with tarfile.open(root/'task.tar.gz','r:gz') as tar:
            members=tar.getmembers()
            if {m.name for m in members}!={'Task.lean','Task.olean','Obligation.lean','Obligation.olean'} or not all(m.isfile() for m in members):
                raise SystemExit('Unexpected task archive members')
            for member in members:(package/member.name).write_bytes(tar.extractfile(member).read())
        expected_task=report['configuration']['task_package_sha256']
        if tree_digest(package)!=expected_task:raise SystemExit('Task package hash mismatch')
        result=grade('lean',package,expected_task,root/'Submission.lean')
        if result['status']!=report['result']['status'] or result['status']!='accepted':raise SystemExit('Proof replay failed: '+json.dumps(result))
    print('Reference checksums, event timestamps, task package and Lean proof check passed.')


if __name__=='__main__':main()
