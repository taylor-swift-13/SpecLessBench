"""Run one agent attempt with only one sealed task mounted.

Package preparation is trusted: callers must supply a *task-specific* tree,
not a shared corpus. The expected digest must come from a trusted registry,
never from a file supplied by the agent. This module does not create packages.
"""
import hashlib
import shutil
import tempfile
from pathlib import Path

from sandbox import run_isolated


def tree_digest(directory):
    root = Path(directory)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('task package must be a real directory')
    files = sorted(root.rglob('*'))
    h = hashlib.sha256(b'SpecLessBench single-task package v1\0')
    for path in files:
        if path.is_symlink() or not (path.is_dir() or path.is_file()):
            raise ValueError('links and special files are forbidden')
        name = path.relative_to(root).as_posix().encode('utf-8')
        if path.is_file():
            h.update(len(name).to_bytes(8, 'big'))
            h.update(name)
            data = path.read_bytes()
            h.update(len(data).to_bytes(8, 'big'))
            h.update(data)
    return h.hexdigest()


def run_attempt(platform, package, expected_digest, argv, output_name, timeout=120, capture_limit_bytes=1000000, raw_output=False, phase='synthetic-prototype'):
    """Run argv inside a fresh sandbox; return only the declared proof file.

    The process sees the frozen task at /trusted, a fresh writable /work,
    toolchain/system libraries, and an empty /submission. No host workspace,
    previous attempt, network, or private registry is mounted.
    """
    if output_name not in ('Submission.lean', 'Submission.v'):
        raise ValueError('invalid proof filename')
    if (platform == 'lean') != (output_name == 'Submission.lean'):
        raise ValueError('proof filename does not match platform')
    if not isinstance(expected_digest, str) or len(expected_digest) != 64:
        raise ValueError('invalid trusted digest')
    if tree_digest(package) != expected_digest:
        raise ValueError('task package digest mismatch')
    with tempfile.TemporaryDirectory(prefix='specless-attempt-') as tmp:
        root = Path(tmp)
        task = root / 'task'
        empty = root / 'empty'
        shutil.copytree(package, task, symlinks=False)
        empty.mkdir()
        if tree_digest(task) != expected_digest:
            raise ValueError('task changed while copying')
        try:
            result = run_isolated(platform, task, empty, argv, timeout=timeout,
                                  collect=[output_name],capture_limit_bytes=capture_limit_bytes,raw_output=raw_output,require_artifacts=False,phase=phase)
        except ValueError as error:
            if str(error) != 'Missing or unsafe output artifact':
                raise
            return {'status': 'invalid-output', 'exit_code': None, 'proof': None}
        # Do not pass the agent process logs back to the grader as evidence.
        return {'status': 'invalid-output' if result.get('missing_artifacts') else result['status'], 'exit_code': result['exit_code'],
                'proof': result.get('artifacts', {}).get(output_name),
                'stdout': result.get('stdout', ''), 'stderr': result.get('stderr', ''),
                'resources': result.get('resources'), 'output_truncated': result.get('output_truncated'),
                'stdout_bytes': result.get('stdout_bytes'), 'stderr_bytes': result.get('stderr_bytes')}
