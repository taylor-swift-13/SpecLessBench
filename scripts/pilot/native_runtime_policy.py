"""Prospective proof-only runtime and pre-attempt infrastructure holds."""
import hashlib
import json
import os
import subprocess
from pathlib import Path

RUNTIME_SCOPE_REVISION = 'native-proof-runtime-minimal-v1'
LEGACY_RUNTIME_SCOPE_REVISION = 'native-default-plugins-v1'
HOST_STORAGE_FLOOR_BYTES = 5 * 1024**3
RETAINED_STORAGE_CEILING_BYTES = 8 * 1024**3
STUDY_ROOT = Path.home()/'.local/share/speclessbench'
CONFIG_PATH = Path(__file__).with_name('native_proof_runtime_minimal.toml')
RUNTIME_CONFIG_SHA256 = 'c30d41b3f0c260d08b56ff6f2cfab221dcc6623ed1ce309b877f73eb8d179170'


def runtime_config():
    raw = CONFIG_PATH.read_bytes().replace(b'\r\n', b'\n')
    digest = hashlib.sha256(raw).hexdigest()
    if digest != RUNTIME_CONFIG_SHA256:
        raise RuntimeError('Proof runtime preset changed without a reviewed runtime revision')
    return raw.decode('utf-8'), digest


def storage_hold(free_bytes=None):
    if free_bytes is None:
        try:
            fs = os.statvfs('/mnt/c')
            free_bytes = fs.f_bavail * fs.f_frsize
        except OSError as exc:
            return {'kind': 'storage', 'reason': 'Host headroom could not be verified; no attempt started',
                    'error_type': type(exc).__name__}
    if free_bytes < HOST_STORAGE_FLOOR_BYTES:
        return {'kind': 'storage', 'free_bytes': free_bytes,
                'floor_bytes': HOST_STORAGE_FLOOR_BYTES,
                'reason': 'Host C: headroom is below the infrastructure floor; no attempt started'}
    return None


def retained_storage_hold(retained_bytes=None):
    """Admission check between attempts, not a per-model storage budget."""
    if retained_bytes is None:
        try:
            retained_bytes = int(subprocess.check_output(
                ['du', '-sx', '-B1', str(STUDY_ROOT)], stderr=subprocess.PIPE, timeout=30).split()[0])
        except (OSError, ValueError, subprocess.SubprocessError, IndexError) as exc:
            return {'kind': 'storage', 'reason': 'Retained storage could not be verified; no attempt started',
                    'error_type': type(exc).__name__}
    if retained_bytes >= RETAINED_STORAGE_CEILING_BYTES:
        return {'kind': 'storage', 'retained_bytes': retained_bytes,
                'ceiling_bytes': RETAINED_STORAGE_CEILING_BYTES,
                'reason': 'Retained study storage reached the admission ceiling; archive before starting another attempt'}
    return None


def pair_runtime_hold(job, all_jobs, read_report=None):
    """Do not mix a new feature surface with a completed old-mode companion."""
    if job.get('reports'):
        return {'kind': 'runtime', 'reason': 'Selected job already has a canonical report; no repeat authorized'}
    if read_report is None:
        read_report = lambda p: json.loads(Path(p).read_text())
    _, expected_hash = runtime_config()
    for companion in all_jobs:
        if (companion.get('task_id'), companion.get('platform')) != (job.get('task_id'), job.get('platform')):
            continue
        if companion.get('goal_mode') == job.get('goal_mode'):
            continue
        for report_path in companion.get('reports', []):
            try:
                cfg = read_report(report_path)['configuration']
                if not isinstance(cfg, dict):
                    raise ValueError('Companion configuration is not an object')
                if any(cfg.get(key) != companion.get(key) for key in ('task_id', 'platform', 'goal_mode')):
                    raise ValueError('Companion configuration identity does not match its canonical job')
            except (OSError, ValueError, KeyError, TypeError) as exc:
                return {'kind': 'runtime', 'reason': 'Companion runtime could not be verified',
                        'report': str(report_path), 'error_type': type(exc).__name__}
            revision = cfg.get('runtime_scope_revision', LEGACY_RUNTIME_SCOPE_REVISION)
            actual_hash = cfg.get('runtime_config_sha256')
            if revision != RUNTIME_SCOPE_REVISION or actual_hash != expected_hash:
                return {'kind': 'runtime', 'reason': 'Completed companion used a different runtime; a reviewed pair transition is required',
                        'task_id': job['task_id'], 'platform': job['platform'],
                        'companion_goal_mode': companion['goal_mode'], 'report': str(report_path),
                        'companion_runtime_revision': revision, 'companion_runtime_config_sha256': actual_hash,
                        'requested_runtime_revision': RUNTIME_SCOPE_REVISION,
                        'requested_runtime_config_sha256': expected_hash,
                        'automatic_requeue_or_retry': False}
    return None
