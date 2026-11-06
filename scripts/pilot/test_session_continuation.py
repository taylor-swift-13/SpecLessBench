import unittest

from run_evaluation_wsl import continuation_stop, round_arguments, report_markdown
from evaluation_prompts import build_prompt, feedback_prompt, digest
from batch_evaluation import make_jobs
from audit_evaluation_costs import session_tokens


class SessionContinuationTests(unittest.TestCase):
    def test_resumed_session_usage_snapshots_not_summed(self):
        self.assertEqual(session_tokens([{'input_tokens':100,'output_tokens':10},
                                         {'input_tokens':250,'output_tokens':30}]),
                         {'input_tokens':250,'cached_input_tokens':0,'output_tokens':30})
        self.assertIsNone(session_tokens([]))
        with self.assertRaises(ValueError):session_tokens([{'input_tokens':100},{'input_tokens':50}])

    def test_baseline_interfaces_and_hashes(self):
        jobs=make_jobs([{'pilot_id':'A','platforms':['lean','rocq']}])
        self.assertEqual([j['prompt_variant'] for j in jobs],['baseline','baseline'])
        for platform,budget in [('lean',7200),('rocq',7200),('compcert',14400)]:
            prompt,metadata,components=build_prompt(platform,'baseline',budget,10)
            self.assertEqual(metadata['initial_prompt_sha256'],digest(prompt))
            self.assertIn(f'{budget} seconds',prompt)
            self.assertIn('10 total',prompt)
            self.assertIsNone(components['execution_guidance'])
        with self.assertRaises(ValueError):build_prompt('lean','removed-variant',7200,10)

    def test_shared_feedback_and_report_variant(self):
        feedback=feedback_prompt({'status':'rejected'},6000,9,[{'stdout':'proof error'}])
        self.assertIn('9',feedback)
        self.assertIn('proof error',feedback)
        for variant in ('baseline',):
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
