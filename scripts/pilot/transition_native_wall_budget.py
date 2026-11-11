"""Plan a uniform budget-revision transition for incomplete native Goal pairs.

Default operation only reads evidence and prints JSON, without taking locks.
--apply requires a saved reviewed plan and its SHA, the reviewed status SHA,
both nonblocking study locks, no live
controller/evaluator, and explicit storage/requeue clearance for interrupted
companions. It changes canonical pointers, never original attempts or reports,
and does not start a model, prepare a package, grade a proof, or resume a session.

Clearance JSON (separate from immutable interruption reviews)::

  {"schema_version": 1, "clearances": [{
    "original_attempt": "/absolute/attempt/path",
    "interruption_review": "/absolute/interruption.json",
    "interruption_review_sha256": "<sha256>", "archive_sha256": "<sha256>",
    "target_budget_scope_revision": "attempt-entry-deadline-v1",
    "approved_to_requeue": true,
    "storage_preflight_evidence": {"path": "/absolute/evidence.json",
                                   "sha256": "<sha256>"}}]}

A prepared transaction contains before/after state and a separate cost review.
Status replacement is atomic; commit.json and the recorded after-state SHA make
a crash between preparation and replacement distinguishable from a commit.
"""
from __future__ import annotations

import argparse
import ast
import collections
import contextlib
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import uuid

from native_runtime_policy import (HOST_STORAGE_FLOOR_BYTES, LEGACY_RUNTIME_SCOPE_REVISION,
                                  RETAINED_STORAGE_CEILING_BYTES, RUNTIME_CONFIG_SHA256,
                                  RUNTIME_SCOPE_REVISION, retained_storage_hold, runtime_config,
                                  storage_hold)

TARGET_REVISION = 'attempt-entry-deadline-v1'
COMPLETED = frozenset(('accepted', 'rejected', 'timeout'))
DEFAULT_BATCH = Path.home()/'.local/share/speclessbench/batches/native-luna-medium'
DEFAULT_PACKAGES = Path.home()/'.local/share/speclessbench/packages'
DEFAULT_REPO = Path(__file__).resolve().parents[2]
COST_SCOPE = ('Canonical totals contain only job.reports. Superseded completed '
              'reports and interrupted partial costs remain preserved separately; '
              'they remain part of historical resource expenditure.')


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False)+'\n').encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024*1024), b''):
            value.update(block)
    return value.hexdigest()


def file_evidence(path):
    path = Path(path)
    if not path.is_absolute() or not path.is_file() or path.is_symlink():
        raise ValueError(f'Expected an existing absolute evidence file: {path}')
    return {'path': str(path), 'sha256': sha(path)}


def atomic_bytes(path, data):
    temporary = path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    with temporary.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def read_json(path):
    return json.loads(Path(path).read_bytes())


def installed_revision(repo):
    source = Path(repo)/'scripts/pilot/run_evaluation_wsl.py'
    tree = ast.parse(source.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == 'BUDGET_SCOPE_REVISION'
                for target in node.targets):
            return ast.literal_eval(node.value)
    return None


def summarize(reports):
    # Importing the batch controller defines its functions; main() is not run.
    from batch_native_evaluation import summarize as batch_summarize
    return batch_summarize(reports)


def canonical_reports(state):
    rows = []
    seen_paths = set()
    for index, job in enumerate(state['jobs']):
        paths = job.get('reports', [])
        if len(paths) > 1:
            raise ValueError('A job has multiple canonical reports; refusing double counting')
        if not paths:
            if job['status'] in COMPLETED:
                raise ValueError(f'Completed job lacks a canonical report: {index}')
            continue
        evidence = file_evidence(paths[0])
        if evidence['path'] in seen_paths:
            raise ValueError('A canonical report is referenced by multiple jobs')
        seen_paths.add(evidence['path'])
        report = read_json(evidence['path'])
        config = report['configuration']
        if tuple(config.get(key) for key in ('task_id', 'platform', 'goal_mode')) != tuple(
                job[key] for key in ('task_id', 'platform', 'goal_mode')):
            raise ValueError(f'Report/job identity mismatch: {evidence["path"]}')
        if report['result']['status'] != job['status']:
            raise ValueError(f'Report/job outcome mismatch: {evidence["path"]}')
        rows.append({'job_index': index, **evidence, 'report': report})
    return rows


