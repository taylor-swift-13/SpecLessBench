"""Versioned post-hoc adjudication of final Lean audit rejections.

Default: print a read-only plan. --apply requires a stopped serial controller,
the worker/activity locks, and no running evaluation. It never edits an attempt,
proof, prompt, claim or historical report. Model costs remain unchanged; new host
checking costs are reported separately. No model turn or new attempt is started.
"""
from __future__ import annotations

import argparse
import collections
import contextlib
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid

DEFAULT_REPO = Path('/mnt/c/Users/50635/Documents/Codex/2026-11-03/benchmark-equalbench-wsl')
DEFAULT_BATCH = Path.home()/'.local/share/speclessbench/batches/native-luna-medium'
POLICY_ID = 'lean-native-kernel-replay-v1'
RESOURCE_KEYS = ('input_tokens', 'cached_input_tokens', 'output_tokens')
SOURCE_NAMES = ('TrustedLeanAudit.lean', 'lean_grader_core.py', 'grade_sealed.py',
                'sandbox.py', 'resource_supervisor.py', 'regrade_native_audits.py')


def utc_now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')


def atomic_json(path, value):
    temp = path.with_name(path.name+'.tmp')
    with temp.open('w') as out:
        out.write(json.dumps(value, indent=2, ensure_ascii=False)+'\n')
        out.flush()
        os.fsync(out.fileno())
    temp.replace(path)


def verify_checksums(root):
    """Verify obtainable original checksums without running code from the attempt."""
    root = Path(root)
    manifest = root/'SHA256SUMS'
    if not manifest.is_file() or manifest.is_symlink():
        raise ValueError(f'Missing original checksum manifest: {manifest}')
    checked = 0
    for line in manifest.read_text().splitlines():
        match = re.fullmatch(r'([0-9a-f]{64})  (.+)', line)
        if match is None:
            raise ValueError(f'Invalid original checksum line in {manifest}')
        relative = Path(match[2])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Unsafe original checksum path')
        candidate = root/relative
        if not candidate.is_file() or candidate.is_symlink() or sha(candidate) != match[1]:
            raise ValueError(f'Original evidence checksum mismatch: {candidate}')
        checked += 1
    return {'manifest_sha256': sha(manifest), 'verified_files': checked}


def lean_claim_goal(claim):
    """Same literal renderer as the frozen model runner; no claim repair."""
    if claim == {'claim': 'equivalence'}:
        return 'Task.equivalent'
    if (type(claim) is not dict or set(claim) != {'claim', 'input', 'left', 'right'}
            or claim['claim'] != 'counterexample'):
        raise ValueError('Original claim is not an exact supported literal branch')
    for key in ('input', 'left', 'right'):
        value = claim[key]
        if (type(value) is not list or len(value) > 8192
                or any(type(x) is not int or not -(2**63) <= x < 2**63 for x in value)):
            raise ValueError('Original claim has invalid literal integer lists')
    if claim['left'] == claim['right']:
        raise ValueError('Original counterexample observations are equal')
    def literal(values):
        return '['+', '.join(str(x) if x >= 0 else '('+str(x)+')' for x in values)+']'
    return 'Task.refutationAt '+' '.join(literal(claim[k]) for k in ('input', 'left', 'right'))


def original_report_path(job):
    reports = job.get('reports', [])
    if len(reports) > 1:
        raise ValueError('Multiple authoritative reports would double-count one job')
    if not reports:
        return None
    path = Path(reports[0])
    # A re-adjudicated job must not be silently adjudicated a second time.
    if job.get('adjudications'):
        raise ValueError(f'Existing adjudication needs explicit inspection: {path}')
    return path


