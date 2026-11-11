"""Check native admission and failure accounting without running an agent."""
import configparser
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import native_runtime_policy as policy


class NativeRuntimePolicyTests(unittest.TestCase):
    def job(self, *, task='P-0000000000000001', platform='lean', mode='on', reports=None):
        return {'task_id': task, 'platform': platform, 'goal_mode': mode,
                'status': 'pending-package', 'attempts': [], 'reports': reports or []}

    def report(self, companion, *, revision=None, config_hash=None):
        return {'configuration': {
            'task_id': companion['task_id'], 'platform': companion['platform'],
            'goal_mode': companion['goal_mode'],
            'runtime_scope_revision': revision or policy.RUNTIME_SCOPE_REVISION,
            'runtime_config_sha256': config_hash or policy.runtime_config()[1]},
            'result': {'status': 'accepted'}}

    def test_storage_floor_boundaries(self):
        floor = 5 * 1024**3
        self.assertEqual(policy.HOST_STORAGE_FLOOR_BYTES, floor)
        for free in (0, floor - 1):
            with self.subTest(free=free):
                hold = policy.storage_hold(free)
                self.assertIsInstance(hold, dict)
                self.assertEqual(hold['free_bytes'], free)
                self.assertEqual(hold['floor_bytes'], floor)
        self.assertIsNone(policy.storage_hold(floor))
        self.assertIsNone(policy.storage_hold(floor + 1))

    def test_host_measurement_failure_returns_a_storage_hold(self):
        with patch.object(policy.os, 'statvfs', side_effect=OSError('synthetic unavailable mount')):
            hold = policy.storage_hold()
        self.assertEqual(hold['kind'], 'storage')

    def test_retained_storage_ceiling_boundaries(self):
        ceiling = 8 * 1024**3
        self.assertEqual(policy.RETAINED_STORAGE_CEILING_BYTES, ceiling)
        self.assertIsNone(policy.retained_storage_hold(ceiling - 1))
        for retained in (ceiling, ceiling + 1):
            with self.subTest(retained=retained):
                hold = policy.retained_storage_hold(retained)
                self.assertEqual(hold['kind'], 'storage')
                self.assertEqual(hold['retained_bytes'], retained)
                self.assertEqual(hold['ceiling_bytes'], ceiling)

    def test_retained_storage_measurement_failure_or_bad_output_holds(self):
        for failure in (OSError('synthetic missing du'),
                        subprocess.TimeoutExpired(['du'], 30)):
            with self.subTest(failure=type(failure).__name__), \
                    patch.object(policy.subprocess, 'check_output', side_effect=failure):
                self.assertEqual(policy.retained_storage_hold()['kind'], 'storage')
        for output in (b'', b'not-a-size\tfixture\n'):
            with self.subTest(output=output), \
                    patch.object(policy.subprocess, 'check_output', return_value=output):
                self.assertEqual(policy.retained_storage_hold()['kind'], 'storage')

    def test_runtime_config_hash_covers_exact_preset_bytes(self):
        text, digest = policy.runtime_config()
        normalized = policy.CONFIG_PATH.read_bytes().replace(b'\r\n', b'\n')
        self.assertEqual(text.encode('utf-8'), normalized)
        self.assertEqual(digest, hashlib.sha256(normalized).hexdigest())

    def test_crlf_checkout_uses_the_same_runtime_configuration(self):
        text, digest = policy.runtime_config()
        with tempfile.TemporaryDirectory(prefix='runtime-crlf-test-') as directory:
            fixture = Path(directory)/'config.toml'
            fixture.write_bytes(text.replace('\n', '\r\n').encode('utf-8'))
            with patch.object(policy, 'CONFIG_PATH', fixture):
                self.assertEqual(policy.runtime_config(), (text, digest))

    def test_preset_preserves_proof_permissions_and_disables_unrelated_features(self):
        text, _ = policy.runtime_config()
        # These fixed TOML sections use the common INI subset. CLI parsing is
        # independently checked below when the research binary is installed.
        config = configparser.ConfigParser(interpolation=None)
        config.read_string('[root]\n' + text)
        for name in ('apps', 'memories', 'plugins', 'remote_plugin'):
            self.assertFalse(config.getboolean('features', name), name)
        self.assertEqual(config['root']['model'], '"gpt-6-luna"')
        self.assertEqual(config['root']['model_reasoning_effort'], '"medium"')
        self.assertEqual(config['root']['approval_policy'], '"never"')
        self.assertEqual(config['root']['web_search'], '"disabled"')
        self.assertFalse(config.getboolean('permissions.eval.network', 'enabled'))
        self.assertEqual(config['permissions.eval.filesystem']['"/home/runner/.codex/auth.json"'], '"deny"')

    def test_no_completed_companion_needs_no_report_reader(self):
        job = self.job()
        companion = self.job(mode='off')
        reader = Mock(side_effect=AssertionError('No canonical report should be read'))
        self.assertIsNone(policy.pair_runtime_hold(job, [companion, job], reader))
        reader.assert_not_called()

    def test_matching_runtime_is_allowed_in_either_pair_direction(self):
        for mode, other in (('on', 'off'), ('off', 'on')):
            with self.subTest(mode=mode):
                job = self.job(mode=mode)
                companion = self.job(mode=other, reports=['canonical.json'])
                reader = Mock(return_value=self.report(companion))
                before = copy.deepcopy([companion, job])
                self.assertIsNone(policy.pair_runtime_hold(job, [companion, job], reader))
                reader.assert_called_once_with('canonical.json')
                self.assertEqual([companion, job], before)

    def test_missing_revision_is_legacy_even_with_current_hash(self):
        job = self.job()
        companion = self.job(mode='off', reports=['legacy.json'])
        report = self.report(companion)
        report['configuration'].pop('runtime_scope_revision')
        hold = policy.pair_runtime_hold(job, [companion, job], lambda _: report)
        self.assertEqual(hold['companion_runtime_revision'], policy.LEGACY_RUNTIME_SCOPE_REVISION)
        self.assertFalse(hold['automatic_requeue_or_retry'])

    def test_explicit_legacy_is_rejected_regardless_of_model_outcome(self):
        job = self.job()
        for outcome in ('accepted', 'rejected', 'timeout'):
            with self.subTest(outcome=outcome):
                companion = self.job(mode='off', reports=['canonical.json'])
                companion['status'] = outcome
                report = self.report(companion, revision=policy.LEGACY_RUNTIME_SCOPE_REVISION)
                report['result']['status'] = outcome
                self.assertIsInstance(policy.pair_runtime_hold(job, [companion, job], lambda _: report), dict)

    def test_matching_revision_with_missing_or_changed_hash_is_rejected(self):
        job = self.job()
        companion = self.job(mode='off', reports=['canonical.json'])
        for old_hash in (None, '0' * 64):
            with self.subTest(old_hash=old_hash):
                report = self.report(companion)
                report['configuration']['runtime_config_sha256'] = old_hash
                self.assertIsInstance(policy.pair_runtime_hold(job, [companion, job], lambda _: report), dict)

    def test_unreviewed_preset_change_is_rejected_before_pair_matching(self):
        job = self.job()
        companion = self.job(mode='off', reports=['canonical.json'])
        report = self.report(companion)
        text, old_hash = policy.runtime_config()
        with tempfile.TemporaryDirectory(prefix='runtime-preset-test-') as directory:
            changed = Path(directory)/'config.toml'
            changed.write_text(text + '\n# changed prospective preset\n')
            with patch.object(policy, 'CONFIG_PATH', changed):
                self.assertNotEqual(hashlib.sha256(changed.read_bytes()).hexdigest(), old_hash)
                with self.assertRaises(RuntimeError):
                    policy.runtime_config()
                reader = Mock(return_value=report)
                with self.assertRaises(RuntimeError):
                    policy.pair_runtime_hold(job, [companion, job], reader)
                reader.assert_not_called()

    def test_other_task_platform_and_same_mode_reports_are_not_companions(self):
        job = self.job()
        unrelated = [self.job(task='P-0000000000000002', mode='off', reports=['wrong-task.json']),
                     self.job(platform='rocq', mode='off', reports=['wrong-platform.json']),
                     self.job(mode='on', reports=['same-mode.json'])]
        reader = Mock(side_effect=AssertionError('An unrelated report was read'))
        self.assertIsNone(policy.pair_runtime_hold(job, unrelated + [job], reader))
        reader.assert_not_called()

    def test_report_identity_must_match_the_canonical_companion(self):
        job = self.job()
        companion = self.job(mode='off', reports=['canonical.json'])
        for field, wrong in (('task_id', 'P-0000000000000002'),
                             ('platform', 'rocq'), ('goal_mode', 'on')):
            with self.subTest(field=field):
                report = self.report(companion)
                report['configuration'][field] = wrong
                self.assertIsInstance(policy.pair_runtime_hold(job, [companion, job], lambda _: report), dict)

    def test_unreadable_or_malformed_canonical_report_blocks(self):
        job = self.job()
        companion = self.job(mode='off', reports=['canonical.json'])
        for reader in (Mock(side_effect=OSError('missing fixture')), Mock(return_value={}),
                       Mock(return_value={'configuration': None})):
            with self.subTest(reader=reader):
                self.assertIsInstance(policy.pair_runtime_hold(job, [companion, job], reader), dict)

    def test_all_canonical_reports_must_match(self):
        job = self.job()
        companion = self.job(mode='off', reports=['new.json', 'legacy.json'])
        reports = {'new.json': self.report(companion),
                   'legacy.json': self.report(companion, revision=policy.LEGACY_RUNTIME_SCOPE_REVISION)}
        self.assertIsInstance(policy.pair_runtime_hold(job, [companion, job], reports.__getitem__), dict)

    def test_noncanonical_history_does_not_replace_canonical_pointers(self):
        job = self.job()
        companion = self.job(mode='off', reports=['current.json'])
        companion.update(original_reports=['legacy.json'], protocol_superseded_reports=['legacy.json'])
        reader = Mock(return_value=self.report(companion))
        self.assertIsNone(policy.pair_runtime_hold(job, [companion, job], reader))
        reader.assert_called_once_with('current.json')

    def test_completed_selected_job_cannot_be_automatically_repeated(self):
        job = self.job(reports=['own-canonical.json'])
        reader = Mock(side_effect=AssertionError('No report should be loaded'))
        self.assertIsInstance(policy.pair_runtime_hold(job, [job], reader), dict)
        reader.assert_not_called()

    def test_installed_cli_loads_preset_in_an_isolated_home(self):
        cli = Path.home()/'.nvm/versions/node/v20.17.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex'
        if not cli.is_file():
            self.skipTest('Research Codex binary is not installed')
        text, _ = policy.runtime_config()
        with tempfile.TemporaryDirectory(prefix='runtime-features-test-') as directory:
            isolated = Path(directory)
            (isolated/'config.toml').write_text(text)
            env = {'HOME': directory, 'CODEX_HOME': directory, 'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}
            result = subprocess.run([str(cli), 'features', 'list'], env=env, capture_output=True,
                                    text=True, timeout=20, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            wanted = {'apps', 'memories', 'plugins', 'remote_plugin'}
            actual = {parts[0]: parts[-1] for line in result.stdout.splitlines()
                      if len(parts := line.split()) >= 3 and parts[0] in wanted}
            self.assertEqual(actual, {name: 'false' for name in wanted})
            self.assertEqual(sorted(str(p.relative_to(isolated)) for p in isolated.rglob('*') if p.is_file()),
                             ['config.toml'])

    def controller_hold(self, *, low_storage, retained_hold=None):
        import batch_native_evaluation as batch

        with tempfile.TemporaryDirectory(prefix='runtime-controller-test-') as directory:
            root = Path(directory)
            base = root/'batches'/'native'
            base.mkdir(parents=True)
            packages = root/'packages'
            job = self.job()
            package = packages/job['task_id']/job['platform']
            package.mkdir(parents=True)
            (package/'registry.json').write_text('{}')
            companion = self.job(mode='off', reports=[str(root/'canonical.json')])
            companion['status'] = 'rejected'
            report = self.report(companion, revision=policy.LEGACY_RUNTIME_SCOPE_REVISION)
            report['result']['status'] = 'rejected'
            report['resources'] = {'tokens': None}
            (root/'canonical.json').write_text(json.dumps(report))
            before_jobs = copy.deepcopy([companion, job])
            (base/'status.json').write_text(json.dumps({'schema_version': 1, 'jobs': before_jobs}))
            writes = []
            original_dump = batch.dump

            def record_dump(path, value):
                writes.append(copy.deepcopy(value))
                original_dump(path, value)

            hold = policy.storage_hold(policy.HOST_STORAGE_FLOOR_BYTES - 1) if low_storage else None
            with patch.object(batch, 'BASE', base), patch.object(batch, 'PACKAGES', packages), \
                    patch.object(batch, 'verify_freeze'), patch.object(batch, 'storage_hold', return_value=hold), \
                    patch.object(batch, 'retained_storage_hold', return_value=retained_hold), \
                    patch.object(batch, 'run', side_effect=AssertionError('A held job must not run')) as run, \
                    patch.object(batch, 'dump', side_effect=record_dump):
                batch.main()
            result = json.loads((base/'status.json').read_text())
            run.assert_not_called()
            self.assertEqual(result['jobs'], before_jobs)
            self.assertIsNone(result['worker_pid'])
            self.assertTrue(writes)
            self.assertTrue(all(value['jobs'] == before_jobs for value in writes))
            self.assertTrue(all(value['phase'] != 'running' for value in writes))
            return result

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Native controller uses Linux flock')
    def test_controller_storage_hold_does_not_mark_or_start_a_job(self):
        state = self.controller_hold(low_storage=True)
        self.assertEqual(state['phase'], 'blocked-infrastructure-storage')
        self.assertEqual(state['preflight_hold']['kind'], 'storage')

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Native controller uses Linux flock')
    def test_controller_runtime_hold_preserves_the_completed_off_report(self):
        state = self.controller_hold(low_storage=False)
        self.assertEqual(state['phase'], 'blocked-runtime-revision')
        self.assertEqual(state['preflight_hold']['kind'], 'runtime')
        self.assertFalse(state['preflight_hold']['automatic_requeue_or_retry'])

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Native controller uses Linux flock')
    def test_controller_retained_storage_hold_does_not_mark_or_start_a_job(self):
        hold = policy.retained_storage_hold(policy.RETAINED_STORAGE_CEILING_BYTES)
        state = self.controller_hold(low_storage=False, retained_hold=hold)
        self.assertEqual(state['phase'], 'blocked-infrastructure-storage')
        self.assertEqual(state['preflight_hold']['retained_bytes'], policy.RETAINED_STORAGE_CEILING_BYTES)

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Native controller uses Linux flock')
    def test_controller_preserves_infrastructure_reports_and_stops_the_queue(self):
        import batch_native_evaluation as batch

        for outcome in ('infrastructure-error', 'agent-error'):
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory(prefix='runtime-failure-test-') as directory:
                root = Path(directory)
                base = root / 'batches' / 'native'
                base.mkdir(parents=True)
                packages = root / 'packages'
                first = self.job(mode='off')
                next_job = self.job(mode='on')
                package = packages / first['task_id'] / first['platform']
                package.mkdir(parents=True)
                (package / 'registry.json').write_text('{}')

                canonical_path = root / 'completed.json'
                completed = self.job(task='P-0000000000000002', mode='off', reports=[str(canonical_path)])
                completed['status'] = 'accepted'
                completed_report = self.report(completed)
                completed_report['resources'] = {
                    'tokens': {'input_tokens': 10, 'cached_input_tokens': 2, 'output_tokens': 3},
                    'token_usage_complete': True,
                    'total_wall_seconds': 7,
                }
                completed_bytes = json.dumps(completed_report).encode()
                canonical_path.write_bytes(completed_bytes)
                (base / 'status.json').write_text(json.dumps({'jobs': [completed, first, next_job]}))

                attempt = root / 'failed-attempt'
                attempt.mkdir()
                failure = self.report(first)
                failure['result'] = {'status': outcome, 'detail': 'Synthetic provider HTTP 401'}
                failure['resources'] = {
                    'tokens': {'input_tokens': 99, 'cached_input_tokens': 88, 'output_tokens': 4},
                    'total_wall_seconds': 31,
                }
                failure_path = attempt / 'report.json'
                failure_bytes = json.dumps(failure).encode()

                def fake_run(task_id, platform, *, timeout, goal_mode, on_run):
                    self.assertEqual((task_id, platform, goal_mode), (first['task_id'], 'lean', 'off'))
                    on_run(attempt)
                    failure_path.write_bytes(failure_bytes)
                    return attempt, failure

                with (
                    patch.object(batch, 'BASE', base),
                    patch.object(batch, 'PACKAGES', packages),
                    patch.object(batch, 'verify_freeze'),
                    patch.object(batch, 'storage_hold', return_value=None),
                    patch.object(batch, 'retained_storage_hold', return_value=None),
                    patch.object(batch, 'run', side_effect=fake_run) as run,
                ):
                    batch.main()

                run.assert_called_once()
                state = json.loads((base / 'status.json').read_text())
                self.assertEqual(state['phase'], 'blocked-infrastructure')
                self.assertIsNone(state['worker_pid'])
                self.assertEqual(state['jobs'][0], completed)
                self.assertEqual(state['jobs'][2], next_job)
                failed = state['jobs'][1]
                self.assertEqual(failed['status'], 'infrastructure-error')
                self.assertEqual(failed['reports'], [])
                self.assertEqual(failed['infrastructure_reports'], [str(failure_path)])
                self.assertEqual(failed['attempts'], [str(attempt)])
                self.assertNotIn('current_run', failed)
                self.assertEqual(state['totals']['completed'], 1)
                self.assertEqual(state['totals']['accepted'], 1)
                self.assertEqual(state['totals']['tokens'], completed_report['resources']['tokens'])
                self.assertEqual(state['totals']['wall_seconds'], 7)
                self.assertEqual(state['by_condition']['lean/off']['completed'], 1)
                self.assertEqual(state['by_condition']['lean/on']['completed'], 0)
                history = [json.loads(line) for line in (base / 'history.jsonl').read_text().splitlines()]
                self.assertEqual(len(history), 1)
                self.assertEqual(history[0]['report'], str(failure_path))
                self.assertEqual(history[0]['result'], failure['result'])
                self.assertFalse(history[0]['included_in_completed_totals'])
                self.assertEqual(canonical_path.read_bytes(), completed_bytes)
                self.assertEqual(failure_path.read_bytes(), failure_bytes)


if __name__ == '__main__':
    unittest.main()