def review_paths(state, supplied):
    paths = list(map(str, supplied))
    for value in state.get('interruption_reviews', []):
        if isinstance(value, str):
            paths.append(value)
        elif isinstance(value, dict):
            for key in ('interruption_review', 'review', 'review_path', 'path'):
                if value.get(key):
                    paths.append(value[key])
                    break
    return list(dict.fromkeys(paths))


def interrupted_evidence(job, reviews, clearances, target, *, runtime_config_sha256=None,
                         runtime_preflight=None):
    """Bind immutable interruption evidence to separate, explicit clearance."""
    if runtime_config_sha256 is None:
        target_fields = {'target_budget_scope_revision': target}
    else:
        target_fields = {'target_runtime_scope_revision': target,
                         'target_runtime_config_sha256': runtime_config_sha256}
    blockers = []
    retained = []
    attempts = list(dict.fromkeys(job.get('attempts', []) +
                                 ([job['current_run']] if job.get('current_run') else [])))
    needs_review = bool(attempts) or job['status'] not in ('pending-package',)
    if not needs_review:
        return retained, blockers
    if not attempts:
        return retained, ['Interrupted companion has no preserved attempt path']
    for attempt in attempts:
        matches = [(path, review) for path, review in reviews if
                   review.get('original_attempt') == attempt and
                   tuple(review.get(key) for key in ('task_id', 'platform', 'goal_mode')) ==
                   tuple(job[key] for key in ('task_id', 'platform', 'goal_mode'))]
        if len(matches) != 1:
            blockers.append(f'Expected one preserved interruption review for {attempt}')
            continue
        path, review = matches[0]
        try:
            evidence = file_evidence(path)
            if (review.get('classification') != 'infrastructure-interrupted' or
                    review.get('originals_modified') is not False or
                    review.get('terminal_model_result') is not None or
                    review.get('host_grading') != 'not-run' or
                    review.get('included_in_completed_result_or_cost_totals') is not False):
                raise ValueError('Interruption review does not preserve an ungraded infrastructure partial')
            archive = file_evidence(review['archive'])
            if archive['sha256'] != review['archive_sha256']:
                raise ValueError('Preserved interruption archive hash mismatch')
            row = {'original_attempt': attempt, 'interruption_review': evidence,
                   'archive': archive, 'review_snapshot': review,
                   'partial_cost_scope': 'Preserved infrastructure partial; excluded from canonical completed totals'}
            retained.append(row)
            approvals = [entry for entry in clearances if entry.get('original_attempt') == attempt]
            if len(approvals) != 1:
                raise ValueError('Missing unique separate storage/requeue clearance')
            approval = approvals[0]
            if (approval.get('approved_to_requeue') is not True or
                    any(approval.get(key) != value for key, value in target_fields.items()) or
                    approval.get('interruption_review') != evidence['path'] or
                    approval.get('interruption_review_sha256') != evidence['sha256'] or
                    approval.get('archive_sha256') != archive['sha256']):
                raise ValueError('Separate clearance does not bind this review, archive and target revision')
            storage = approval['storage_preflight_evidence']
            observed_storage = file_evidence(storage['path'])
            if observed_storage['sha256'] != storage['sha256']:
                raise ValueError('Storage preflight evidence hash mismatch')
            if runtime_preflight is not None:
                preflight = read_json(observed_storage['path'])
                expected = {**target_fields, **runtime_preflight}
                host_bytes = preflight.get('host_c_available_bytes')
                retained_bytes = preflight.get('retained_directory_bytes')
                if (any(preflight.get(key) != value for key, value in expected.items()) or
                        preflight.get('fsync_readback_linux_and_windows') is not True or
                        type(host_bytes) is not int or host_bytes < HOST_STORAGE_FLOOR_BYTES or
                        type(retained_bytes) is not int or not 0 <= retained_bytes < RETAINED_STORAGE_CEILING_BYTES):
                    raise ValueError('Storage preflight does not establish current status, runtime and write readiness')
            row['clearance'] = copy.deepcopy(approval)
            row['storage_preflight_evidence'] = observed_storage
        except (KeyError, OSError, ValueError) as error:
            blockers.append(f'{attempt}: {error}')
    return retained, blockers


