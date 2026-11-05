"""Run one fixed theorem with an offline JSONL-speaking agent in a fresh sandbox.

The agent command runs without network access. It receives the prompt through
the literal {prompt} argument placeholder and sees only /trusted (the task),
/work (a fresh writable directory), and the selected toolchain. Its stdout is
JSONL; it must write /work/Submission.lean. No shell is implicitly invoked.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import platform as host_platform
import re
import subprocess
import time
import uuid
from decimal import Decimal, InvalidOperation
from pathlib import Path

from release_gate import score
from single_task_runner import run_attempt, tree_digest
from sandbox import TOOLCHAINS
from selection import selection

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / '_build/pilot-v1/first-real-task'
DEFAULT_RUNS = Path.home() / '.local/share/speclessbench/runs'
PROMPT = ('Work on the single fixed theorem Obligation.goal in /trusted. '
          'Write /work/Submission.lean defining Submission.solve : Obligation.goal. '
          'Do not use sorry or add axioms. Emit your conversation and tool calls as JSONL on stdout.')
SECRET_KEYS = re.compile(r'(api[_-]?key|secret|password|authorization|access[_-]?token)', re.I)


def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def sha(data): return hashlib.sha256(data).hexdigest()
def dump(path, data): path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def safe_config(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if SECRET_KEYS.search(key): raise ValueError('Credentials must not be placed in the run configuration')
            safe_config(item)
    elif isinstance(value, list):
        for item in value: safe_config(item)
    elif isinstance(value, str) and re.search(r'(?i)(?:sk-[A-Za-z0-9_-]{12,}|bearer\s+\S+)', value):
        raise ValueError('Credentials must not be placed in the run configuration')


def git_revision():
    try: return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True, timeout=10).strip()
    except (OSError, subprocess.SubprocessError): return None

def git_dirty():
    try:return bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT,text=True,timeout=20).strip())
    except (OSError,subprocess.SubprocessError):return None

def checker_summary(platform, stages):
    names=('submission_compile','fixed_goal_gate','axiom_audit') if platform=='lean' else ('submission_compile','fixed_goal_gate','independent_kernel','axiom_audit')
    for name,stage in zip(names,stages):stage['stage']=name
    gate=next((s for s in stages if s['stage']=='fixed_goal_gate'),None)
    audit=next((s for s in stages if s['stage']=='axiom_audit'),None)
    text=((audit.get('stdout') or '')+'\n'+(audit.get('stderr') or '')).strip() if audit else None
    return {'fixed_goal_gate':'passed' if gate and gate['status']=='exited' and gate['exit_code']==0 else 'not_passed_or_not_run',
            'axiom_audit':{'status':('passed' if audit['exit_code']==0 else 'failed') if audit and audit['status']=='exited' else 'not_completed',
                           'allowed_axioms':['propext','Classical.choice','Quot.sound'] if platform=='lean' else [],
                           'auditor_output':text,'output_truncated':audit.get('output_truncated') if audit else None},
            'kernel_check':{'method':'Lean gate compilation and trust-level-zero audit' if platform=='lean' else 'coqchk',
                            'status':('passed' if gate and gate['exit_code']==0 and audit and audit['status']=='exited' and audit['exit_code'] in (0,1) else 'not_completed') if platform=='lean' else ('passed' if any(s['stage']=='independent_kernel' and s['status']=='exited' and s['exit_code']==0 for s in stages) else 'not_completed')}}


def run(task, platform, claim, config_path, output_root=DEFAULT_RUNS, purpose='evaluation'):
    config_bytes=Path(config_path).read_bytes()
    config = json.loads(config_bytes)
    safe_config(config)
    if set(config) - {'agent', 'limits', 'pricing'} or not isinstance(config.get('agent'), dict): raise ValueError('Expected agent, optional limits and pricing')
    agent = config['agent']; command = agent.get('command')
    if not isinstance(command, list) or not command or not all(isinstance(x, str) and '\0' not in x for x in command): raise ValueError('agent.command must be a nonempty argv array')
    limits = config.get('limits', {}); timeout = limits.get('wall_seconds', 120)
    if set(limits) - {'wall_seconds'} or type(timeout) is not int or not 1 <= timeout <= 3600: raise ValueError('wall_seconds must be an integer from 1 to 3600')
    pricing=config.get('pricing')
    if pricing is not None:
        if not isinstance(pricing,dict) or set(pricing)!={'input_usd_per_million','cached_input_usd_per_million','output_usd_per_million','version'}:raise ValueError('Invalid pricing configuration')
        try:
            rates=[Decimal(str(pricing[k])) for k in ('input_usd_per_million','cached_input_usd_per_million','output_usd_per_million')]
            if any(not v.is_finite() or v<0 for v in rates):raise ValueError('Invalid pricing rate')
        except (InvalidOperation,TypeError):raise ValueError('Invalid pricing rate')
    meta = json.loads((BUILD / 'registry.json').read_text())
    if (task, platform, claim) != (meta['pilot_id'], meta['platform'], meta['claim']): raise ValueError('Task, platform, or theorem is not prepared')
    if purpose not in ('evaluation','reference'):raise ValueError('Unknown run purpose')
    if purpose=='evaluation' and task in {x['pilot_id'] for x in selection()[1]}: raise ValueError('The entire factorial family is reference-only, not an evaluation task')
    package = BUILD / 'task'
    if tree_digest(package) != meta['public_sha256']: raise ValueError('Task package digest mismatch')
    command = [arg.replace('{prompt}', PROMPT) for arg in command]
    run_root = Path(output_root)
    if run_root.is_symlink(): raise ValueError('Output directory must not be a symlink')
    run_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    run_parent = run_root / purpose / task / platform / claim
    run_parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    run_dir = run_parent / (dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:12])
    run_dir.mkdir(mode=0o700)
    started = now(); start = time.monotonic(); checker = []; attempt = None; result = None; error = None
    (run_dir / 'prompt.txt').write_text(PROMPT + '\n', encoding='utf-8')
    (run_dir / 'config.source.json').write_bytes(config_bytes)
    dump(run_dir / 'config.json', config)
    events = [{'type':'run_started','time_utc':started,'task':task,'platform':platform,'claim':claim},
              {'type':'prompt','time_utc':started,'content':PROMPT}]
    agent_time = None; checker_time = None
    try:
        t = time.monotonic()
        attempt = run_attempt(platform, package, meta['public_sha256'], command, 'Submission.lean',
                              timeout=timeout, capture_limit_bytes=128*1024*1024, raw_output=True,phase='evaluation-agent')
        agent_time = time.monotonic()-t
        stdout = attempt.get('stdout_bytes'); stderr = attempt.get('stderr_bytes')
        # A timeout before the supervisor returns has no captured bytes: report that gap.
        if stdout is not None: (run_dir / 'agent.stdout').write_bytes(stdout)
        if stderr is not None: (run_dir / 'agent.stderr').write_bytes(stderr)
        parsed = []; malformed = 0
        for line in (stdout or b'').splitlines():
            try:
                entry = json.loads(line)
                if not isinstance(entry, dict): raise ValueError('event is not an object')
                parsed.append(entry);events.append({'type':'agent_event','event':entry})
            except (ValueError, UnicodeDecodeError):
                malformed += 1
                events.append({'type':'unparsed_stdout','raw_utf8':line.decode('utf-8','replace')})
        proof = attempt.get('proof')
        if proof is not None:
            proof_path=run_dir/'Submission.lean';proof_path.write_bytes(proof)
            t=time.monotonic();result=score(task,platform,proof_path,trace=checker,purpose=purpose);checker_time=time.monotonic()-t
        elif attempt['status'] in ('supervisor-timeout','timeout','timed-out'):
            result={'status':'timeout','detail':'agent timed out without a submission'}
        elif attempt['status'] in ('isolation-unavailable',):
            result={'status':'infrastructure-error','detail':'sandbox unavailable'}
        elif attempt.get('status')=='exited' and attempt.get('exit_code') not in (None,0):
            result={'status':'agent-error','detail':'agent process exited unsuccessfully','exit_code':attempt['exit_code']}
        else: result={'status':'rejected','detail':'agent did not produce a safe submission'}
    except Exception as exc:
        error=type(exc).__name__+': '+str(exc);result={'status':'infrastructure-error','detail':error}
        parsed=[];malformed=0
    ended=now(); wall=time.monotonic()-start
    events.append({'type':'run_finished','time_utc':ended,'result':result})
    with (run_dir/'events.jsonl').open('w',encoding='utf-8') as stream:
        for row in events:stream.write(json.dumps(row,ensure_ascii=False)+'\n')
    checks=checker_summary(platform,checker)
    dump(run_dir/'checker.log',checker)
    usage=[e for e in parsed if e.get('type')=='usage']
    session_end=[e for e in parsed if e.get('type')=='session_end']
    transcript_complete=bool(session_end and session_end[-1].get('transcript_complete') is True and not malformed and attempt and attempt.get('status')=='exited' and attempt.get('exit_code')==0 and attempt.get('stdout_bytes') is not None and attempt.get('output_truncated') is False)
    totals=None
    if len(usage)==1 and usage[0].get('scope')=='run_total':
        keys=('input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens','total_tokens')
        if all(usage[0].get(k) is None or (type(usage[0][k]) is int and usage[0][k]>=0) for k in keys):
            totals={k:usage[0].get(k) for k in keys}
    cost=None
    if totals and pricing is not None:
        i,c,o=(totals.get(k) for k in ('input_tokens','cached_input_tokens','output_tokens'))
        if all(type(x) is int for x in (i,c,o)) and c<=i:
            amount=(Decimal(i-c)*rates[0]+Decimal(c)*rates[1]+Decimal(o)*rates[2])/Decimal(1000000)
            cost={'estimated_usd':str(amount),'source':'agent-reported tokens and user-supplied rates; not provider billing','pricing':pricing}
    resources={'wall_seconds':wall,'agent_wall_seconds':agent_time,'checker_wall_seconds':checker_time,
               'agent_sandbox':attempt.get('resources') if attempt else None,'checker_stages':[x.get('resources') for x in checker],
               'usage_events':usage,'usage_source':'agent-reported, not independently verified' if usage else None,
               'token_totals':totals,'monetary_cost':cost,'hosted_inference_memory_bytes':None,
               'unavailable_reason':'Usage is self-reported; verified provider billing and hosted inference telemetry are unavailable.'}
    dump(run_dir/'resources.json',resources)
    metadata={k:agent.get(k) for k in ('name','version','model_provider','model_name','model_version','reasoning_effort','temperature')}
    metadata['configured']=agent
    report={'schema_version':1,'run_id':run_dir.name,'purpose':purpose,'started_utc':started,'ended_utc':ended,
            'task':{'id':task,'platform':platform,'claim':claim,'theorem':'Obligation.goal','package_sha256':meta['public_sha256'],'benchmark_commit':git_revision(),'benchmark_tracked_files_dirty':git_dirty()},
            'agent':metadata,'limits':{'wall_seconds':timeout,'network':'disabled','memory_cgroup_bytes':3*1024**3,'pids_limit':64},
            'environment':{'system':host_platform.platform(),'toolchain':'Lean 4.34.0' if platform=='lean' else None,
                           'toolchain_executable_sha256':sha((Path(TOOLCHAINS[platform])/'bin/lean').read_bytes()) if platform=='lean' else None},
            'prompt_sha256':sha(PROMPT.encode()),'config_source_sha256':sha(config_bytes),'result':result,'checks':checks,'resources':resources,
            'transcript':{'agent_reported_complete':transcript_complete,'completeness_independently_verified':False,
                          'invalid_jsonl_lines':malformed,'output_truncated':attempt.get('output_truncated') if attempt else None,
                          'raw_output_available':bool(attempt and attempt.get('stdout_bytes') is not None),
                          'reason':'Only events emitted by the agent are observable; hidden model reasoning and omitted tool calls cannot be recovered.'},
            'submission_sha256':sha((run_dir/'Submission.lean').read_bytes()) if (run_dir/'Submission.lean').is_file() else None,
            'notes':['This runner supports only locally available offline agents. Agent-provided metadata and usage are self-reported.','Checker logs may be truncated; each stage reports its truncation status.']}
    dump(run_dir/'report.json',report)
    (run_dir/'report.md').write_text('# Evaluation report\n\n'+f'- Task: `{task}` ({platform}, {claim})\n- Result: **{result["status"]}**\n- Agent: `{agent.get("name", "unknown")}`\n- Wall time: {wall:.3f} s\n- Agent-reported transcript complete: {transcript_complete}\n- Token usage and monetary cost: see resources.json; not independently verified\n',encoding='utf-8')
    return run_dir,report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task',required=True);parser.add_argument('--platform',required=True,choices=('lean','rocq','compcert'))
    parser.add_argument('--claim',required=True,choices=('equivalence','counterexample'));parser.add_argument('--config',required=True)
    parser.add_argument('--output-root',default=str(DEFAULT_RUNS))
    parser.add_argument('--reference',action='store_true',help='Run a reference-only task outside the evaluation set')
    args=parser.parse_args();directory,report=run(args.task,args.platform,args.claim,args.config,args.output_root,purpose='reference' if args.reference else 'evaluation')
    print(json.dumps({'run_dir':str(directory),'status':report['result']['status']}))
    raise SystemExit(0 if report['result']['status']=='accepted' else 1)


if __name__=='__main__':main()
