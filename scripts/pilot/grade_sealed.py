"""Deterministic proof decision against a curator-sealed obligation package.

This is a reusable grading entry point, not a registry of certified pilot
packages. The digest and package path must be selected by the trusted caller;
they must never be supplied by the agent being graded.
"""
import argparse
import json
import shutil
import tempfile
import time
from pathlib import Path

from single_task_runner import tree_digest
from lean_grader_core import grade_prepared as grade_lean
from rocq_grader_core import grade_prepared as grade_rocq


def grade(platform, package, expected_digest, proof, timeout=90, trace=None, deadline=None):
    if platform not in ('lean', 'rocq', 'compcert'):
        return {'status': 'infrastructure-error', 'detail': 'unknown platform'}
    proof = Path(proof)
    if proof.is_symlink() or not proof.is_file() or proof.stat().st_size > 1024 * 1024:
        return {'status': 'rejected', 'detail': 'invalid submission file'}
    try:
        if tree_digest(package) != expected_digest:
            return {'status': 'infrastructure-error', 'detail': 'package digest mismatch'}
        with tempfile.TemporaryDirectory(prefix='specless-sealed-grade-') as tmp:
            root = Path(tmp); trusted = root / 'trusted'; submission = root / 'submission'
            shutil.copytree(package, trusted, symlinks=False)
            if tree_digest(trusted) != expected_digest:
                return {'status': 'infrastructure-error', 'detail': 'package changed while copying'}
            submission.mkdir()
            filename = 'Submission.lean' if platform == 'lean' else 'Submission.v'
            data = proof.read_bytes()
            if len(data) > 1024 * 1024:
                return {'status': 'rejected', 'detail': 'submission too large'}
            (submission / filename).write_bytes(data)
            if platform == 'lean':
                result = grade_lean(trusted, submission, timeout, trace, deadline=deadline)
            else:
                result = grade_rocq(platform, trusted, submission, timeout, trace, deadline=deadline)
            if deadline is not None and time.monotonic() >= deadline:
                return {'status': 'timeout', 'detail': 'Shared attempt time budget reached before checker decision',
                        'observed_result_after_deadline': result}
            return result
    except TimeoutError as error:
        if deadline is not None and time.monotonic() >= deadline:raise
        return {'status': 'infrastructure-error', 'detail': str(error)}
    except (OSError, ValueError) as error:
        return {'status': 'infrastructure-error', 'detail': str(error)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--platform', choices=('lean', 'rocq', 'compcert'), required=True)
    parser.add_argument('--package', required=True, help='trusted task-specific obligation directory')
    parser.add_argument('--package-sha256', required=True, help='digest from trusted registry')
    parser.add_argument('--proof', required=True)
    args = parser.parse_args()
    result = grade(args.platform, args.package, args.package_sha256, args.proof)
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result['status'] == 'accepted' else 1)


if __name__ == '__main__':
    main()
