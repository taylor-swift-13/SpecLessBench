"""Exercise isolation and immutable input binding with synthetic tasks only."""
import tempfile
from pathlib import Path

from single_task_runner import run_attempt, tree_digest


def main():
    with tempfile.TemporaryDirectory(prefix='specless-isolation-test-') as tmp:
        root = Path(tmp)
        task = root / 'task'; task.mkdir()
        (task / 'problem.txt').write_text('ONLY THIS PROBLEM')
        other = root / 'other-problem'; other.mkdir()
        (other / 'secret.txt').write_text('OTHER PROBLEM')
        previous = root / 'previous-attempt'; previous.mkdir()
        (previous / 'secret.txt').write_text('PREVIOUS ATTEMPT')
        digest = tree_digest(task)
        code = ("from pathlib import Path; "
                "assert Path('/trusted/problem.txt').read_text() == 'ONLY THIS PROBLEM'; "
                "assert not Path('/mnt/c').exists(); "
                "assert not Path('/home/yangfp/.ssh').exists(); "
                "assert not list(Path('/submission').iterdir()); "
                "assert not Path('/work/previous').exists(); "
                "Path('/work/previous').write_text('private attempt state'); "
                "Path('/work/Submission.lean').write_text('synthetic proof')")
        for _ in range(2):
            result = run_attempt('lean', task, digest,
                                 ['/usr/bin/python3', '-c', code], 'Submission.lean')
            assert result['status'] == 'exited' and result['exit_code'] == 0, result
            assert result['proof'] == b'synthetic proof'
        result = run_attempt('lean', task, digest, ['/usr/bin/true'], 'Submission.lean')
        assert result['status'] == 'invalid-output' and result['proof'] is None
        (task / 'problem.txt').write_text('modified')
        try:
            run_attempt('lean', task, digest, ['/usr/bin/true'], 'Submission.lean')
        except ValueError as error:
            assert 'digest mismatch' in str(error)
        else:
            raise AssertionError('modified task accepted')
    print('Fresh attempt isolation and sealed task binding passed (synthetic only).')


if __name__ == '__main__':
    main()