def recompute(state, packages):
    reports = [row['report'] for row in canonical_reports(state)]
    state['counts'] = dict(collections.Counter(job['status'] for job in state['jobs']))
    state['ready_runs'] = sum(job['status'] == 'pending-package' and
                             (packages/job['task_id']/job['platform']/'registry.json').is_file()
                             for job in state['jobs'])
    state['unprepared_runs'] = state['counts'].get('pending-package', 0)-state['ready_runs']
    state['totals'] = summarize(reports)
    state['by_condition'] = {platform+'/'+mode: summarize([report for report in reports if
        report['configuration']['platform'] == platform and report['configuration']['goal_mode'] == mode])
        for platform in state.get('platforms', ('lean', 'rocq')) for mode in ('off', 'on')}


def revision_summaries(reports, key='budget_scope_revision', default='legacy-unspecified'):
    revisions = sorted({report['configuration'].get(key) or default for report in reports})
    return {revision: summarize([report for report in reports if
        (report['configuration'].get(key) or default) == revision])
        for revision in revisions}


def projected_state(state, selected, packages, *, runtime=False):
    revised = copy.deepcopy(state)
    for pair in selected:
        completed = revised['jobs'][pair['completed_job_index']]
        completed.setdefault('protocol_superseded_reports', []).extend(completed['reports'])
        completed['reports'] = []
        completed['status'] = 'pending-package'
        companion = revised['jobs'][pair['companion_job_index']]
        companion['reports'] = []
        companion['status'] = 'pending-package'
        if runtime:
            for job in (completed, companion):
                prior = job.pop('current_run', None)
                if prior and prior not in job.setdefault('attempts', []):
                    job['attempts'].append(prior)
    recompute(revised, packages)
    return revised