def build_plan(state, policy_id=POLICY_ID):
    reviewed = []
    selected = []
    for index, job in enumerate(state['jobs']):
        if job['platform'] != 'lean':
            continue
        path = original_report_path(job)
        if path is None:
            continue
        report = json.loads(path.read_text())
        config = report['configuration']
        if (config['task_id'], config['platform'], config['goal_mode']) != (
                job['task_id'], 'lean', job['goal_mode']):
            raise ValueError(f'Report/job identity mismatch: {path}')
        result = report['result']
        if result['status'] != job['status']:
            raise ValueError(f'Report/job decision mismatch: {path}')
        affected = result['status'] == 'rejected' and result.get('stage') == 'audit'
        row = {'job_index': index, 'task_id': job['task_id'], 'platform': 'lean',
               'goal_mode': job['goal_mode'], 'original_report': str(path),
               'original_report_sha256': sha(path), 'original_result': result,
               'review_action': 'regrade-final-audit-rejection' if affected else
                   ('unchanged-accepted-under-stricter-policy' if result['status'] == 'accepted'
                    else 'unchanged-stage-before-audit-or-incomplete-attempt')}
        if affected:
            log_path = path.parent/'checker.log'
            trace = json.loads(log_path.read_text())
            if len(trace) != 3 or trace[0].get('exit_code') != 0 or trace[1].get('exit_code') != 0:
                raise ValueError(f'Unexpected previous final audit trace: {path}')
            errors = str(trace[-1].get('stderr', ''))
            row['previous_audit_category'] = (
                'official-native-computation-dependency' if '_native.native_decide.ax_' in errors
                else 'sorry-placeholder' if 'sorryAx' in errors else 'other-audit-rejection')
            row['previous_audit_stderr'] = errors
            row['original_checker_log_sha256'] = sha(log_path)
            selected.append(row)
        reviewed.append(row)
    return {'schema_version': 1, 'policy_id': policy_id, 'created_utc': utc_now(),
            'scope': 'All completed authoritative Lean reports; regrade every final audit rejection uniformly',
            'invariants': ['No proof, claim, prompt, task or model run is repaired or rerun',
                           'Previously accepted strict-policy reports satisfy the broader axiom policy',
                           'Earlier-stage failures and timeouts receive no new model time',
                           'Original attempt evidence and cost snapshots are immutable'],
            'reviewed_lean_reports': len(reviewed), 'selected_audit_rejections': len(selected),
            'previous_audit_categories': dict(collections.Counter(
                row.get('previous_audit_category') for row in selected)),
            'review': reviewed, 'selected': selected}


def validate_inputs(row, tree_digest):
    path = Path(row['original_report'])
    if sha(path) != row['original_report_sha256']:
        raise ValueError('Original report changed after planning')
    report = json.loads(path.read_text())
    root = path.parent
    evidence = verify_checksums(root)
    proof = root/'Submission.lean'
    claim_path = root/'claim.json'
    if not proof.is_file() or proof.is_symlink() or sha(proof) != report['proof_sha256']:
        raise ValueError(f'Original submitted proof hash mismatch: {proof}')
    claim = json.loads(claim_path.read_text())
    if claim != report['submission_claim']:
        raise ValueError('Original claim/report mismatch')
    rendered = lean_claim_goal(claim)
    expected_obligation = ('import Task\nnamespace Obligation\ndef goal : Prop := '+rendered+
                           '\nend Obligation\n')
    original_task = root/'private/task'
    task_digest = tree_digest(original_task)
    if task_digest != report['configuration']['task_package_sha256']:
        raise ValueError('Original immutable public package digest mismatch')
    grading = root/'private'/('grading-'+str(report.get('resume_count', 0)))
    if not grading.is_dir():
        raise ValueError(f'Missing original sealed grading snapshot: {grading}')
    if (grading/'Obligation.lean').read_text() != expected_obligation:
        raise ValueError('Original grading obligation does not exactly render the original claim')
    if (root/'Obligation.lean').read_bytes() != (grading/'Obligation.lean').read_bytes():
        raise ValueError('Original protected obligation snapshots differ')
    for name in ('Task.lean', 'Task.olean'):
        if sha(grading/name) != sha(original_task/name):
            raise ValueError('Original grading task snapshot changed')
    evidence.update({'proof_sha256': sha(proof), 'claim_sha256': sha(claim_path),
                     'prompt_sha256': sha(root/'prompt.txt'),
                     'config_sha256': sha(root/'config.json'),
                     'original_public_package_sha256': task_digest,
                     'original_grading_package_sha256': tree_digest(grading),
                     'original_obligation_sha256': sha(grading/'Obligation.lean'),
                     'original_checksums_verified_utc': utc_now()})
    return report, proof, grading, evidence


