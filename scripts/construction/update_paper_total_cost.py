"""Refresh the paper's partial cost ledger from the audited JSON snapshot."""
import json
from pathlib import Path
from accounting import ROOT
ledger=json.loads((ROOT/'benchmarks/construction/total-cost.json').read_text(encoding='utf-8'))
t=ledger['token_observation']['provider_interval_union'];w=ledger['time_observation'];m=ledger['memory_observation']
cutoff=max(row['provider_interval_end_utc'] for row in ledger['batch_records']).replace('T',' ').replace('Z',' UTC')
def num(x):return format(x,',')
def hours(s):return f'{s/3600:.2f}'
job_peak=m.get('max_observed_pilot_job_cgroup_peak_bytes')
job_sentence=(f"The largest observed isolated pilot-job cgroup peak is {job_peak/(1024**3):.2f} GiB through sandbox process exit, including its supervisor. " if job_peak is not None else '')
body=rf'''% BEGIN AUTO CONSTRUCTION COST LEDGER
\paragraph{{Observed project-level ledger.}} As of {cutoff}, the deduplicated ledger covers {ledger['batch_count']} recorded batch snapshots, including construction-related research and the cost audit itself. The recorded request-window union is {hours(w['request_window_union_seconds'])} hours, including waiting and idle time; separately, the union of instrumented command intervals is {hours(w['instrumented_command_window_union_seconds'])} hours. Provider counters over the observed interval union report {num(t['total_tokens'])} total tokens: {num(t['input_tokens'])} input tokens, of which {num(t['cached_input_tokens'])} are cached, and {num(t['output_tokens'])} output tokens, including {num(t['reasoning_output_tokens'])} reasoning tokens. The largest observed single-process high-water RSS is {m['max_observed_single_process_rss_bytes']/(1024**3):.2f} GiB. {job_sentence}We merge overlapping intervals within each session and do not multiply shared authoring costs by tasks or ports.

These are \emph{{observed partial records}}, not a complete benchmark construction time, token bill or memory peak: historical activity and post-snapshot tails are missing; conversation windows may include work that cannot be uniquely attributed; and a process high-water mark does not measure concurrent tree or hosted model memory. A final total must be reported only after the release cutoff and the remaining telemetry gaps are resolved or explicitly reported as unknown. The machine-readable ledger retains batch sources, snapshot cutoffs and completeness flags.
% END AUTO CONSTRUCTION COST LEDGER'''
p=ROOT/'paper/main.tex';text=p.read_text(encoding='utf-8');start=text.index('% BEGIN AUTO CONSTRUCTION COST LEDGER');end=text.index('% END AUTO CONSTRUCTION COST LEDGER',start)+len('% END AUTO CONSTRUCTION COST LEDGER')
p.write_text(text[:start]+body+text[end:],encoding='utf-8',newline='\n')
print('Updated paper cost ledger through',cutoff)