def build_plan(state, *, status_path, status_sha256, packages=DEFAULT_PACKAGES,
               repo=DEFAULT_REPO, clearance_path=None, supplied_reviews=(), runtime=False):
    packages = Path(packages)
    rows = canonical_reports(state)
    by_job = {row['job_index']: row for row in rows}
    groups = {}
    for index, job in enumerate(state['jobs']):
        mode = job['goal_mode']
        if mode not in ('off', 'on'):
            raise ValueError('Unknown native Goal condition')
        group = groups.setdefault((job['task_id'], job['platform']), {})
        if mode in group:
            raise ValueError('Duplicate task/platform/condition job')
        group[mode] = index
    reviews = []
    review_errors = []
    for path in review_paths(state, supplied_reviews):
        try:
            reviews.append((path, read_json(path)))
        except (OSError, ValueError) as error:
            review_errors.append(f'Cannot read interruption review {path}: {error}')
    clearance_source = None
    clearances = []
    if clearance_path is not None:
        clearance_source = file_evidence(clearance_path)
        clearance_document = read_json(clearance_path)
        if clearance_document.get('schema_version') != 1:
            raise ValueError('Unsupported separate clearance schema')
        clearances = clearance_document['clearances']
    selected = []
    retained_complete_pairs = 0
    for (task_id, platform), indices in sorted(groups.items()):
        if set(indices) != {'off', 'on'}:
            raise ValueError(f'Incomplete job definition for {task_id}/{platform}')
        completed = [index for index in indices.values() if index in by_job and
                     by_job[index]['report']['result']['status'] in COMPLETED]
        if len(completed) == 2:
            retained_complete_pairs += 1
            continue
        if len(completed) != 1:
            continue
        index = completed[0]
        row = by_job[index]
        configuration = row['report']['configuration']
        previous_budget = configuration.get('budget_scope_revision')
        previous_runtime = configuration.get('runtime_scope_revision', LEGACY_RUNTIME_SCOPE_REVISION)
        previous_config = configuration.get('runtime_config_sha256')
        if runtime:
            if (previous_runtime, previous_config) == (RUNTIME_SCOPE_REVISION, RUNTIME_CONFIG_SHA256):
                continue
        elif previous_budget == TARGET_REVISION:
            continue
        other = indices['on' if state['jobs'][index]['goal_mode'] == 'off' else 'off']
        companion = state['jobs'][other]
        if runtime:
            evidence, blockers = interrupted_evidence(
                companion, reviews, clearances, RUNTIME_SCOPE_REVISION,
                runtime_config_sha256=RUNTIME_CONFIG_SHA256,
                runtime_preflight={'status_sha256': status_sha256,
                                   'canonical_reports_verified': len(rows)})
            if platform not in ('lean', 'rocq') or index != indices['off']:
                blockers.append('Runtime migration requires a completed Lean/Rocq off and its unfinished on companion')
            if previous_budget != TARGET_REVISION or previous_runtime != LEGACY_RUNTIME_SCOPE_REVISION:
                blockers.append('Companion report is outside the reviewed legacy-runtime transition')
        else:
            evidence, blockers = interrupted_evidence(companion, reviews, clearances, TARGET_REVISION)
        if companion.get('reports'):
            blockers.append('Uncompleted companion has canonical report pointers; explicit review is required')
        if indices['off'] >= indices['on']:
            blockers.append('Controller job order does not schedule fresh off before on')
        pair = {'task_id': task_id, 'platform': platform,
                         'completed_job_index': index, 'companion_job_index': other,
                         'completed_goal_mode': state['jobs'][index]['goal_mode'],
                         'superseded_report': {key: row[key] for key in ('path', 'sha256')},
                         'superseded_result': row['report']['result'],
                         'previous_budget_scope_revision': previous_budget,
                         'superseded_resources': row['report']['resources'],
                         'interrupted_evidence': evidence,
                         'preserved_attempt_paths': {mode: copy.deepcopy(state['jobs'][job_index].get('attempts', []))
                                                     for mode, job_index in indices.items()},
                         'fresh_session_order': ['off', 'on'], 'apply_blockers': blockers}
        if runtime:
            pair.update(previous_runtime_scope_revision=previous_runtime,
                        previous_runtime_config_sha256=previous_config)
        selected.append(pair)
    projected = projected_state(state, selected, packages, runtime=runtime)
    source_paths = [Path(repo)/'scripts/pilot'/name for name in (
        'transition_native_wall_budget.py', 'batch_native_evaluation.py', 'run_evaluation_wsl.py')]
    blockers = [message for pair in selected for message in pair['apply_blockers']]
    if any(job['status'] == 'running' for job in state['jobs']):
        blockers.append('Study state still contains running jobs')
    if installed_revision(repo) != TARGET_REVISION:
        blockers.append('Installed runner budget revision differs from transition target')
    if runtime:
        source_paths.extend(Path(repo)/'scripts/pilot'/name for name in (
            'transition_native_runtime.py', 'native_runtime_policy.py', 'native_proof_runtime_minimal.toml'))
        _, effective_config_sha = runtime_config()
        preset = source_paths[-1].read_bytes().replace(b'\r\n', b'\n')
        if digest(preset) != effective_config_sha:
            blockers.append('Repository preset differs from the reviewed effective runtime configuration')
        if not selected:
            blockers.append('No incomplete legacy-runtime pair requires transition')
        hold = storage_hold() or retained_storage_hold()
        if hold:
            blockers.append(hold['reason'])
    plan = {'schema_version': 1, 'kind': 'native-wall-budget-transition-plan', 'created_utc': now(),
            'target_budget_scope_revision': TARGET_REVISION,
            'selection_rule': 'Every incomplete pair with exactly one canonical completed condition under an older budget revision, independent of its outcome',
            'status_source': {'path': str(Path(status_path)), 'sha256': status_sha256},
            'packages_root': str(packages.resolve()), 'repo_root': str(Path(repo).resolve()),
            'apply_lock_paths': [str(Path(status_path).parent.parent/'worker.lock'),
                                 str(packages.resolve()/'activity.lock')],
            'runner_sources': [file_evidence(path) for path in source_paths],
            'canonical_report_sources': [{key: row[key] for key in ('path', 'sha256')} for row in rows],
            'clearance_source': clearance_source, 'review_read_errors': review_errors,
            'selected_pairs': selected, 'retained_complete_pairs': retained_complete_pairs,
            'canonical_completed_before': summarize([row['report'] for row in rows])['completed'],
            'canonical_completed_after': projected['totals']['completed'],
            'projected_counts': projected['counts'], 'projected_totals': projected['totals'],
            'projected_by_condition': projected['by_condition'],
            'canonical_by_budget_scope_revision_before': revision_summaries([row['report'] for row in rows]),
            'canonical_by_budget_scope_revision_after': revision_summaries(
                [row['report'] for row in canonical_reports(projected)]),
            'resource_cost_scope': COST_SCOPE,
            'fresh_attempt_policy': 'New independent sessions, off then on; no proof/session reuse and no external resume',
            'future_attempt_budget_scope_revision': TARGET_REVISION,
            'apply_blockers': blockers, 'apply_allowed_by_evidence': not blockers,
            'runtime_guards_not_checked_in_plan': ['worker/activity LOCK_NB', 'no live controller/evaluator',
                                                   'status, report, runner, review, archive and clearance hashes unchanged'],
            'state_changes_committed': False}
    if runtime:
        plan.update(kind='native-runtime-transition-plan',
                    target_runtime_scope_revision=RUNTIME_SCOPE_REVISION,
                    target_runtime_config_sha256=effective_config_sha,
                    selection_rule='Incomplete pairs with a completed legacy-runtime off under the current deadline, independent of outcome',
                    canonical_by_runtime_scope_revision_before=revision_summaries(
                        [row['report'] for row in rows], 'runtime_scope_revision', LEGACY_RUNTIME_SCOPE_REVISION),
                    canonical_by_runtime_scope_revision_after=revision_summaries(
                        [row['report'] for row in canonical_reports(projected)],
                        'runtime_scope_revision', LEGACY_RUNTIME_SCOPE_REVISION))
    return plan


