"""Exercise sandbox -> proof bytes -> sealed grader with synthetic Lean goal."""
import tempfile
from pathlib import Path

from grade_sealed import grade
from single_task_runner import run_attempt, tree_digest
from test_sandboxed_lean_gate import compile_stage


def main():
    with tempfile.TemporaryDirectory(prefix='specless-end-to-end-') as tmp:
        root = Path(tmp); task = root / 'task'; empty = root / 'empty'
        task.mkdir(); empty.mkdir()
        (task / 'Obligation.lean').write_text('namespace Obligation\ndef goal : Prop := True\nend Obligation\n')
        (task / 'Obligation.olean').write_bytes(compile_stage(task, empty, '/trusted/Obligation.lean', 'Obligation.olean'))
        digest = tree_digest(task)
        for term, expected in [('True.intro', 'accepted'), ('by sorry', 'rejected')]:
            source = 'import Obligation\nnamespace Submission\ntheorem solve : Obligation.goal := ' + term + '\nend Submission\n'
            code = 'from pathlib import Path; Path("/work/Submission.lean").write_text(' + repr(source) + ')'
            attempt = run_attempt('lean', task, digest, ['/usr/bin/python3', '-c', code], 'Submission.lean')
            assert attempt['status'] == 'exited' and attempt['exit_code'] == 0, attempt
            proof = root / 'proof.lean'; proof.write_bytes(attempt['proof'])
            decision = grade('lean', task, digest, proof)
            assert decision['status'] == expected, decision
        print('Synthetic agent attempt -> sealed Lean grader: valid accepted, sorry rejected.')


if __name__ == '__main__':
    main()