def checksum_directory(root):
    files = sorted(p for p in root.rglob('*') if p.is_file() and p.name != 'SHA256SUMS')
    (root/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.relative_to(root).as_posix()+'\n' for p in files))


def summarize_reports(reports):
    """Same original-cost aggregation as batch controller, with no regrade costs mixed in."""
    return {'completed': len(reports), 'accepted': sum(r['result']['status'] == 'accepted' for r in reports),
            'tokens': {k: sum((r['resources'].get('tokens') or {}).get(k, 0) for r in reports)
                       for k in RESOURCE_KEYS},
            'missing_usage': sum(r['resources'].get('tokens') is None for r in reports),
            'incomplete_usage': sum(not r['resources'].get('token_usage_complete', False) for r in reports),
            'agent_seconds': sum(r['resources'].get('agent_wall_seconds') or 0 for r in reports),
            'checker_seconds': sum(r['resources'].get('checker_wall_seconds') or 0 for r in reports),
            'wall_seconds': sum(r['resources'].get('total_wall_seconds') or 0 for r in reports),
            'native_turns': sum((r.get('native_goal_session') or {}).get('native_turn_count', 0) for r in reports),
            'agent_memory_peak_bytes': max([r['resources'].get('agent_max_cgroup_memory_peak_bytes') or 0 for r in reports], default=0) or None,
            'checker_memory_peak_bytes': max([r['resources'].get('checker_max_cgroup_memory_peak_bytes') or 0 for r in reports], default=0) or None,
            'billing': None, 'hosted_model_memory': None}


def assert_quiescent(state):
    if any(j['status'] == 'running' for j in state['jobs']):
        raise ValueError('A live evaluation still exists; wait for its natural terminal result')
    ps = subprocess.check_output(['ps', '-eo', 'args'], text=True)
    if any('/opt/goal_client.py' in line or
           ('resource_supervisor.py ' in line and '/runs/evaluation/' in line)
           for line in ps.splitlines()):
        raise ValueError('Evaluation descendants remain live')


