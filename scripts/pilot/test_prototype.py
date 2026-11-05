"""Run independent synthetic grader security regressions; never prove tasks."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'benchmarks/pilot';rows=[]
for name in ('test_sandbox.py','test_sandboxed_lean_gate.py','test_lean_grader_core.py','test_rocq_grader_core.py','test_release_gate.py','test_selection.py'):
    script=ROOT/'scripts/pilot'/name
    print('Running',name,flush=True)
    result=subprocess.run([sys.executable,'-u',str(script)],cwd=ROOT,capture_output=True,text=True,timeout=600)
    rows.append({'test':name,'script_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),
                 'exit_code':result.returncode,'output':result.stdout[-4000:]})
    if result.returncode:raise SystemExit(result.stdout+'\n'+result.stderr)
report={'schema_version':1,'status':'synthetic-tests-passed','tests':rows,
 'components':[{'path':name,'sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest()}
    for name in ('scripts/pilot/sandbox.py','scripts/pilot/resource_supervisor.py','scripts/pilot/TrustedLeanAudit.lean','scripts/pilot/lean_grader_core.py','scripts/pilot/rocq_grader_core.py','scripts/pilot/release_gate.py','scripts/pilot/selection.py','benchmarks/pilot/evaluation-policy.json','scripts/pilot/test_prototype.py')],
 'scope':'these regression tests use toy propositions and OS boundary probes only',
 'job_telemetry':'benchmarks/construction/pilot-jobs.jsonl',
 'release_ready':False,'limitations':['only factorial Lean reference branches have solver packages; evaluation tasks and other platforms are not integrated',
    'Rocq assumptions text and loader require adversarial review',
    'user-scoped cgroup availability and kernel security vary by deployment; fallback must fail closed',
    'bwrap and shared host kernel are not a complete hostile-code security boundary']}
(OUT/'grader-prototype.json').write_text(json.dumps(report,indent=2)+'\n')
print('Synthetic prototype regressions passed; pilot grader not released.')
