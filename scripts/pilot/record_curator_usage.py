"""Snapshot this curator chat's actual request metering, separately from evals."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(path, data):
    temporary = path.with_name(path.name+'.tmp')
    temporary.write_bytes(data); temporary.replace(path)


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False)+'\n').encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rollout', type=Path, required=True)
    parser.add_argument('--thread', required=True)
    args = parser.parse_args(); os.umask(0o077)
    private = Path.home()/'.local/share/speclessbench/costs/curator'/args.thread
    private.mkdir(parents=True, exist_ok=True, mode=0o700)
    # Read a fixed, complete-line prefix while the desktop app keeps appending.
    with args.rollout.open('rb') as source:
        raw = source.read(os.fstat(source.fileno()).st_size)
    raw = raw[:raw.rfind(b'\n')+1]
    state_file = private/'source-checkpoint.json'
    if state_file.exists():
        old = json.loads(state_file.read_text())
        if len(raw) < old['prefix_bytes'] or sha(raw[:old['prefix_bytes']]) != old['prefix_sha256']:
            raise ValueError('Curator log is not an extension of the saved prefix; preserve prior evidence')
    contexts = {}; context_rows = []; records = []; totals = Counter(); partitions = {}
    started = {}; intervals = []; latest = None; first = None; offset = 0; seen = set()
    for line in raw.splitlines(keepends=True):
        record = json.loads(line); payload = record.get('payload', {}); timestamp = record.get('timestamp')
        if record['type'] == 'turn_context':
            context = {'source_byte_offset': offset, **record}; context_rows.append(context)
            contexts[payload.get('turn_id')] = context
        elif record['type'] == 'event_msg':
            turn = payload.get('turn_id')
            if payload.get('type') == 'task_started':
                started.setdefault(turn, timestamp)
            elif payload.get('type') in ('task_complete', 'turn_aborted'):
                if turn is None and len(started) == 1:
                    turn = next(iter(started))
                begin = started.pop(turn, None)
                if begin:
                    intervals.append({'turn_id': turn, 'started_utc': begin, 'ended_utc': timestamp, 'status': payload['type']})
        elif record['type'] == 'token_usage_record':
            if payload.get('thread_id') != args.thread:
                raise ValueError('Metering belongs to another thread')
            response = (payload.get('session_id'), payload.get('response_id'))
            if response[1] is not None:
                if response in seen:
                    raise ValueError('Repeated response id; do not double count')
                seen.add(response)
            context = contexts.get(payload.get('turn_id')); config = context['payload'] if context else {}
            key = (config.get('model'), config.get('effort'))
            partition = partitions.setdefault(key, {'configured_model': key[0], 'reasoning_effort': key[1], 'requests': 0, 'usage': Counter()})
            partition['requests'] += 1; partition['usage'].update(payload['usage']); totals.update(payload['usage'])
            records.append({'source_byte_offset': offset, 'configuration_source_byte_offset': context['source_byte_offset'] if context else None, **record})
            latest = record; first = first or record
        offset += len(line)
    if not latest or dict(totals) != latest['payload']['thread_token_usage']:
        raise ValueError('Per-request usage does not match the desktop cumulative counter')
    summary = {'schema_version': 1, 'metering_as_of_utc': latest['timestamp'], 'thread_id': args.thread,
               'scope': 'All model requests in this curator/controller chat, including construction, discussion, reference work and evaluation monitoring. Not construction-only; excludes separately launched Codex reference and evaluation workers.',
               'source': {'kind': 'Codex token_usage_record', 'prefix_bytes': len(raw), 'prefix_sha256': sha(raw)},
               'usage': dict(totals), 'uncached_input_tokens': totals['input_tokens']-totals['cached_input_tokens'],
               'requests': len(records), 'by_configuration': list(partitions.values()),
               'audit': {'request_sum_matches_thread_counter': True, 'duplicate_response_ids': 0,
                         'requests_without_available_model_configuration': sum(p['requests'] for p in partitions.values() if p['configured_model'] is None),
                         'token_count_events_excluded_to_avoid_double_counting': True},
               'timing': {'first_usage_utc': first['timestamp'], 'latest_usage_utc': latest['timestamp'],
                          'closed_turn_intervals': len(intervals), 'open_turns': len(started),
                          'model_inference_wall_seconds': None,
                          'scope': 'Turn intervals retained privately; they include tools and waiting and can overlap subprocess work. Do not add them to agent wall time.'},
               'monetary_cost': None, 'hosted_inference_memory_peak_bytes': None,
               'controller_process_memory_peak_bytes': None,
               'attribution': 'Historical construction-only and per-family allocation remains unresolved; session totals must not be reported as task construction totals.',
               'overlap': 'This session-wide series overlaps earlier construction batch snapshots. Do not add it to the historical construction ledger without request/interval deduplication.',
               'accounting': 'Cached input is a subset of input; reasoning output is a subset of output. Do not add these subsets again.'}
    for name, rows in (('metering.jsonl.gz', records), ('model-contexts.jsonl.gz', context_rows)):
        data = gzip.compress(b''.join((json.dumps(row, ensure_ascii=False)+'\n').encode() for row in rows), mtime=0)
        write(private/name, data); summary.setdefault('private_evidence_sha256', {})[name] = sha(data)
    write(private/'turn-intervals.json', encoded({'closed': intervals, 'open': started}))
    write(private/'summary.json', encoded(summary))
    with (private/'checkpoints.jsonl').open('a') as log:
        log.write(json.dumps(summary)+'\n'); log.flush(); os.fsync(log.fileno())
    write(state_file, encoded({'source': str(args.rollout), 'prefix_bytes': len(raw), 'prefix_sha256': sha(raw)}))
    write(ROOT/'benchmarks/construction/curator-workflow-usage.json', encoded(summary))
    print(json.dumps({'metering_as_of_utc': summary['metering_as_of_utc'], 'requests': summary['requests'], 'usage': summary['usage'], 'audit': summary['audit']}))


if __name__ == '__main__':
    main()
