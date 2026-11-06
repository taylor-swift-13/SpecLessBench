import unittest

from run_evaluation_wsl import continuation_stop, round_arguments, report_markdown
from evaluation_prompts import build_prompt, feedback_prompt, digest, GUIDANCE


class SessionContinuationTests(unittest.TestCase):
    def test_prompt_variants_only_differ_in_execution_guidance(self):
        for platform, budget, artifact in [('lean',7200,'Submission.lean'),
                                           ('rocq',7200,'Submission.v'),
                                           ('compcert',14400,'Submission.v')]:
            baseline, bm, bc = build_prompt(platform, 'baseline', budget, 10)
            stronger, sm, sc = build_prompt(platform, 'verification', budget, 10)
            self.assertEqual(stronger, baseline+'\n'+GUIDANCE)
            self.assertIsNone(bc.pop('execution_guidance'))
            self.assertEqual(sc.pop('execution_guidance'), GUIDANCE)
            self.assertEqual(bc, sc)
            for prompt, metadata in [(baseline,bm),(stronger,sm)]:
                self.assertIn(artifact, prompt)
                self.assertIn(f'{budget} seconds', prompt)
                self.assertIn('10 total', prompt)
                self.assertEqual(metadata['initial_prompt_sha256'], digest(prompt))
            self.assertNotEqual(bm['initial_prompt_sha256'],sm['initial_prompt_sha256'])
            self.assertIsNone(bm['component_sha256']['execution_guidance'])
        with self.assertRaises(ValueError):build_prompt('lean','unknown',7200,10)

    def test_shared_feedback_and_report_variant(self):
        feedback=feedback_prompt({'status':'rejected'},6000,9,[{'stdout':'proof error'}])
        self.assertIn('9',feedback)
        self.assertIn('proof error',feedback)
        for variant in ('baseline','verification'):
            _,metadata,_=build_prompt('lean',variant,7200,10)
            report={'configuration':{'task_id':'test','platform':'lean','model':'gpt-6-luna',
                    'model_reasoning_effort':'medium','prompt_protocol':metadata},
                    'resources':{},'result':{'status':'rejected'}}
            markdown=report_markdown(report)
            self.assertIn(variant,markdown)
            self.assertIn(metadata['initial_prompt_sha256'],markdown)

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
