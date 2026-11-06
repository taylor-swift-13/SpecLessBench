import unittest

from audit_evaluation_costs import session_tokens
from evaluation_prompts import build_prompt, digest
from run_evaluation_wsl import report_markdown
from goal_client import goal_objective
from goal_observation import initial_observation, observe
from batch_native_evaluation import jobs, summarize


class EvaluationProtocolTests(unittest.TestCase):
    def test_batch_costs_add_usage_but_not_memory_peaks(self):
        reports=[{'result':{'status':status},'resources':{
                  'tokens':{'input_tokens':count,'cached_input_tokens':count-1,'output_tokens':1},
                  'token_usage_complete':True,'agent_max_cgroup_memory_peak_bytes':peak}}
                 for status,count,peak in [('accepted',10,100),('rejected',20,200)]]
        total=summarize(reports)
        self.assertEqual(total['completed'],2)
        self.assertEqual(total['accepted'],1)
        self.assertEqual(total['tokens']['input_tokens'],30)
        self.assertEqual(total['agent_memory_peak_bytes'],200)

    def test_native_pair_order_and_no_compcert(self):
        queue=jobs([{'pilot_id':'one'}])
        self.assertEqual([(j['platform'],j['goal_mode']) for j in queue],
                         [('lean','off'),('lean','on'),('rocq','off'),('rocq','on')])
        queue[0]['attempts'].append('off-attempt')
        self.assertEqual(queue[1]['attempts'],[])

    def test_goal_platform_interfaces(self):
        self.assertIn('Submission.lean',goal_objective('lean'))
        self.assertIn('Task.lean',goal_objective('lean'))
        self.assertIn('Submission.v',goal_objective('rocq'))
        self.assertNotIn('Submission.lean',goal_objective('rocq'))

    def test_timeout_keeps_observed_native_turns(self):
        state=initial_observation('on')
        observe(state,{'type':'thread.started','thread_id':'root'})
        for direction,method,params in [
            ('send','turn/start',{'threadId':'root'}),
            ('receive','turn/started',{'threadId':'root'}),
            ('receive','turn/completed',{'threadId':'root'}),
            ('receive','turn/started',{'threadId':'root'}),
            ('receive','turn/started',{'threadId':'other'})]:
            observe(state,{'type':'rpc.event','direction':direction,
                           'message':{'method':method,'params':params}})
        self.assertEqual(state['native_turn_count'],2)
        self.assertEqual(state['completed_native_turn_count'],1)
        self.assertEqual(state['client_turn_start_count'],1)
        self.assertEqual(state['manual_resumes'],0)
        with self.assertRaises(ValueError):
            observe(state,{'type':'rpc.event','direction':'send',
                           'message':{'method':'thread/resume'}})

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
