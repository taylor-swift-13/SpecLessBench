import unittest

from run_evaluation_wsl import acceptance_contract, continuation_stop, round_arguments


class SessionContinuationTests(unittest.TestCase):
    def test_acceptance_contract_uses_actual_budget_and_artifact(self):
        for platform, budget, artifact in [('lean',7200,'Submission.lean'),
                                           ('rocq',7200,'Submission.v'),
                                           ('compcert',14400,'Submission.v')]:
            prompt = acceptance_contract(platform, budget, 10)
            self.assertIn(artifact, prompt)
            self.assertIn(f'{budget}-second', prompt)
            self.assertIn('10 TOTAL', prompt)
            self.assertIn('local compilation alone is insufficient', prompt)

    def test_same_session_nine_resumes_then_stop(self):
        session = 'same-original-session'
        commands = []
        for index in range(30):
            commands.append(round_arguments(index, session if index else None, 'continue'))
            reason = continuation_stop({'status':'rejected'}, index*10, 7200, index, 9, session)
            if reason: break
        self.assertEqual(len(commands), 10)
        self.assertEqual(reason, 'resume-limit')
        for command in commands[1:]:
            self.assertEqual(command[0], 'resume')
            self.assertIn(session, command)
            self.assertNotIn('--ephemeral', command)

    def test_budget_shared_instead_of_reset(self):
        for elapsed in (10, 2000, 7199):
            self.assertIsNone(continuation_stop({'status':'rejected'}, elapsed, 7200, 1, 20, 's'))
        self.assertEqual(continuation_stop({'status':'rejected'}, 7200, 7200, 1, 20, 's'), 'time-budget')

    def test_success_and_infrastructure_stop(self):
        self.assertEqual(continuation_stop({'status':'accepted'}, 5, 7200, 0, 20, 's'), 'accepted')
        self.assertEqual(continuation_stop({'status':'agent-error'}, 5, 7200, 0, 20, 's'), 'infrastructure-review')
        with self.assertRaises(RuntimeError):
            continuation_stop({'status':'rejected'}, 5, 7200, 0, 20, None)
        with self.assertRaises(ValueError): round_arguments(1, None, 'continue')


if __name__ == '__main__': unittest.main()
