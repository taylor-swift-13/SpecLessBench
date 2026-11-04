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
start=time.monotonic();proc=subprocess.Popen(config['argv'],start_new_session=True)
try:code=proc.wait(timeout=config['timeout']);status='exited'
except subprocess.TimeoutExpired:
    os.killpg(proc.pid,signal.SIGKILL);proc.wait();code=None;status='timeout'
result={'status':status,'exit_code':code,'limits':observed,'wall_seconds':time.monotonic()-start,
        'memory_peak_bytes':int(read('memory.peak')),'memory_events':read('memory.events'),
        'cpu_stat':read('cpu.stat'),
        'memory_scope':'cgroup v2 peak through sandbox process exit, including supervisor and sandbox descendants; before final cleanup, not hosted model memory'}
report.write_text(json.dumps(result));raise SystemExit(0)