def assert_quiescent(state):
    if any(job['status'] == 'running' for job in state['jobs']):
        raise ValueError('A running job remains in study state')
    processes = subprocess.check_output(['ps', '-eo', 'pid=,args='], text=True)
    scripts = {'batch_native_evaluation.py', 'run_evaluation_wsl.py', 'goal_client.py', 'resource_supervisor.py'}
    module_names = {Path(script).stem for script in scripts}
    for line in processes.splitlines():
        fields = line.strip().split(None, 1)
        if len(fields) != 2 or int(fields[0]) == os.getpid():
            continue
        try:
            argv = shlex.split(fields[1])
        except ValueError:
            raise ValueError('Cannot safely inspect a live process command')
        module = argv[argv.index('-m')+1:argv.index('-m')+2] if '-m' in argv else []
        inline = argv[argv.index('-c')+1:] if '-c' in argv else []
        known_module = bool(module and module[0].rsplit('.', 1)[-1] in module_names)
        known_inline = any(re.search(r'\b'+re.escape(name)+r'\b', value)
                           for value in inline for name in module_names)
        if (any(Path(value).name in scripts for value in argv) or known_module or known_inline or
                ('/opt/codex' in argv and 'app-server' in argv)):
            raise ValueError(f'Live controller/evaluator remains: pid {fields[0]}')


def verify_plan_sources(plan):
    sources = plan['canonical_report_sources'] + plan['runner_sources']
    if plan['clearance_source']:
        sources.append(plan['clearance_source'])
    for pair in plan['selected_pairs']:
        for row in pair['interrupted_evidence']:
            sources += [row['interruption_review'], row['archive']]
            if row.get('storage_preflight_evidence'):
                sources.append(row['storage_preflight_evidence'])
    for source in sources:
        if file_evidence(source['path'])['sha256'] != source['sha256']:
            raise ValueError(f'Evidence changed since planning: {source["path"]}')


