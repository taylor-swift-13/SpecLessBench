"""Exercise transition selection and guarded commits using temporary toy evidence."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import transition_native_wall_budget as transition


class TransitionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='native-budget-transition-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.batch = self.root/'batches'/'native'
        self.packages = self.root/'packages'
        self.batch.mkdir(parents=True)
        self.packages.mkdir()
        self.state = {'schema_version': 1, 'platforms': ['lean', 'rocq'],
                      'paused': True, 'jobs': []}

    def add_pair(self, name, off=None, on=None, revision=None, interrupted=False):
        for mode, outcome in (('off', off), ('on', on)):
            job = {'task_id': name, 'platform': 'lean', 'goal_mode': mode,
                   'status': outcome or 'pending-package', 'attempts': [], 'reports': []}
            if outcome:
                directory = self.root/'attempts'/name/mode
                directory.mkdir(parents=True)
                report = {'configuration': {'task_id': name, 'platform': 'lean', 'goal_mode': mode},
                          'result': {'status': outcome},
                          'resources': {'total_wall_seconds': 10, 'agent_wall_seconds': 8,
                                        'checker_wall_seconds': 2, 'tokens': {'input_tokens': 7},
                                        'token_usage_complete': True},
                          'native_goal_session': {'native_turn_count': 1}}
                if revision is not None:
                    report['configuration']['budget_scope_revision'] = revision
                path = directory/'report.json'
                path.write_bytes(transition.encode(report))
                job['reports'] = [str(path)]
                job['attempts'] = [str(directory)]
            if mode == 'on' and interrupted:
                directory = self.root/'attempts'/name/'interrupted-on'
                directory.mkdir(parents=True)
                (directory/'partial.txt').write_text('retained partial, never a model failure')
                job.update(status='infrastructure-error', attempts=[str(directory)], current_run=str(directory))
            self.state['jobs'].append(job)

    def save(self):
        path = self.batch/'status.json'
        path.write_bytes(transition.encode(self.state))
        return path

    def plan(self, clearance=None, *, runtime=False):
        status = self.save()
        with patch.object(transition, 'storage_hold', return_value=None), \
                patch.object(transition, 'retained_storage_hold', return_value=None):
            return transition.build_plan(self.state, status_path=status,
                                         status_sha256=transition.sha(status), packages=self.packages,
                                         clearance_path=clearance, runtime=runtime)

    def reviewed_plan(self, plan):
        path = self.root/'reviewed-plan.json'
        path.write_bytes(transition.encode(plan))
        return {'reviewed_plan_path': path, 'expected_plan_sha256': transition.sha(path)}

    def add_interruption_review(self, name='toy-review', attempt=None):
        job = self.state['jobs'][-1]
        directory = self.batch/'interruptions'/name
        directory.mkdir(parents=True)
        archive = directory/'preserved.tar'
        archive.write_bytes(b'toy retained interruption archive')
        review = {'classification': 'infrastructure-interrupted',
                  'task_id': job['task_id'], 'platform': job['platform'], 'goal_mode': job['goal_mode'],
                  'original_attempt': attempt or job['current_run'], 'archive': str(archive),
                  'archive_sha256': transition.sha(archive), 'originals_modified': False,
                  'terminal_model_result': None, 'host_grading': 'not-run',
                  'included_in_completed_result_or_cost_totals': False,
                  'observed_partial_costs': {'wall_seconds': 3},
                  'native_goal_session': {'native_turn_count': 0},
                  'review_status': 'evidence-preserved; storage preflight pending'}
        path = directory/'interruption.json'
        path.write_bytes(transition.encode(review))
        self.state.setdefault('interruption_reviews', []).append(str(path))
        return path, archive

    def clearance(self, review, archive):
        storage = self.root/'storage-preflight.json'
        storage.write_bytes(transition.encode({'toy_storage_review': 'cleared'}))
        document = {'schema_version': 1, 'clearances': [{
            'original_attempt': self.state['jobs'][-1]['current_run'],
            'interruption_review': str(review), 'interruption_review_sha256': transition.sha(review),
            'archive_sha256': transition.sha(archive), 'approved_to_requeue': True,
            'target_budget_scope_revision': transition.TARGET_REVISION,
            'storage_preflight_evidence': {'path': str(storage), 'sha256': transition.sha(storage)}}]}
        path = self.root/'separate-clearance.json'
        path.write_bytes(transition.encode(document))
        return path

    def runtime_clearance(self, *reviews):
        storage = self.root/'runtime-preflight.json'
        storage.write_bytes(transition.encode({
            'status_sha256': transition.digest(transition.encode(self.state)),
            'canonical_reports_verified': sum(len(job['reports']) for job in self.state['jobs']),
            'target_runtime_scope_revision': transition.RUNTIME_SCOPE_REVISION,
            'target_runtime_config_sha256': transition.RUNTIME_CONFIG_SHA256,
            'fsync_readback_linux_and_windows': True,
            'host_c_available_bytes': transition.HOST_STORAGE_FLOOR_BYTES,
            'retained_directory_bytes': 1000,
        }))
        entries = []
        for review, archive in reviews:
            entries.append({
                'original_attempt': transition.read_json(review)['original_attempt'],
                'interruption_review': str(review),
                'interruption_review_sha256': transition.sha(review),
                'archive_sha256': transition.sha(archive),
                'approved_to_requeue': True,
                'target_runtime_scope_revision': transition.RUNTIME_SCOPE_REVISION,
                'target_runtime_config_sha256': transition.RUNTIME_CONFIG_SHA256,
                'storage_preflight_evidence': {'path': str(storage), 'sha256': transition.sha(storage)},
            })
        path = self.root/'runtime-clearance.json'
        path.write_bytes(transition.encode({'schema_version': 1, 'clearances': entries}))
        return path

    def test_selection_depends_on_revision_and_pair_completeness_not_outcome(self):
        for outcome in ('accepted', 'rejected', 'timeout'):
            self.add_pair('incomplete-'+outcome, off=outcome)
        self.add_pair('completed', off='accepted', on='rejected')
        self.add_pair('pending')
        self.add_pair('already-current', off='rejected', revision=transition.TARGET_REVISION)
        original = copy.deepcopy(self.state)
        plan = self.plan()
        self.assertEqual({row['task_id'] for row in plan['selected_pairs']},
                         {'incomplete-accepted', 'incomplete-rejected', 'incomplete-timeout'})
        self.assertEqual(plan['retained_complete_pairs'], 1)
        self.assertEqual(plan['canonical_completed_before']-plan['canonical_completed_after'], 3)
        self.assertTrue(all(row['fresh_session_order'] == ['off', 'on'] for row in plan['selected_pairs']))
        self.assertEqual(self.state, original)
        self.assertFalse((self.batch.parent/'worker.lock').exists())
        self.assertFalse((self.packages/'activity.lock').exists())

    def test_current_study_shape_projects_217_to_216_with_missing_clearance(self):
        for index in range(108):
            self.add_pair('complete-'+str(index), off='accepted', on='rejected')
        for index in range(29):
            self.add_pair('pending-'+str(index))
        self.add_pair('P-e69f7e9ea72f14cf', off='rejected', interrupted=True)
        self.add_interruption_review()
        plan = self.plan()
        self.assertEqual(len(self.state['jobs']), 276)
        self.assertEqual((plan['canonical_completed_before'], plan['canonical_completed_after']), (217, 216))
        self.assertEqual([row['task_id'] for row in plan['selected_pairs']], ['P-e69f7e9ea72f14cf'])
        self.assertTrue(any('clearance' in error for error in plan['apply_blockers']))
        self.assertEqual(plan['selected_pairs'][0]['superseded_resources']['total_wall_seconds'], 10)
        self.assertFalse(plan['state_changes_committed'])

    def test_guarded_commit_preserves_attempts_and_separates_costs(self):
        self.add_pair('toy', off='rejected', interrupted=True)
        review, archive = self.add_interruption_review()
        clearance = self.clearance(review, archive)
        reviewed = self.reviewed_plan(self.plan(clearance))
        status = self.save()
        original = status.read_bytes()
        report_path = Path(self.state['jobs'][0]['reports'][0])
        report_bytes = report_path.read_bytes()
        interrupted_before = copy.deepcopy(self.state['jobs'][1])
        with patch.object(transition, 'assert_quiescent'):
            result = transition.apply_transition(batch=self.batch, packages=self.packages,
                repo=transition.DEFAULT_REPO, expected_status_sha256=transition.digest(original),
                clearance_path=clearance, **reviewed)
        revised = json.loads(status.read_bytes())
        self.assertEqual(revised['totals']['completed'], 0)
        self.assertEqual(revised['totals']['wall_seconds'], 0)
        self.assertEqual(revised['jobs'][0]['protocol_superseded_reports'], [str(report_path)])
        self.assertTrue(all(job['reports'] == [] and job['status'] == 'pending-package' for job in revised['jobs']))
        self.assertEqual(revised['jobs'][1]['attempts'], interrupted_before['attempts'])
        self.assertEqual(revised['jobs'][1]['current_run'], interrupted_before['current_run'])
        self.assertEqual(report_path.read_bytes(), report_bytes)
        self.assertEqual(revised['future_attempt_budget_scope_revision'], transition.TARGET_REVISION)
        self.assertTrue(revised['paused'])
        directory = Path(result['directory'])
        self.assertEqual((directory/'status.before.json').read_bytes(), original)
        self.assertEqual((directory/'status.after.json').read_bytes(), status.read_bytes())
        self.assertEqual(transition.sha(directory/'reviewed-plan.json'), reviewed['expected_plan_sha256'])
        transaction = transition.read_json(directory/'commit.json')
        self.assertEqual(transaction['phase'], 'committed')
        self.assertEqual(transaction['status_after_sha256'], transition.sha(status))
        retained = transition.read_json(directory/'review.json')
        self.assertEqual(retained['protocol_superseded_reports'][0]['report_snapshot'], json.loads(report_bytes))
        self.assertEqual(retained['protocol_superseded_reports'][0]['resources']['total_wall_seconds'], 10)
        self.assertEqual(retained['interrupted_evidence'][0]['review_snapshot']['observed_partial_costs'], {'wall_seconds': 3})

    def test_missing_clearance_and_changed_sources_cannot_commit(self):
        self.add_pair('toy', off='accepted', interrupted=True)
        self.add_interruption_review()
        plan = self.plan()
        reviewed = self.reviewed_plan(plan)
        status = self.batch/'status.json'
        before = status.read_bytes()
        with patch.object(transition, 'assert_quiescent'):
            with self.assertRaisesRegex(ValueError, 'clearance'):
                transition.apply_transition(batch=self.batch, packages=self.packages,
                    repo=transition.DEFAULT_REPO, expected_status_sha256=transition.digest(before), **reviewed)
        self.assertEqual(status.read_bytes(), before)
        self.assertFalse((self.batch/'protocol-transitions').exists())
        Path(plan['canonical_report_sources'][0]['path']).write_bytes(b'changed after planning')
        with self.assertRaisesRegex(ValueError, 'Evidence changed'):
            transition.verify_plan_sources(plan)

    def test_unrelated_clearance_and_live_controller_are_rejected(self):
        self.add_pair('toy', off='accepted', interrupted=True)
        review, archive = self.add_interruption_review()
        clearance = self.clearance(review, archive)
        content = transition.read_json(clearance)
        content['clearances'][0]['interruption_review_sha256'] = '0'*64
        clearance.write_bytes(transition.encode(content))
        self.assertTrue(any('does not bind' in error for error in self.plan(clearance)['apply_blockers']))
        for command in ('python3 /tmp/batch_native_evaluation.py',
                        'python3 -m run_evaluation_wsl --task toy',
                        "python3 -c 'import run_evaluation_wsl; run_evaluation_wsl.run(\"toy\")'"):
            with self.subTest(command=command), patch.object(transition.subprocess, 'check_output', return_value='1 '+command+'\n'):
                with self.assertRaisesRegex(ValueError, 'Live controller'):
                    transition.assert_quiescent(self.state)

    def test_apply_rejects_report_change_after_review_even_when_status_is_unchanged(self):
        self.add_pair('toy', off='accepted')
        plan = self.plan()
        reviewed = self.reviewed_plan(plan)
        status = self.batch/'status.json'
        before = status.read_bytes()
        report = Path(self.state['jobs'][0]['reports'][0])
        document = transition.read_json(report)
        document['resources']['total_wall_seconds'] += 1
        report.write_bytes(transition.encode(document))
        with patch.object(transition, 'assert_quiescent'):
            with self.assertRaisesRegex(ValueError, 'Evidence changed'):
                transition.apply_transition(batch=self.batch, packages=self.packages,
                    repo=transition.DEFAULT_REPO, expected_status_sha256=transition.digest(before), **reviewed)
        self.assertEqual(status.read_bytes(), before)

    def test_apply_never_waits_for_held_worker_or_activity_lock(self):
        import fcntl
        self.add_pair('toy', off='accepted')
        reviewed = self.reviewed_plan(self.plan())
        status = self.batch/'status.json'
        before = status.read_bytes()
        for lock_path in (self.batch.parent/'worker.lock', self.packages/'activity.lock'):
            with self.subTest(lock=str(lock_path)), lock_path.open('a') as held:
                fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
                with self.assertRaises(BlockingIOError):
                    transition.apply_transition(batch=self.batch, packages=self.packages,
                        repo=transition.DEFAULT_REPO, expected_status_sha256=transition.digest(before), **reviewed)
        self.assertEqual(status.read_bytes(), before)
        self.assertFalse((self.batch/'protocol-transitions').exists())

    def test_runtime_migration_keeps_complete_pairs_and_requires_both_interruptions(self):
        for index in range(108):
            self.add_pair('complete-'+str(index), off='accepted', on='rejected')
        for index in range(29):
            self.add_pair('pending-'+str(index))
        task = 'P-e69f7e9ea72f14cf'
        self.add_pair(task, off='rejected', revision=transition.TARGET_REVISION, interrupted=True)
        first = self.add_interruption_review()
        second_attempt = str(self.root/'attempts'/task/'second-interrupted-on')
        self.state['jobs'][-1]['attempts'].append(second_attempt)
        second = self.add_interruption_review('second-review', second_attempt)
        status = self.save()
        original = status.read_bytes()
        self.assertEqual(self.plan()['selected_pairs'], [])
        plan = self.plan(self.runtime_clearance(first), runtime=True)
        self.assertEqual(len(plan['apply_blockers']), 1)
        self.assertIn(second_attempt, plan['apply_blockers'][0])
        clearance = self.runtime_clearance(first, second)
        plan = self.plan(clearance, runtime=True)
        self.assertEqual(plan['apply_blockers'], [])
        self.assertEqual(plan['retained_complete_pairs'], 108)
        self.assertEqual((plan['canonical_completed_before'], plan['canonical_completed_after']), (217, 216))
        self.assertEqual([pair['task_id'] for pair in plan['selected_pairs']], [task])
        pair = plan['selected_pairs'][0]
        self.assertEqual(pair['fresh_session_order'], ['off', 'on'])
        self.assertEqual(len(pair['interrupted_evidence']), 2)
        off_report = Path(self.state['jobs'][-2]['reports'][0])
        report_bytes = off_report.read_bytes()
        with patch.object(transition, 'assert_quiescent'), \
                patch.object(transition, 'storage_hold', return_value=None), \
                patch.object(transition, 'retained_storage_hold', return_value=None):
            result = transition.apply_transition(batch=self.batch, packages=self.packages,
                repo=transition.DEFAULT_REPO, expected_status_sha256=transition.digest(original),
                clearance_path=clearance, runtime=True, **self.reviewed_plan(plan))
        revised = transition.read_json(status)
        self.assertEqual(revised['jobs'][:-2], self.state['jobs'][:-2])
        self.assertEqual(revised['jobs'][-2]['protocol_superseded_reports'], [str(off_report)])
        self.assertEqual(revised['jobs'][-1]['attempts'], self.state['jobs'][-1]['attempts'])
        self.assertNotIn('current_run', revised['jobs'][-1])
        self.assertEqual([job['status'] for job in revised['jobs'][-2:]], ['pending-package']*2)
        self.assertEqual(off_report.read_bytes(), report_bytes)
        review = transition.read_json(Path(result['directory'])/'review.json')
        self.assertEqual(review['kind'], 'native-runtime-transition-review')
        self.assertEqual(review['target_runtime_config_sha256'], transition.RUNTIME_CONFIG_SHA256)
        self.assertEqual(len(review['interrupted_evidence']), 2)
        self.assertEqual(revised['protocol_runtime_transitions'][0]['revision'], result['revision'])
        self.assertNotIn('protocol_budget_transitions', revised)

    def test_runtime_apply_rejects_changed_config_clearance_archive_and_storage(self):
        self.add_pair('toy', off='rejected', revision=transition.TARGET_REVISION, interrupted=True)
        review, archive = self.add_interruption_review()
        clearance = self.runtime_clearance((review, archive))
        original_clearance = clearance.read_bytes()
        invalid = json.loads(original_clearance)
        invalid['clearances'][0]['target_runtime_config_sha256'] = '0'*64
        clearance.write_bytes(transition.encode(invalid))
        plan = self.plan(clearance, runtime=True)
        self.assertTrue(any('does not bind' in blocker for blocker in plan['apply_blockers']))

        clearance.write_bytes(original_clearance)
        plan = self.plan(clearance, runtime=True)
        self.assertEqual(plan['apply_blockers'], [])
        reviewed = self.reviewed_plan(plan)
        status = self.batch/'status.json'
        original = status.read_bytes()
        apply_args = dict(batch=self.batch, packages=self.packages, repo=transition.DEFAULT_REPO,
                          expected_status_sha256=transition.digest(original), clearance_path=clearance,
                          runtime=True, **reviewed)
        with patch.object(transition, 'assert_quiescent'), \
                patch.object(transition, 'storage_hold', return_value={'reason': 'Host C: low'}):
            with self.assertRaisesRegex(ValueError, 'Host C: low'):
                transition.apply_transition(**apply_args)
        self.assertEqual(status.read_bytes(), original)
        self.assertFalse((self.batch/'protocol-transitions').exists())

        archive.write_bytes(b'changed after review')
        with patch.object(transition, 'assert_quiescent'):
            with self.assertRaisesRegex(ValueError, 'Evidence changed'):
                transition.apply_transition(**apply_args)
        self.assertEqual(status.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
