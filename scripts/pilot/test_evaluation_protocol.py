import unittest

from audit_evaluation_costs import session_tokens
from evaluation_prompts import build_prompt, digest
from run_evaluation_wsl import report_markdown


class EvaluationProtocolTests(unittest.TestCase):
    def test_session_snapshots_not_summed(self):
        self.assertEqual(session_tokens([{'input_tokens':100,'output_tokens':10},
                                         {'input_tokens':250,'output_tokens':30}]),
                         {'input_tokens':250,'cached_input_tokens':0,'output_tokens':30})
        self.assertIsNone(session_tokens([]))
        with self.assertRaises(ValueError):
            session_tokens([{'input_tokens':100},{'input_tokens':50}])

    def test_prompt_has_no_external_round_limit(self):
        for platform,budget in [('lean',7200),('rocq',7200),('compcert',14400)]:
            prompt,metadata,_=build_prompt(platform,'baseline',budget)
            self.assertEqual(metadata['initial_prompt_sha256'],digest(prompt))
            self.assertIn(f'{budget} seconds',prompt)
            self.assertNotIn('10 total',prompt)
        with self.assertRaises(ValueError):
            build_prompt('lean','unsupported',7200)

    def test_goal_mode_distinct_from_native_turn_count(self):
        _,metadata,_=build_prompt('compcert','baseline',14400)
        report={'configuration':{'task_id':'test','platform':'compcert','model':'gpt-6-luna',
                'model_reasoning_effort':'medium','prompt_protocol':metadata,'goal_mode':'on'},
                'resources':{},'result':{'status':'rejected'},
                'native_goal_session':{'native_turn_count':4,'client_turn_start_count':1}}
        markdown=report_markdown(report)
        self.assertIn('Goal mode: on',markdown)
        self.assertIn('Native turns: 4',markdown)
        self.assertIn('Manual resumes: 0',markdown)


if __name__ == '__main__':
    unittest.main()
