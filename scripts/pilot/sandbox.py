"""Bubblewrap process boundary for pilot grader development.

This is a prototype, not a complete untrusted-agent security boundary: the
shared host kernel and per-task solver packages need independent review.
Never expose curator directories through the `trusted` argument.
"""
import datetime,json,os,resource,signal,subprocess,tempfile,uuid
from pathlib import Path

TOOLCHAINS={
 'lean':'/home/yangfp/.elan/toolchains/leanprover--lean4---v4.34.0',
 'rocq':'/home/yangfp/.opam/qcp-8.20',
 'compcert':'/home/yangfp/.opam/five'}

def _record(platform,result):
    root=Path(__file__).resolve().parents[2];path=root/'benchmarks/construction/pilot-jobs.jsonl'
    row={'schema_version':1,'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'phase':'synthetic-prototype','platform':platform,'status':result.get('status'),
         'exit_code':result.get('exit_code'),'resources':result.get('resources')}
    # Never log proof source, literal task data, curator labels, or sandbox output.
    path.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(row,sort_keys=True)+'\n').encode()
    fd=os.open(path,os.O_APPEND|os.O_CREAT|os.O_WRONLY,0o600)
    try:os.write(fd,data)
    finally:os.close(fd)
    return result

def _clean_dir(path):
    p=Path(path)
    if not p.is_dir() or p.is_symlink():raise ValueError('Expected a real directory')
    if any(q.is_symlink() for q in p.rglob('*')):raise ValueError('Symlinks are not allowed in mounted input directories')
    return p.resolve()

def run_isolated(platform, trusted, submission, argv, timeout=60, memory_bytes=16*1024**3,
                 artifacts=None, collect=None, cgroup_memory_bytes=3*1024**3, pids_limit=64):
    if platform not in TOOLCHAINS:raise ValueError('Unknown toolchain')
    trusted=_clean_dir(trusted);submission=_clean_dir(submission)
    if trusted==submission or trusted in submission.parents or submission in trusted.parents:raise ValueError('Trusted and untrusted directories must not overlap')
    if not argv or not all(isinstance(x,str) and '\0' not in x for x in argv):raise ValueError('Invalid command')
    artifacts=artifacts or {};collect=collect or []
    for name,data in artifacts.items():
        if Path(name).name!=name or name in ('.','..') or not isinstance(data,bytes) or len(data)>32*1024**2:
            raise ValueError('Invalid transferred artifact')
    if any(Path(name).name!=name or name in ('.','..') for name in collect):raise ValueError('Invalid output name')
    tool=TOOLCHAINS[platform]
    with tempfile.TemporaryDirectory(prefix='specless-sandbox-')as root:
        work=Path(root)/'work';work.mkdir();stdout=Path(root)/'stdout';stderr=Path(root)/'stderr'
        for name,data in artifacts.items():(work/name).write_bytes(data)
        cmd=['/usr/bin/bwrap','--unshare-all','--die-with-parent','--new-session',
          '--ro-bind','/usr','/usr','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64',
          '--symlink','usr/bin','/bin','--dir','/home','--dir','/home/yangfp',
          '--dir','/home/yangfp/.elan','--dir','/home/yangfp/.elan/toolchains',
          '--dir','/home/yangfp/.opam','--ro-bind',tool,tool,
          '--dir','/trusted','--ro-bind',str(trusted),'/trusted',
          '--dir','/submission','--ro-bind',str(submission),'/submission',
          '--dir','/work','--bind',str(work),'/work','--tmpfs','/tmp',
          '--dev','/dev','--proc','/proc','--clearenv','--setenv','PATH','/usr/bin:/bin',
          '--setenv','HOME','/tmp','--setenv','LC_ALL','C','--setenv','LEAN_PATH','/trusted:/work',
          '--chdir','/work','--',*argv]
        report=Path(root)/'resource-report.json';config=Path(root)/'supervisor.json'
        config.write_text(json.dumps({'argv':cmd,'timeout':timeout,'memory_limit':cgroup_memory_bytes,
          'pids_limit':pids_limit,'report':str(report)}))
        unit='specless-'+uuid.uuid4().hex+'.scope'
        supervisor=Path(__file__).resolve().parent/'resource_supervisor.py'
        launch=['/usr/bin/systemd-run','--user','--scope','--quiet','--unit',unit,
          '-p',f'MemoryMax={cgroup_memory_bytes}','-p','MemorySwapMax=0','-p',f'TasksMax={pids_limit}',
          '/usr/bin/python3',str(supervisor),str(config)]
        def limits():
            resource.setrlimit(resource.RLIMIT_AS,(memory_bytes,memory_bytes))
            resource.setrlimit(resource.RLIMIT_CPU,(timeout,timeout+1))
            resource.setrlimit(resource.RLIMIT_FSIZE,(128*1024**2,128*1024**2))
            resource.setrlimit(resource.RLIMIT_NOFILE,(128,128))
        with stdout.open('wb')as out,stderr.open('wb')as err:
            proc=subprocess.Popen(launch,stdout=out,stderr=err,start_new_session=True,preexec_fn=limits)
            try:rc=proc.wait(timeout=timeout+15)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGKILL);proc.wait()
                subprocess.run(['/usr/bin/systemctl','--user','stop',unit],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=10)
                return _record(platform,{'status':'supervisor-timeout','exit_code':None,'stdout':'','stderr':''})
        # Explicitly stop any remaining descendants in the temporary scope.
        subprocess.run(['/usr/bin/systemctl','--user','stop',unit],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=10)
        def read(p):
            with p.open('rb')as f:return f.read(1_000_000).decode('utf-8','replace')
        if rc!=0 or not report.is_file():return _record(platform,{'status':'isolation-unavailable','exit_code':rc,'stdout':read(stdout),'stderr':read(stderr)})
        accounting=json.loads(report.read_text())
        if accounting.get('status')=='limits-not-enforced':return _record(platform,{'status':'isolation-unavailable','exit_code':None,'stdout':read(stdout),'stderr':read(stderr),'resources':accounting})
        result_code=accounting['exit_code'];outputs={}
        if result_code==0:
            for name in collect:
                p=work/name
                if p.is_symlink() or not p.is_file() or p.stat().st_size>32*1024**2:raise ValueError('Missing or unsafe output artifact')
                outputs[name]=p.read_bytes()
        return _record(platform,{'status':accounting['status'],'exit_code':result_code,'stdout':read(stdout),'stderr':read(stderr),'artifacts':outputs,'resources':accounting})
