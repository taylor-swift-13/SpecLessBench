"""Reject bypasses against the first frozen goal; never prove the task."""
import json
import tempfile
from pathlib import Path

from release_gate import score
from single_task_runner import run_attempt

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / '_build/pilot-v1/first-real-task'


def main():
    meta = json.loads((BUILD / 'registry.json').read_text())
    task = BUILD / 'task'
    cases = [
        ('sorry', 'theorem solve : Obligation.goal := by sorry'),
        ('axiom', 'axiom bypass : Obligation.goal\ntheorem solve : Obligation.goal := bypass'),
        ('wrong-goal', 'theorem solve : True := True.intro'),
    ]
    with tempfile.TemporaryDirectory(prefix='real-task-test-') as tmp:
        proof = Path(tmp) / 'Submission.lean'
        for name, body in cases:
            source = 'import Obligation\nnamespace Submission\n' + body + '\nend Submission\n'
            code = 'from pathlib import Path; Path("/work/Submission.lean").write_text(' + repr(source) + ')'
            attempt = run_attempt('lean', task, meta['public_sha256'],
                                  ['/usr/bin/python3', '-c', code], 'Submission.lean')
            assert attempt['status'] == 'exited' and attempt['exit_code'] == 0, attempt
            proof.write_bytes(attempt['proof'])
            result = score(meta['pilot_id'], 'lean', proof)
            assert result['status'] == 'rejected', (name, result)
            print(name, result['status'], flush=True)
    print('Real frozen Lean equivalence goal tested; no valid task proof attempted.')


if __name__ == '__main__': main()
