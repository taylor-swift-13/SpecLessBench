"""Test the sealed entry point with synthetic proofs on all three toolchains."""
import tempfile
from pathlib import Path

from grade_sealed import grade
from sandbox import run_isolated, TOOLCHAINS
from single_task_runner import tree_digest
from test_sandboxed_lean_gate import compile_stage


def test(platform):
    with tempfile.TemporaryDirectory(prefix='specless-grade-test-') as temp:
        root = Path(temp); package = root / 'package'; empty = root / 'empty'
        package.mkdir(); empty.mkdir()
        proof = root / ('Submission.lean' if platform == 'lean' else 'Submission.v')
        if platform == 'lean':
            (package / 'Obligation.lean').write_text('namespace Obligation\ndef goal : Prop := True\nend Obligation\n')
            obj = compile_stage(package, empty, '/trusted/Obligation.lean', 'Obligation.olean')
            (package / 'Obligation.olean').write_bytes(obj)
            cases = [('theorem solve : Obligation.goal := True.intro', 'accepted'),
                     ('theorem solve : Obligation.goal := by sorry', 'rejected'),
                     ('axiom bad : False\ntheorem solve : Obligation.goal := False.elim bad', 'rejected')]
            prefix = 'import Obligation\nnamespace Submission\n'; suffix = '\nend Submission\n'
        else:
            (package / 'Obligation.v').write_text('Definition goal : Prop := True.\n')
            coqc = TOOLCHAINS[platform] + '/bin/coqc'
            result = run_isolated(platform, package, empty, [coqc, '-q', '-noglob', '-Q', '/trusted', 'Trusted', '-Q', '/work', 'Trusted', '-o', '/work/Obligation.vo', '/trusted/Obligation.v'], collect=['Obligation.vo'])
            assert result['status'] == 'exited' and result['exit_code'] == 0, result
            (package / 'Obligation.vo').write_bytes(result['artifacts']['Obligation.vo'])
            cases = [('Definition solve : Obligation.goal := I.', 'accepted'),
                     ('Theorem solve : Obligation.goal. Admitted.', 'rejected'),
                     ('Axiom bad : False. Definition solve : Obligation.goal := False_rect _ bad.', 'rejected')]
            prefix = 'From Trusted Require Import Obligation.\n'; suffix = '\n'
        digest = tree_digest(package)
        for content, expected in cases:
            proof.write_text(prefix + content + suffix)
            result = grade(platform, package, digest, proof)
            assert result['status'] == expected, (platform, content, result)
        (package / 'changed').write_text('tamper')
        assert grade(platform, package, digest, proof)['status'] == 'infrastructure-error'
        print(platform, 'valid / admitted / extra axiom / tampering checked', flush=True)


if __name__ == '__main__':
    for platform in ('lean', 'rocq', 'compcert'):
        test(platform)
