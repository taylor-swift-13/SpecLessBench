"""Normalize CLI session-cumulative usage without modifying proof evidence."""
import argparse
import json
from pathlib import Path

KEYS = ('input_tokens', 'cached_input_tokens', 'output_tokens')


def session_tokens(events):
    if not events:
        return None
    if any(b.get(k, 0) < a.get(k, 0) for a, b in zip(events, events[1:]) for k in KEYS):
        raise ValueError('Session usage decreased; manual review required')
    return {k: events[-1].get(k, 0) for k in KEYS}


def main(batch):
    from run_evaluation_wsl import dump, sha, report_markdown
    state = json.loads(batch.read_text())
    corrected = 0
    for job in state['jobs']:
        for name in job.get('reports', []):
            path = Path(name); report = json.loads(path.read_text())
            resources = report['resources']; usage = resources.get('provider_usage_events', [])
            tokens = session_tokens(usage)
            if resources.get('token_accounting') == 'last-session-cumulative-event':
                continue
            audit = {'original_tokens': resources.get('tokens'), 'normalized_tokens': tokens,
                     'method': 'Last CLI session-cumulative usage event; never sum resumed-session snapshots',
                     'report_before_sha256': sha(path.read_bytes()),
                     'events_sha256': sha((path.parent/'events.jsonl').read_bytes())}
            dump(path.parent/'token-accounting-audit.json', audit)
            resources['tokens'] = tokens
            resources['token_accounting'] = 'last-session-cumulative-event'
            dump(path.parent/'resources.json', resources); dump(path, report)
            (path.parent/'report.md').write_text(report_markdown(report))
            files = sorted(f for f in path.parent.iterdir() if f.is_file() and f.name != 'SHA256SUMS')
            (path.parent/'SHA256SUMS').write_text(''.join(sha(f.read_bytes())+'  '+f.name+'\n' for f in files))
            corrected += 1
    print(json.dumps({'reports_normalized': corrected}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', type=Path, required=True)
    main(parser.parse_args().batch)
