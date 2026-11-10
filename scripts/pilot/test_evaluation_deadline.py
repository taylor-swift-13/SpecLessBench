"""Exercise attempt deadlines with fake agents/checkers; no model or compiler runs."""
import io
import json
import runpy
import subprocess
import tempfile
import threading
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

import run_evaluation_wsl as runner
import sandbox
import grade_sealed
import lean_grader_core
import rocq_grader_core
from evaluation_prompts import build_prompt
from prepare_evaluation import run_compiler
from single_task_runner import tree_digest


class Clock:
    def __init__(self):self.value=0.0
    def monotonic(self):return self.value
    def advance(self,seconds):self.value+=seconds


class DeadlineTests(unittest.TestCase):
    def attempt(self, *, setup=5, agent=1, compiler=1, checker=1, cleanup=0, observation_error=False, model_requested=True, child_launched=True):
        clock=Clock()
        with tempfile.TemporaryDirectory(prefix='deadline-test-') as temp, ExitStack() as stack:
            root=Path(temp);package=root/'packages'/'fake'/'lean';(package/'task').mkdir(parents=True)
            (package/'task'/'Task.lean').write_text('-- synthetic fixture\n')
            (package/'registry.json').write_text(json.dumps({'pilot_id':'fake','platform':'lean','public_sha256':'digest'}))
            for name in ('auth','codex','host'):(root/name).write_text('synthetic')
            for name,value in {'BASE':root/'runs','PACKAGES':root/'packages','AUTH':root/'auth',
                               'CODEX':root/'codex','CODE_HOST':root/'host'}.items():
                stack.enter_context(patch.object(runner,name,value))
            stack.enter_context(patch.object(runner.time,'monotonic',clock.monotonic))
            def selection():clock.advance(2);return ([{'pilot_id':'fake'}],None)
            stack.enter_context(patch.object(runner,'selection',side_effect=selection))
            stack.enter_context(patch.object(runner,'tree_digest',return_value='digest'))
            def fingerprint(_):clock.advance(setup-2);return {'sha256':'fake'}
            stack.enter_context(patch.object(runner,'fingerprint_tree',side_effect=fingerprint))
            stack.enter_context(patch.object(runner.subprocess,'check_output',return_value='fake-version'))
            observed={}
            def command(argv,**kwargs):
                if 'models' in argv:
                    observed['catalog_timeout']=kwargs['timeout']
                    return subprocess.CompletedProcess(argv,0,json.dumps({'models':[{'slug':'gpt-6-luna','supported_reasoning_levels':[{'effort':'medium'}]}]}).encode(),b'')
                if observation_error and 'show' in argv:
                    clock.advance(kwargs['timeout'])
                    raise subprocess.TimeoutExpired(argv,kwargs['timeout'])
                if 'stop' in argv:clock.advance(cleanup)
                return subprocess.CompletedProcess(argv,0,'','')
            stack.enter_context(patch.object(runner.subprocess,'run',side_effect=command))
            class Agent:
                def __init__(self,argv,**kwargs):
                    self.stopped=threading.Event()
                    config=json.loads(Path(argv[-1]).read_text());observed['agent_config']=config
                    clock.advance(agent)
                    private=Path(config['report']).parent
                    (private/'work'/'claim.json').write_text('{"claim":"equivalence"}')
                    (private/'work'/'Submission.lean').write_text('-- retained synthetic submission\n')
                    Path(config['report']).write_text(json.dumps({'status':'exited','exit_code':0,'wall_seconds':agent,'child_launched':child_launched}))
                    events=[{'type':'thread.started','thread_id':'fake-session'}]
                    if model_requested:
                        events += [{'type':'rpc.event','direction':'send','message':{'method':'turn/start','params':{'threadId':'fake-session'}}},
                                   {'type':'rpc.event','direction':'receive','message':{'method':'turn/started','params':{'threadId':'fake-session'}}}]
                    events += [{'type':'turn.completed'},
                            {'type':'native.run.completed','summary':{'stop_reason':'single-turn-completed'}}]
                    stream=io.BytesIO(b''.join((json.dumps(event)+'\n').encode() for event in events))
                    def lines():
                        yield from stream
                        if observation_error:
                            self.stopped.wait(timeout=2)
                            observed['reader_finished_after_stop']=self.stopped.is_set()
                    self.stdout=lines()
                def poll(self):return None if observation_error and not self.stopped.is_set() else 0
                def kill(self):self.stopped.set();observed['agent_killed']=True
                def wait(self,timeout=None):return 0
            stack.enter_context(patch.object(runner.subprocess,'Popen',Agent))
            def compile_fake(*args,**kwargs):
                observed['compiler_timeout']=kwargs['timeout'];observed['compiler_deadline']=kwargs['deadline'];clock.advance(compiler)
            compile_mock=stack.enter_context(patch.object(runner,'compile_lean',side_effect=compile_fake))
            def grade_fake(*args,**kwargs):
                observed['checker_timeout']=kwargs['timeout'];observed['checker_deadline']=kwargs['deadline'];clock.advance(checker)
                return {'status':'accepted','stage':'synthetic-checker'}
            grade_mock=stack.enter_context(patch.object(runner,'grade',side_effect=grade_fake))
            directory,report=runner.run('fake','lean',timeout=10,goal_mode='off')
            observed.update(compiler_calls=compile_mock.call_count,checker_calls=grade_mock.call_count,
                            prompt=(directory/'prompt.txt').read_bytes(),
                            proof_retained=(directory/'Submission.lean').is_file())
            return report,observed

    def test_setup_and_checking_share_the_entry_deadline(self):
        report,seen=self.attempt()
        self.assertEqual(report['result']['status'],'accepted')
        self.assertEqual(seen['agent_config']['timeout'],5)
        self.assertEqual(seen['agent_config']['deadline_monotonic'],10)
        self.assertEqual(seen['catalog_timeout'],8)
        self.assertEqual(seen['compiler_timeout'],4)
        self.assertEqual(seen['checker_timeout'],3)
        self.assertEqual(seen['compiler_deadline'],seen['checker_deadline'])
        self.assertEqual(report['resources']['decision_wall_seconds'],8)
        self.assertEqual(seen['prompt'],build_prompt('lean','baseline',10)[0].encode())

    def test_expired_setup_never_starts_an_agent(self):
        report,seen=self.attempt(setup=11)
        self.assertEqual(report['result']['status'],'infrastructure-error')
        self.assertTrue(report['result']['budget_exhausted'])
        self.assertEqual(report['stop_reason'],'setup-budget-exhausted')
        self.assertFalse(report['resources']['agent_process_launched'])
        self.assertNotIn('agent_config',seen)
        self.assertEqual(seen['compiler_calls'],0)
        self.assertEqual(seen['checker_calls'],0)

    def test_expired_compiler_never_starts_another_checker(self):
        report,seen=self.attempt(compiler=5)
        self.assertEqual(report['result']['status'],'timeout')
        self.assertEqual(seen['checker_calls'],0)
        self.assertTrue(seen['proof_retained'])

    def test_successful_checker_after_deadline_is_timeout(self):
        report,seen=self.attempt(checker=4)
        self.assertEqual(report['result']['status'],'timeout')
        self.assertEqual(report['resources']['decision_wall_seconds'],11)
        self.assertEqual(report['result']['observed_result_after_deadline']['status'],'accepted')
        self.assertTrue(seen['proof_retained'])

    def test_agent_using_last_second_leaves_no_checker_budget(self):
        report,seen=self.attempt(agent=5)
        self.assertEqual(report['result']['status'],'timeout')
        self.assertEqual(seen['compiler_calls'],0)
        self.assertEqual(seen['checker_calls'],0)

    def test_control_group_lookup_expiry_stops_agent_and_joins_reader(self):
        report,seen=self.attempt(observation_error=True)
        self.assertEqual(report['result']['status'],'timeout')
        self.assertTrue(seen['agent_killed'])
        self.assertTrue(seen['reader_finished_after_stop'])
        self.assertEqual(seen['checker_calls'],0)

    def test_wrapper_start_without_model_request_is_infrastructure(self):
        for child in (False,True):
            with self.subTest(child_launched=child):
                report,seen=self.attempt(observation_error=True,model_requested=False,child_launched=child)
                self.assertEqual(report['result']['status'],'infrastructure-error')
                self.assertTrue(report['result']['budget_exhausted'])
                self.assertFalse(report['result']['model_attempt_observed'])
                self.assertEqual(report['resources']['agent_process_launched'],child)
                self.assertTrue(seen['agent_killed'])
                self.assertTrue(seen['reader_finished_after_stop'])

    def test_cleanup_overhead_does_not_grant_more_model_time(self):
        report,seen=self.attempt(cleanup=2)
        self.assertEqual(report['result']['status'],'accepted')
        self.assertEqual(seen['agent_config']['timeout'],5)
        self.assertEqual(report['resources']['decision_wall_seconds'],8)
        self.assertEqual(report['resources']['post_decision_wall_seconds'],4)
        self.assertEqual(report['resources']['deadline_overrun_seconds'],2)

    def test_expired_deadline_has_no_positive_floor(self):
        with patch.object(runner.time,'monotonic',return_value=10):
            with self.assertRaises(TimeoutError):runner.remaining_seconds(10,180)
        with tempfile.TemporaryDirectory(prefix='deadline-boundary-') as temp:
            root=Path(temp);trusted=root/'trusted';submission=root/'submission';trusted.mkdir();submission.mkdir()
            with patch.object(sandbox.time,'monotonic',return_value=10), patch.object(sandbox.subprocess,'Popen') as spawn:
                with self.assertRaises(TimeoutError):
                    sandbox.run_isolated('lean',trusted,submission,['fake-checker'],deadline=10)
                spawn.assert_not_called()
            with patch('prepare_evaluation.time.monotonic',return_value=10), patch('prepare_evaluation.subprocess.Popen') as spawn:
                with self.assertRaises(TimeoutError):run_compiler(trusted,'fake',['fake-compiler'],{},deadline=10)
                spawn.assert_not_called()

    def test_supervisor_launch_overhead_cannot_reset_the_deadline(self):
        clock=Clock();observed={};read_text=Path.read_text
        with tempfile.TemporaryDirectory(prefix='deadline-supervisor-') as temp:
            root=Path(temp);config=root/'config.json';report=root/'report.json'
            config.write_text(json.dumps({'argv':['fake-agent'],'timeout':10,'deadline_monotonic':10,
                                         'report':str(report),'memory_limit':1024,'pids_limit':8}))
            cgroup={'memory.max':'1024','pids.max':'8','memory.swap.max':'0',
                    'memory.peak':'10','memory.events':'','cpu.stat':''}
            def read(path,*args,**kwargs):
                if str(path)=='/proc/self/cgroup':return '0::/fake'
                if str(path.parent)=='/sys/fs/cgroup/fake':return cgroup[path.name]
                return read_text(path,*args,**kwargs)
            class Process:
                pid=12345
                def __init__(self,*args,**kwargs):clock.advance(3)
                def wait(self,timeout=None):
                    if timeout is not None:
                        observed['wait_timeout']=timeout;clock.advance(timeout)
                        raise subprocess.TimeoutExpired('fake-agent',timeout)
                    return 0
            with patch.object(Path,'read_text',read), patch('sys.argv',['resource_supervisor.py',str(config)]), \
                 patch('time.monotonic',clock.monotonic), patch('subprocess.Popen',Process), patch('os.killpg') as kill:
                with self.assertRaises(SystemExit) as stopped:
                    runpy.run_path(str(Path(runner.__file__).with_name('resource_supervisor.py')))
            self.assertEqual(stopped.exception.code,0)
            self.assertEqual(observed['wait_timeout'],7)
            self.assertEqual(json.loads(report.read_text())['status'],'timeout')
            kill.assert_called_once()
            clock.value=10
            with patch.object(Path,'read_text',read), patch('sys.argv',['resource_supervisor.py',str(config)]), \
                 patch('time.monotonic',clock.monotonic), patch('subprocess.Popen') as spawn:
                with self.assertRaises(SystemExit):
                    runpy.run_path(str(Path(runner.__file__).with_name('resource_supervisor.py')))
            spawn.assert_not_called()
            self.assertFalse(json.loads(report.read_text())['child_launched'])

    def test_sealed_lean_and_rocq_stages_keep_one_deadline(self):
        for platform,module,extension in [('lean',lean_grader_core,'olean'),('rocq',rocq_grader_core,'vo')]:
            with self.subTest(platform=platform), tempfile.TemporaryDirectory(prefix='deadline-stages-') as temp:
                root=Path(temp);package=root/'package';package.mkdir()
                (package/('Obligation.'+extension)).write_bytes(b'synthetic fixture')
                proof=root/('Submission.lean' if platform=='lean' else 'Submission.v');proof.write_text('-- synthetic fixture')
                clock=Clock();calls=[]
                def isolated(*args,**kwargs):
                    calls.append(kwargs['deadline'])
                    if clock.monotonic()>=kwargs['deadline']:raise TimeoutError('shared deadline')
                    clock.advance(4)
                    evidence={'policy':lean_grader_core.LEAN_GRADING_POLICY,'verification':'independent-kernel-reduction',
                              'trust_level':0,'verified_native_decide_axioms':[],'standard_axioms':[]}
                    stdout='native_audit: '+json.dumps(evidence) if platform=='lean' else 'Closed under the global context'
                    return {'status':'exited','exit_code':0,'stdout':stdout,'stderr':'',
                            'artifacts':{name:b'synthetic object' for name in kwargs.get('collect',[])}}
                with patch.object(module,'run_isolated',side_effect=isolated), patch.object(grade_sealed.time,'monotonic',clock.monotonic):
                    if platform=='rocq':
                        with self.assertRaises(TimeoutError):
                            grade_sealed.grade(platform,package,tree_digest(package),proof,deadline=10)
                    else:
                        result=grade_sealed.grade(platform,package,tree_digest(package),proof,deadline=10)
                        self.assertEqual(result['status'],'timeout')
                        self.assertEqual(result['observed_result_after_deadline']['status'],'accepted')
                self.assertEqual(calls,[10]*(3 if platform=='lean' else 4))
                calls.clear();clock.value=0
                def isolated_without_deadline(*args,**kwargs):
                    self.assertIsNone(kwargs['deadline'])
                    kwargs['deadline']=100
                    return isolated(*args,**kwargs)
                with patch.object(module,'run_isolated',side_effect=isolated_without_deadline):
                    result=grade_sealed.grade(platform,package,tree_digest(package),proof)
                self.assertEqual(result['status'],'accepted')
                if platform=='lean':
                    with patch.object(grade_sealed,'grade_lean',side_effect=TimeoutError('synthetic startup timeout')):
                        result=grade_sealed.grade(platform,package,tree_digest(package),proof)
                    self.assertEqual(result['status'],'infrastructure-error')


if __name__=='__main__':unittest.main()
