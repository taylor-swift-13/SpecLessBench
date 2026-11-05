"""Run one prepared Lean goal with Codex in WSL and keep a private report.

Codex may contact its model service. Its tools run under a second sandbox that
denies network and access to the temporary Codex authentication directory.
"""
import datetime as dt
import hashlib
import json
import os
import platform
import resource as process_resource
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import uuid
from pathlib import Path

from release_gate import score
from single_task_runner import tree_digest

ROOT=Path(__file__).resolve().parents[2]
TASK=ROOT/'_build/pilot-v1/first-real-task'
BASE=Path.home()/'.local/share/speclessbench/runs'
AUTH=Path.home()/'.codex/auth.json'
CODEX=Path.home()/'.nvm/versions/node/v20.17.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex'
CODE_HOST=CODEX.parent/'codex-code-mode-host'
LEAN=Path.home()/'.elan/toolchains/leanprover--lean4---v4.34.0'
SUPERVISOR=ROOT/'scripts/pilot/resource_supervisor.py'
TIMEOUT=3600
PROMPT=('Prove the one fixed Lean theorem Obligation.goal. The task source and compiled '
        'dependencies are in /task. Work only in /work. Create /work/Submission.lean '
        'which imports Obligation and defines Submission.solve : Obligation.goal. '
        'You may create helper lemmas in that file. Do not use sorry or add axioms. '
        'The checker recompiles against the fixed task and audits proof dependencies.')
ACTIVE_RUN=None


