"""Synthetic OS-isolation checks only; not benchmark proof attempts."""
import tempfile
from pathlib import Path
from sandbox import run_isolated
def main():
    with tempfile.TemporaryDirectory(prefix='pilot-sandbox-test-')as tmp:
        root=Path(tmp);trusted=root/'trusted';submission=root/'submission';trusted.mkdir();submission.mkdir()
        (trusted/'fixed').write_text('protected');(submission/'item').write_text('submission')
        code='''import os,socket
assert open('/trusted/fixed').read() == 'protected'
assert not os.path.exists('/home/yangfp/.ssh')
assert not os.path.exists('/mnt/c')
try:
 open('/trusted/fixed','w').write('bad')
 raise AssertionError('trusted writable')
except OSError: pass
s=socket.socket();s.settimeout(1)
try:
 s.connect(('1.1.1.1',53));raise AssertionError('network accessible')
except OSError: pass
print('sandbox checks passed')
'''
        result=run_isolated('lean',trusted,submission,['/usr/bin/python3','-c',code],timeout=20)
        assert result['exit_code']==0,result
        assert int(result['resources']['limits']['pids_max'])==64
        assert result['resources']['memory_peak_bytes']>0
        assert (trusted/'fixed').read_text()=='protected'
        exhausted=run_isolated('lean',trusted,submission,['/usr/bin/python3','-c','while True: pass'],timeout=1)
        assert exhausted['status']=='timeout' or exhausted['exit_code']!=0,exhausted
        (submission/'link').symlink_to('/etc/passwd')
        try:run_isolated('lean',trusted,submission,['/usr/bin/true'],timeout=5)
        except ValueError:pass
        else:raise AssertionError('symlink input was accepted')
        (submission/'link').unlink()
        oom=run_isolated('lean',trusted,submission,['/usr/bin/python3','-c','x=bytearray(256*1024*1024)'],timeout=10,cgroup_memory_bytes=64*1024**2,pids_limit=16)
        assert oom['status']=='exited' and oom['exit_code']!=0,oom
        events=dict(line.split() for line in oom['resources']['memory_events'].splitlines())
        assert int(events['oom_kill'])>=1,oom
        fork_test='''import subprocess
children=[]
try:
 for i in range(32): children.append(subprocess.Popen(['/usr/bin/sleep','10']))
except OSError: print('pids limited')
finally:
 for p in children: p.kill()
 for p in children: p.wait()
'''
        forked=run_isolated('lean',trusted,submission,['/usr/bin/python3','-c',fork_test],timeout=10,pids_limit=12)
        assert forked['exit_code']==0 and 'pids limited' in forked['stdout'],forked
        print('synthetic filesystem, network, timeout, memory and process-limit checks passed')
if __name__=='__main__':main()