def apply_transition(*, batch, packages, repo, expected_status_sha256,
                     reviewed_plan_path, expected_plan_sha256,
                     clearance_path=None, supplied_reviews=(), runtime=False):
    import fcntl
    batch = Path(batch).resolve()
    packages = Path(packages).resolve()
    status = batch/'status.json'
    os.umask(0o077)
    with contextlib.ExitStack() as stack:
        for path in (batch.parent/'worker.lock', packages/'activity.lock'):
            lock = stack.enter_context(path.open('a'))
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        original = status.read_bytes()
        if digest(original) != expected_status_sha256:
            raise ValueError('Study status differs from the reviewed plan')
        reviewed_bytes = Path(reviewed_plan_path).read_bytes()
        if digest(reviewed_bytes) != expected_plan_sha256:
            raise ValueError('Saved reviewed plan SHA does not match')
        reviewed_plan = json.loads(reviewed_bytes)
        expected_kind = 'native-runtime-transition-plan' if runtime else 'native-wall-budget-transition-plan'
        if (reviewed_plan.get('kind') != expected_kind or
                reviewed_plan.get('target_budget_scope_revision') != TARGET_REVISION or
                reviewed_plan.get('state_changes_committed') is not False or
                reviewed_plan.get('status_source') != {'path': str(status), 'sha256': expected_status_sha256}):
            raise ValueError('Saved reviewed plan does not bind this status and target revision')
        if runtime and (reviewed_plan.get('target_runtime_scope_revision') != RUNTIME_SCOPE_REVISION or
                        reviewed_plan.get('target_runtime_config_sha256') != RUNTIME_CONFIG_SHA256):
            raise ValueError('Saved reviewed plan does not bind the target runtime and configuration')
        if reviewed_plan['apply_blockers']:
            raise ValueError('Saved reviewed plan still has apply blockers: '+'; '.join(reviewed_plan['apply_blockers']))
        verify_plan_sources(reviewed_plan)
        state = json.loads(original)
        assert_quiescent(state)
        plan = build_plan(state, status_path=status, status_sha256=digest(original),
                          packages=packages, repo=repo, clearance_path=clearance_path,
                          supplied_reviews=supplied_reviews, runtime=runtime)
        if plan['apply_blockers']:
            raise ValueError('Transition blocked: '+'; '.join(plan['apply_blockers']))
        reviewed_fields = ('target_budget_scope_revision', 'runner_sources', 'canonical_report_sources',
                           'packages_root', 'repo_root', 'apply_lock_paths',
                           'clearance_source', 'selected_pairs', 'canonical_completed_before',
                           'canonical_completed_after', 'projected_counts', 'projected_totals')
        if runtime:
            reviewed_fields += ('target_runtime_scope_revision', 'target_runtime_config_sha256',
                                'retained_complete_pairs', 'projected_by_condition')
        for field in reviewed_fields:
            if plan[field] != reviewed_plan[field]:
                raise ValueError(f'Current transition differs from saved reviewed plan: {field}')
        revised = projected_state(state, plan['selected_pairs'], packages, runtime=runtime)
        revision = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:12]
        output = batch/'protocol-transitions'/revision
        staged = output.with_name('.'+revision+'.prepared')
        staged.mkdir(parents=True, mode=0o700)
        reports = {row['path']: row['report'] for row in canonical_reports(state)}
        review = {'schema_version': 1, 'kind': 'native-wall-budget-transition-review',
                  'revision': revision, 'created_utc': now(),
                  'target_budget_scope_revision': TARGET_REVISION,
                  'original_status_sha256': digest(original), 'resource_cost_scope': COST_SCOPE,
                  'reviewed_plan_source': {'path': str(Path(reviewed_plan_path)), 'sha256': expected_plan_sha256},
                  'canonical_by_budget_scope_revision_before': plan['canonical_by_budget_scope_revision_before'],
                  'canonical_by_budget_scope_revision_after': plan['canonical_by_budget_scope_revision_after'],
                  'protocol_superseded_reports': [{**pair['superseded_report'],
                      'report_snapshot': reports[pair['superseded_report']['path']],
                      'resources': pair['superseded_resources']} for pair in plan['selected_pairs']],
                  'interrupted_evidence': [row for pair in plan['selected_pairs'] for row in pair['interrupted_evidence']],
                  'original_attempts_reports_and_submissions_modified': False,
                  'new_model_sessions_started': 0}
        if runtime:
            review.update(kind='native-runtime-transition-review',
                          target_runtime_scope_revision=RUNTIME_SCOPE_REVISION,
                          target_runtime_config_sha256=RUNTIME_CONFIG_SHA256,
                          canonical_by_runtime_scope_revision_before=plan['canonical_by_runtime_scope_revision_before'],
                          canonical_by_runtime_scope_revision_after=plan['canonical_by_runtime_scope_revision_after'])
        review_data = encode(review)
        plan_data = encode(plan)
        transition_record = {
            'revision': revision, 'target_budget_scope_revision': TARGET_REVISION,
            'review': str(output/'review.json'), 'review_sha256': digest(review_data),
            'plan': str(output/'plan.json'), 'plan_sha256': digest(plan_data),
            'original_status_sha256': digest(original),
            'canonical_completed_before': plan['canonical_completed_before'],
            'canonical_completed_after': plan['canonical_completed_after']}
        if runtime:
            transition_record.update(target_runtime_scope_revision=RUNTIME_SCOPE_REVISION,
                                     target_runtime_config_sha256=RUNTIME_CONFIG_SHA256)
            revised['future_attempt_runtime_scope_revision'] = RUNTIME_SCOPE_REVISION
            revised['future_attempt_runtime_config_sha256'] = RUNTIME_CONFIG_SHA256
            revised.setdefault('protocol_runtime_transitions', []).append(transition_record)
        else:
            revised['future_attempt_budget_scope_revision'] = TARGET_REVISION
            revised.setdefault('protocol_budget_transitions', []).append(transition_record)
        revised['updated_utc'] = now()
        revised['phase'] = 'paused' if revised.get('paused') else 'between-runs'
        after = encode(revised)
        transaction = {'schema_version': 1, 'revision': revision, 'phase': 'prepared',
                       'status_before_sha256': digest(original), 'status_after_sha256': digest(after),
                       'status_path': str(status), 'review_sha256': digest(review_data)}
        for name, data in (('status.before.json', original), ('status.after.json', after),
                           ('review.json', review_data), ('plan.json', plan_data),
                           ('reviewed-plan.json', reviewed_bytes),
                           ('commit.json', encode(transaction))):
            atomic_bytes(staged/name, data)
        verify_plan_sources(plan)
        assert_quiescent(state)
        if runtime:
            hold = storage_hold() or retained_storage_hold()
            if hold:
                raise ValueError('Transition blocked: '+hold['reason'])
        if status.read_bytes() != original:
            raise ValueError('Study status changed during preparation; no transition committed')
        staged.rename(output)
        atomic_bytes(status, after)
        transaction.update(phase='committed', committed_utc=now())
        atomic_bytes(output/'commit.json', encode(transaction))
        result = {'revision': revision, 'directory': str(output), 'state_changes_committed': True,
                'canonical_completed_before': plan['canonical_completed_before'],
                'canonical_completed_after': plan['canonical_completed_after'],
                  'future_attempt_budget_scope_revision': TARGET_REVISION}
        if runtime:
            result.update(future_attempt_runtime_scope_revision=RUNTIME_SCOPE_REVISION,
                          future_attempt_runtime_config_sha256=RUNTIME_CONFIG_SHA256)
        return result