def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def dump(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(data):return hashlib.sha256(data).hexdigest()


def fingerprint_tree(root):
    """Fingerprint exact file bytes and symlink targets without loading the tree."""
    h=hashlib.sha256(b'SpecLessBench toolchain tree v1\0');files=0;size=0
    for path in sorted(root.rglob('*')):
        name=path.relative_to(root).as_posix().encode()
        if path.is_symlink():
            h.update(b'L'+len(name).to_bytes(8,'big')+name+os.readlink(path).encode()+b'\0')
        elif path.is_file():
            before=path.stat();h.update(b'F'+len(name).to_bytes(8,'big')+name+before.st_size.to_bytes(8,'big'))
            with path.open('rb') as f:
                for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
            after=path.stat()
            if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise RuntimeError('Toolchain changed during fingerprint')
            files+=1;size+=before.st_size
    return {'sha256':h.hexdigest(),'file_count':files,'total_bytes':size,'scheme':'SpecLessBench toolchain tree v1'}


def main():
    global ACTIVE_RUN
    os.umask(0o077)
    preflight_started=now();preflight_clock=time.monotonic()
    proxies=[]
    for key in ('HTTP_PROXY','HTTPS_PROXY','NO_PROXY','http_proxy','https_proxy','no_proxy'):
        value=os.environ.get(key)
        if value:
            parsed=urllib.parse.urlsplit(value)
            if parsed.username or parsed.password:raise RuntimeError('Credential-bearing proxy values are not supported')
            proxies.extend(['--setenv',key,value])
    meta=json.loads((TASK/'registry.json').read_text())
    if (meta['platform'],meta['claim'])!=('lean','equivalence'):raise SystemExit('Wrong prepared theorem')
    if tree_digest(TASK/'task')!=meta['public_sha256']:raise SystemExit('Task digest mismatch')
    if not AUTH.is_file() or not CODEX.is_file() or not CODE_HOST.is_file():raise SystemExit('WSL Codex authentication, executable, or code-mode host unavailable')
    subprocess.run([sys.executable,str(ROOT/'scripts/pilot/verify_freeze.py')],cwd=ROOT,check=True,stdout=subprocess.DEVNULL,timeout=120)
    subprocess.run([sys.executable,str(ROOT/'scripts/pilot/verify_audit.py')],cwd=ROOT,check=True,stdout=subprocess.DEVNULL,timeout=120)
    BASE.mkdir(mode=0o700,parents=True,exist_ok=True)
    run=BASE/(dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:12]);run.mkdir(mode=0o700)
    ACTIVE_RUN=run
    print('RUN_DIR='+str(run),flush=True)
    private=run/'private';private.mkdir(mode=0o700);home=private/'codex-home';home.mkdir(mode=0o700)
    work=private/'work';work.mkdir(mode=0o700);task=private/'task';shutil.copytree(TASK/'task',task)
    if tree_digest(task)!=meta['public_sha256']:raise SystemExit('Task changed while copying')
    (home/'auth.json').touch(mode=0o600)
    config='''default_permissions = "eval"
approval_policy = "never"
model = "gpt-6-luna"
model_reasoning_effort = "medium"
web_search = "disabled"
[features]
apps = false
memories = false
[permissions.eval]
extends = ":workspace"
[permissions.eval.filesystem]
"/home/runner/.codex/auth.json" = "deny"
[permissions.eval.network]
enabled = false
'''
    (home/'config.toml').write_text(config)
    (run/'codex-config.toml').write_text(config)
    (run/'prompt.txt').write_text(PROMPT+'\n')
    commit_before=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    status_raw=subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT,text=True).splitlines()
    status_normalized=subprocess.check_output(['git','-c','core.autocrlf=true','status','--porcelain','--untracked-files=no'],cwd=ROOT,text=True).splitlines()
    dirty_before=bool(status_raw)
    t=time.monotonic();lean_tree=fingerprint_tree(LEAN);lean_tree['wall_seconds']=time.monotonic()-t
    catalog_result=subprocess.run([str(CODEX),'debug','models'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
    try:
        catalog=json.loads(catalog_result.stdout);models=catalog.get('models',[]) if isinstance(catalog,dict) else catalog
        selected=[m for m in models if m.get('slug')=='gpt-6-luna']
    except (ValueError,AttributeError):selected=[]
    catalog_evidence={'captured_utc':now(),'command':'codex debug models','exit_code':catalog_result.returncode,
                      'raw_catalog_sha256':sha(catalog_result.stdout),
                      'selected_models':[{k:m.get(k) for k in ('slug','display_name','default_reasoning_level','supported_reasoning_levels','context_window')} for m in selected],
                      'scope':'CLI catalog observation, possibly cached; not evidence of the model resolved by a particular response'}
    if catalog_result.returncode!=0 or len(selected)!=1 or not any(x.get('effort')=='medium' for x in selected[0].get('supported_reasoning_levels',[])):
        raise RuntimeError('The requested model and effort are absent from the observed CLI catalog')
    dump(run/'model-catalog.json',catalog_evidence)
    critical=('scripts/pilot/run_codex_wsl.py','scripts/pilot/release_gate.py','scripts/pilot/grade_sealed.py',
              'scripts/pilot/lean_grader_core.py','scripts/pilot/TrustedLeanAudit.lean','scripts/pilot/sandbox.py',
              'scripts/pilot/resource_supervisor.py','scripts/pilot/single_task_runner.py','scripts/pilot/prepare_factorial.py',
              'scripts/pilot/verify_reference.py','benchmarks/tasks/algorithms-core/lean/BasicNative.lean',
              'benchmarks/tasks/algorithms-core/lean/BasicDomain.lean','benchmarks/proof-interface/v1/lean/BranchTargets.lean')
    critical_hashes={name:sha((ROOT/name).read_bytes()) for name in critical}
    for name,observed in critical_hashes.items():
        committed=sha(subprocess.check_output(['git','show',commit_before+':'+name],cwd=ROOT))
        if observed!=committed:raise RuntimeError('Critical file differs from committed version: '+name)
    environment={'preflight_started_utc':preflight_started,'preflight_wall_seconds':time.monotonic()-preflight_clock,
                 'controller_peak_rss_bytes_linux':process_resource.getrusage(process_resource.RUSAGE_SELF).ru_maxrss*1024,
                 'lean_toolchain_tree':lean_tree,'critical_file_sha256':critical_hashes,
                 'git_status_raw':status_raw,'git_status_autocrlf_true':status_normalized,
                 'full_environment_locked':False,'limitations':'The OS, system libraries and model backend are not locked; the tree digest does not distribute binaries.'}
    dump(run/'environment.json',environment)
    settings={'model':'gpt-6-luna','model_reasoning_effort':'medium','agent':'Codex CLI',
              'agent_version':subprocess.check_output([str(CODEX),'--version'],text=True).strip(),
              'timeout_seconds':TIMEOUT,'tools_network':False,'model_network':True,
              'memory_limit_bytes':3*1024**3,'pids_limit':512,
              'task_id':meta['pilot_id'],'platform':'lean','claim':'equivalence',
              'theorem':'Obligation.goal','task_package_sha256':meta['public_sha256'],
              'provider':'ChatGPT account; billing and hosted-model memory unavailable',
              'runner_sha256':sha(Path(__file__).read_bytes()),
              'codex_executable_sha256':sha(CODEX.read_bytes()),
              'codex_code_host_sha256':sha(CODE_HOST.read_bytes()),
              'lean_executable_sha256':sha((LEAN/'bin/lean').read_bytes()),
              'system':platform.platform(),
              'lean_version':subprocess.check_output([str(LEAN/'bin/lean'),'--version'],text=True).strip()}
    dump(run/'config.json',settings)
    cmd=['/usr/bin/bwrap','--unshare-all','--share-net','--die-with-parent','--new-session',
         '--ro-bind','/usr','/usr','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--symlink','usr/bin','/bin',
         '--dir','/etc','--ro-bind','/etc/resolv.conf','/etc/resolv.conf','--ro-bind','/etc/hosts','/etc/hosts',
         '--ro-bind','/etc/nsswitch.conf','/etc/nsswitch.conf','--ro-bind','/etc/ssl','/etc/ssl',
         '--dir','/home','--dir','/home/runner','--dir','/home/runner/.codex','--bind',str(home),'/home/runner/.codex',
         '--ro-bind',str(AUTH),'/home/runner/.codex/auth.json',
         '--dir','/opt','--ro-bind',str(CODEX),'/opt/codex','--ro-bind',str(CODE_HOST),'/opt/codex-code-mode-host','--symlink','codex','/opt/codex-linux-sandbox',
         '--ro-bind',str(LEAN),'/opt/lean','--ro-bind',str(task),'/task','--bind',str(work),'/work',
         '--tmpfs','/tmp','--dev','/dev','--proc','/proc','--clearenv',
         '--setenv','HOME','/home/runner','--setenv','CODEX_HOME','/home/runner/.codex',
         '--setenv','PATH','/opt:/opt/lean/bin:/usr/bin:/bin','--setenv','LEAN_PATH','/task:/work',
         '--setenv','LANG','C.UTF-8','--setenv','TOKIO_WORKER_THREADS','4','--setenv','RAYON_NUM_THREADS','4']
    cmd+=proxies
    cmd+=['--chdir','/work','--',
         '/opt/codex','exec','--ephemeral','--skip-git-repo-check','--json','-C','/work',PROMPT]
    resource=private/'resource.json';supervisor_config=private/'supervisor.json'
    supervisor_config.write_text(json.dumps({'argv':cmd,'timeout':TIMEOUT,'memory_limit':3*1024**3,'pids_limit':512,'report':str(resource)}))
    unit='specless-online-'+uuid.uuid4().hex+'.scope'
    launch=['/usr/bin/systemd-run','--user','--scope','--quiet','--unit',unit,'-p','MemoryMax=3221225472',
            '-p','MemorySwapMax=0','-p','TasksMax=512','/usr/bin/python3',str(SUPERVISOR),str(supervisor_config)]
    started=now();t=time.monotonic()
    try:
        with (run/'events.jsonl').open('wb') as out,(run/'events.timestamps.jsonl').open('w',encoding='utf-8') as timestamps,(run/'agent.stderr').open('wb') as err:
            proc=subprocess.Popen(launch,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=err,start_new_session=True)
            def capture():
                for index,line in enumerate(proc.stdout):
                    out.write(line);out.flush()
                    timestamps.write(json.dumps({'line':index+1,'received_utc':now()})+'\n');timestamps.flush()
            reader=threading.Thread(target=capture,daemon=True);reader.start()
            try:exit_code=proc.wait(timeout=TIMEOUT+30)
            except subprocess.TimeoutExpired:
                subprocess.run(['/usr/bin/systemctl','--user','stop',unit],timeout=15,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                proc.kill();proc.wait();exit_code=None
            reader.join(timeout=15)
            if reader.is_alive():
                subprocess.run(['/usr/bin/systemctl','--user','stop',unit],timeout=15,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                reader.join(timeout=5)
            stream_complete=not reader.is_alive()
    finally:
        subprocess.run(['/usr/bin/systemctl','--user','stop',unit],timeout=15,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        (home/'auth.json').unlink(missing_ok=True)
    elapsed=time.monotonic()-t;resources=json.loads(resource.read_text()) if resource.is_file() else None
    lines=(run/'events.jsonl').read_bytes().splitlines();events=[];invalid=0
    for line in lines:
        try:events.append(json.loads(line))
        except (ValueError,UnicodeDecodeError):invalid+=1
    usage=[x.get('usage') for x in events if isinstance(x,dict) and x.get('type')=='turn.completed' and x.get('usage')]
    proof=work/'Submission.lean';trace=[];checking_started=time.monotonic()
    proof_exists=proof.is_file() and not proof.is_symlink()
    if proof_exists:target=run/'Submission.lean';shutil.copyfile(proof,target)
    if not resources or resources.get('status')=='limits-not-enforced':outcome={'status':'infrastructure-error','detail':'Sandbox supervision unavailable'}
    elif resources.get('status')=='timeout':outcome={'status':'timeout','detail':'Agent exceeded time limit'}
    elif resources.get('status')!='exited' or resources.get('exit_code')!=0:outcome={'status':'agent-error','detail':'Agent process did not exit successfully'}
    elif not any(isinstance(x,dict) and x.get('type')=='turn.completed' for x in events):outcome={'status':'agent-error','detail':'Agent turn did not complete'}
    elif proof_exists:outcome=score(meta['pilot_id'],'lean',target,trace=trace)
    else:outcome={'status':'agent-error','detail':'No submission was produced'}
    checking_elapsed=time.monotonic()-checking_started
    for name,row in zip(('submission_compile','fixed_goal_gate','axiom_audit'),trace):row['stage']=name
    dump(run/'checker.log',trace)
    audit=next((row for row in trace if row.get('stage')=='axiom_audit'),None)
    report={'schema_version':1,'started_utc':started,'ended_utc':now(),'configuration':settings,
            'benchmark_commit':commit_before,'tracked_files_dirty_at_start':dirty_before,
            'result':outcome,'proof_sha256':sha((run/'Submission.lean').read_bytes()) if (run/'Submission.lean').is_file() else None,
            'checks':{'fixed_goal_gate':'passed' if len(trace)>1 and trace[1].get('exit_code')==0 else 'not_passed_or_not_run',
                      'axiom_audit':{'status':'passed' if audit and audit.get('exit_code')==0 else 'not_passed_or_not_run',
                                     'allowed':['propext','Classical.choice','Quot.sound'],
                                     'auditor_output':((audit.get('stdout') or '')+'\n'+(audit.get('stderr') or '')).strip() if audit else None}},
            'resources':{'wall_seconds':elapsed,'checker_seconds':checking_elapsed,'sandbox':resources,
                         'preflight':{'wall_seconds':environment['preflight_wall_seconds'],'controller_peak_rss_bytes_linux':environment['controller_peak_rss_bytes_linux']},
                         'provider_usage_events':usage,'usage_scope':'Codex CLI turn.completed events; no assumed billing conversion',
                         'monetary_cost':None,'hosted_inference_memory_bytes':None},
            'transcript':{'format':'Codex CLI --json','event_count':len(events),'invalid_lines':invalid,
                          'turn_completed':bool(any(isinstance(x,dict) and x.get('type')=='turn.completed' for x in events)),
                          'completeness_independently_verified':False,
                          'line_received_timestamps':'events.timestamps.jsonl','stdout_stream_closed_cleanly':stream_complete,
                          'limitations':'Complete means a turn.completed event was observed, not that all hidden reasoning or tool details are independently recoverable.'},
            'supervisor_exit_code':exit_code,'model_configuration_source':'Codex config and CLI catalog; server-side resolved model metadata not independently verified',
            'environment_evidence':'environment.json','model_catalog_evidence':'model-catalog.json'}
    dump(run/'report.json',report)
    (run/'report.md').write_text('# Evaluation report\n\n'+f'- Task: `{meta["pilot_id"]}` (Lean equivalence)\n- Model: `gpt-6-luna`, medium; Codex {settings["agent_version"]}\n- Result: **{outcome["status"]}**\n- Axiom audit: {report["checks"]["axiom_audit"]["auditor_output"] or "not completed"}\n- Agent / checker wall time: {elapsed:.2f} / {checking_elapsed:.2f} s\n- Agent cgroup memory peak: {resources.get("memory_peak_bytes") if resources else "unknown"} bytes\n- Token usage: {json.dumps(usage,ensure_ascii=False)}\n- Turn completed: {report["transcript"]["turn_completed"]}\n- Monetary cost and hosted-model memory: unknown\n')
    dump(run/'resources.json',report['resources'])
    print(json.dumps({'run_dir':str(run),'result':outcome,'elapsed_seconds':elapsed}),flush=True)
    return 0 if outcome['status']=='accepted' else 1


if __name__=='__main__':
    try:code=main()
    except Exception as exc:
        if ACTIVE_RUN is not None and not (ACTIVE_RUN/'report.json').exists():
            failure={'schema_version':1,'result':{'status':'infrastructure-error','detail':type(exc).__name__+': '+str(exc)},
                     'ended_utc':now(),'transcript':{'complete':False,'reason':'run did not reach normal report finalization'}}
            dump(ACTIVE_RUN/'report.json',failure)
            (ACTIVE_RUN/'report.md').write_text('# Evaluation report\n\n- Result: infrastructure-error\n- Details: see report.json\n')
        print(type(exc).__name__+': '+str(exc),file=sys.stderr)
        code=2
    sys.exit(code)