def apply_regrade(args):
    import fcntl
    os.umask(0o077)
    repo = args.repo.resolve()
    batch = args.batch.resolve()
    status = batch/'status.json'
    sys.path.insert(0, str(repo/'scripts/pilot'))
    from grade_sealed import grade
    from prepare_evaluation import PACKAGES
    from single_task_runner import tree_digest
    # Holding the controller lock is essential: its in-memory state otherwise
    # overwrites external status repairs at its next 30-second idle save.
    with contextlib.ExitStack() as stack:
        for lock_path in (batch.parent/'worker.lock', PACKAGES/'activity.lock'):
            lock = stack.enter_context(lock_path.open('a'))
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        original_status = status.read_bytes()
        state = json.loads(original_status)
        assert_quiescent(state)
        plan = build_plan(state, args.policy_id)
        if not plan['selected']:
            raise ValueError('No original final audit failures selected')
        revision = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:12]
        output = batch/'adjudications'/revision
        output.mkdir(parents=True, mode=0o700)
        (output/'status.before.json').write_bytes(original_status)
        write_json(output/'plan.json', plan)
        sources = output/'grader-sources'
        sources.mkdir(mode=0o700)
        source_hashes = {}
        # Capture auxiliary audit helpers as well as the direct entry points.
        # They may be added as part of this repair and are part of its trust base.
        source_names = sorted(set(SOURCE_NAMES) | {
            p.name for suffix in ('*.py', '*.lean')
            for p in (repo/'scripts/pilot').glob(suffix) if p.is_file()})
        for name in source_names:
            source = repo/'scripts/pilot'/name
            if name == 'regrade_native_audits.py' and not source.is_file():
                source = Path(__file__)
            if not source.is_file():
                raise ValueError(f'Missing new grader source: {source}')
            data = source.read_bytes()
            (sources/name).write_bytes(data)
            source_hashes[name] = hashlib.sha256(data).hexdigest()
        decisions = []
        status_committed = False
        revised = copy.deepcopy(state)
        try:
            for row in plan['selected']:
                old, proof, grading, evidence = validate_inputs(row, tree_digest)
                directory = output/row['task_id']/('goal-'+row['goal_mode'])
                directory.mkdir(parents=True, mode=0o700)
                trace = []
                started = utc_now()
                clock = time.monotonic()
                result = grade('lean', grading, evidence['original_grading_package_sha256'], proof,
                               timeout=args.stage_timeout, trace=trace)
                elapsed = time.monotonic()-clock
                costs = {'host_checker_wall_seconds': elapsed,
                         'host_checker_peak_bytes': max([((x.get('resources') or {}).get('memory_peak_bytes') or 0)
                                                        for x in trace], default=0) or None,
                         'model_tokens': 0, 'billing': None, 'hosted_model_memory': None,
                         'scope': 'Post-hoc host checking only; excluded from original attempt budget and model costs',
                         'original_total_budget_seconds': old['configuration'].get('total_budget_seconds'),
                         'original_wall_seconds': old['resources'].get('total_wall_seconds'),
                         'counterfactual_new_grader_within_original_budget': None}
                write_json(directory/'checker.log', trace)
                write_json(directory/'resources.json', costs)
                if result['status'] == 'infrastructure-error':
                    raise RuntimeError(f'Post-hoc checking infrastructure failure: {row["task_id"]}: {result}')
                if result['status'] not in ('accepted', 'rejected'):
                    raise RuntimeError(f'Unexpected post-hoc decision: {result}')
                native_audit = copy.deepcopy(result.get('audit_evidence'))
                metadata = {'schema_version': 1, 'kind': 'posthoc-grader-policy-correction',
                            'revision': revision, 'policy_id': args.policy_id,
                            'started_utc': started, 'ended_utc': utc_now(),
                            'original_report': row['original_report'],
                            'original_report_sha256': row['original_report_sha256'],
                            'original_result': old['result'], 'new_result': result,
                            'previous_audit_category': row['previous_audit_category'],
                            'evidence': evidence, 'new_grader_sha256': source_hashes,
                            'native_computation_audit': native_audit,
                            'new_checker_log_sha256': sha(directory/'checker.log'),
                            'posthoc_resources': costs,
                            'original_model_resources_unchanged': True,
                            'original_prompt_and_submission_unchanged': True}
                report = copy.deepcopy(old)
                report['result'] = result
                report['checks'] = {'fixed_goal_gate': 'passed' if len(trace) > 1 and trace[1].get('exit_code') == 0 else 'not-passed-or-not-run',
                                    'axiom_audit': 'passed' if len(trace) == 3 and trace[-1].get('exit_code') == 0 else 'not-passed-or-not-run',
                                    'independent_coqchk': None,
                                    'allowed_axioms': ['propext', 'Classical.choice', 'Quot.sound'],
                                    'native_computation_policy': args.policy_id,
                                    'native_computation_audit': native_audit,
                                    'full_stage_output': 'checker.log'}
                report['adjudication'] = metadata
                assert report['resources'] == old['resources']
                assert report['configuration'] == old['configuration']
                report_path = directory/'report.json'
                write_json(report_path, report)
                write_json(directory/'adjudication.json', metadata)
                checksum_directory(directory)
                job = revised['jobs'][row['job_index']]
                job['original_reports'] = list(job['reports'])
                job['reports'] = [str(report_path)]
                job['status'] = result['status']
                job.setdefault('adjudications', []).append(str(directory/'adjudication.json'))
                decisions.append({'task_id': row['task_id'], 'goal_mode': row['goal_mode'],
                                  'old_result': old['result'], 'new_result': result,
                                  'report': str(report_path), 'posthoc_resources': costs})
                print(json.dumps(decisions[-1]), flush=True)
            if status.read_bytes() != original_status:
                raise RuntimeError('Controller status changed during regrade; no status update committed')
            # Recheck every immutable original checksum after host checking.
            for row in plan['selected']:
                verify_checksums(Path(row['original_report']).parent)
            reports = [json.loads(Path(p).read_text()) for j in revised['jobs'] for p in j['reports']]
            revised['counts'] = dict(collections.Counter(j['status'] for j in revised['jobs']))
            revised['totals'] = summarize_reports(reports)
            revised['by_condition'] = {p+'/'+m: summarize_reports([r for r in reports if
                r['configuration']['platform'] == p and r['configuration']['goal_mode'] == m])
                for p in ('lean', 'rocq') for m in ('off', 'on')}
            revised['grading_policy_revision'] = args.policy_id
            revised['updated_utc'] = utc_now()
            summary = {'revision': revision, 'policy_id': args.policy_id,
                       'scope_manifest': str(output/'plan.json'), 'decisions': decisions,
                       'reviewed_lean_reports': plan['reviewed_lean_reports'],
                       'regraded_audit_rejections': len(decisions),
                       'changed_to_accepted': sum(d['old_result']['status'] != 'accepted' and
                                                  d['new_result']['status'] == 'accepted' for d in decisions),
                       'host_checker_wall_seconds': sum(d['posthoc_resources']['host_checker_wall_seconds'] for d in decisions),
                       'host_checker_peak_bytes': max([d['posthoc_resources']['host_checker_peak_bytes'] or 0 for d in decisions], default=0) or None,
                       'model_tokens': 0, 'billing': None, 'hosted_model_memory': None,
                       'counts_before': copy.deepcopy(state.get('counts')),
                       'counts_after': copy.deepcopy(revised['counts']),
                       'by_condition_before': copy.deepcopy(state.get('by_condition')),
                       'by_condition_after': copy.deepcopy(revised['by_condition']),
                       'status_before_sha256': hashlib.sha256(original_status).hexdigest(),
                       'original_model_costs_unchanged': True}
            revised.setdefault('posthoc_adjudications', []).append(summary)
            write_json(output/'summary.json', summary)
            write_json(output/'status.after.json', revised)
            checksum_directory(output)
            atomic_json(status, revised)
            status_committed = True
            print(json.dumps({'committed': True, 'output': str(output),
                              'changed_to_accepted': summary['changed_to_accepted'],
                              'counts': revised['counts']}), flush=True)
        except BaseException as error:
            write_json(output/'failure.json', {'failed_utc': utc_now(), 'error': type(error).__name__+': '+str(error),
                                               'completed_decisions': decisions, 'status_committed': status_committed})
            checksum_directory(output)
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=DEFAULT_REPO)
    parser.add_argument('--batch', type=Path, default=DEFAULT_BATCH)
    parser.add_argument('--policy-id', default=POLICY_ID)
    parser.add_argument('--stage-timeout', type=int, default=600)
    parser.add_argument('--apply', action='store_true', help='Regrade and atomically update authoritative report pointers; requires stopped worker')
    args = parser.parse_args()
    if args.stage_timeout < 1:
        parser.error('--stage-timeout must be positive')
    if args.apply:
        apply_regrade(args)
    else:
        state = json.loads((args.batch/'status.json').read_text())
        print(json.dumps(build_plan(state, args.policy_id), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