def main(*, runtime=False, description=__doc__):
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--batch', type=Path, default=DEFAULT_BATCH)
    parser.add_argument('--packages', type=Path, default=DEFAULT_PACKAGES)
    parser.add_argument('--repo', type=Path, default=DEFAULT_REPO)
    parser.add_argument('--clearance', type=Path)
    parser.add_argument('--interruption-review', type=Path, action='append', default=[])
    parser.add_argument('--apply', action='store_true', help='Explicitly apply a reviewed transition; never starts evaluations')
    parser.add_argument('--expected-status-sha256', help='Required with --apply; status_source.sha256 from reviewed plan')
    parser.add_argument('--reviewed-plan', type=Path, help='Saved JSON output of a clearance-complete dry run; required with --apply')
    parser.add_argument('--expected-plan-sha256', help='SHA-256 of the saved reviewed plan; required with --apply')
    args = parser.parse_args()
    if args.apply:
        if not args.expected_status_sha256 or not args.reviewed_plan or not args.expected_plan_sha256:
            parser.error('--apply requires --expected-status-sha256, --reviewed-plan and --expected-plan-sha256')
        result = apply_transition(batch=args.batch, packages=args.packages, repo=args.repo,
                                  expected_status_sha256=args.expected_status_sha256,
                                  reviewed_plan_path=args.reviewed_plan, expected_plan_sha256=args.expected_plan_sha256,
                                  clearance_path=args.clearance, supplied_reviews=args.interruption_review,
                                  runtime=runtime)
    else:
        status = args.batch.resolve()/'status.json'
        original = status.read_bytes()
        result = build_plan(json.loads(original), status_path=status, status_sha256=digest(original),
                            packages=args.packages, repo=args.repo, clearance_path=args.clearance,
                            supplied_reviews=args.interruption_review, runtime=runtime)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
