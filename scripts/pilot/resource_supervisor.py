"""Trusted cgroup supervisor: untrusted sandbox cannot see its report path."""
import json,os,signal,subprocess,sys,time
from pathlib import Path
config=json.loads(Path(sys.argv[1]).read_text());report=Path(config['report'])
line=next(s for s in Path('/proc/self/cgroup').read_text().splitlines()if s.startswith('0::'))
cg=Path('/sys/fs/cgroup')/line[3:].lstrip('/')
def read(name):return (cg/name).read_text().strip()
observed={'memory_max':read('memory.max'),'pids_max':read('pids.max'),'memory_swap_max':read('memory.swap.max')}
if observed['memory_max']=='max' or int(observed['memory_max'])>config['memory_limit'] or observed['pids_max']=='max' or int(observed['pids_max'])>config['pids_limit'] or observed['memory_swap_max']!='0':
    report.write_text(json.dumps({'status':'limits-not-enforced','limits':observed}));raise SystemExit(125)
start=time.monotonic();deadline=config.get('deadline_monotonic');termination_seconds=0.0
remaining=config['timeout'] if deadline is None else min(config['timeout'],deadline-start)
if remaining<=0:
    code=None;status='timeout'
else:
    proc=subprocess.Popen(config['argv'],start_new_session=True)
    try:
        wait_seconds=remaining if deadline is None else max(0,min(remaining,deadline-time.monotonic()))
        code=proc.wait(timeout=wait_seconds);status='exited'
    except subprocess.TimeoutExpired:
        stopping=time.monotonic()
        os.killpg(proc.pid,signal.SIGKILL);proc.wait();code=None;status='timeout'
        termination_seconds=time.monotonic()-stopping
result={'status':status,'exit_code':code,'limits':observed,'wall_seconds':time.monotonic()-start,
        'child_launched':remaining>0,
        'deadline_monotonic':deadline,'termination_wall_seconds':termination_seconds,
        'deadline_overrun_seconds':max(0,time.monotonic()-deadline) if deadline is not None else None,
        'memory_peak_bytes':int(read('memory.peak')),'memory_events':read('memory.events'),
        'cpu_stat':read('cpu.stat'),
        'memory_scope':'cgroup v2 peak through sandbox process exit, including supervisor and sandbox descendants; before final cleanup, not hosted model memory'}
report.write_text(json.dumps(result));raise SystemExit(0)
