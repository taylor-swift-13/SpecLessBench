"""Regenerate and check all explicit branch target modules in the audit copy."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
from private_paths import PRIVATE
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'benchmarks/pilot-v1';OUT=ROOT/'_build/pilot-v1/platform-audit';W=OUT/'workspace'
sys.path.insert(0,str(ROOT/'scripts/pilot'))
from verify_freeze import main as verify
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    verify();platform=json.loads((P/'platform-audit.json').read_text());assert platform['status']=='passed'
    ast=json.loads((P/'ast-audit.json').read_text());assert ast['byte_identical_count']==103
    steps=['prepare_branch_targets.py','prepare_boundary_targets.py','prepare_stateful_targets.py',
       'prepare_systems_targets.py','prepare_base64_targets.py','prepare_classics_targets.py',
       'prepare_graphsuite_targets.py','prepare_countsort_targets.py']
    rows=[];env=dict(os.environ,LEAN_PATH=str(W/'_build/three-platform/lean'))
    for step in steps:
        print('Checking',step,flush=True);log=OUT/(step+'.log')
        with log.open('wb')as stream:
            result=subprocess.run([sys.executable,'-u',str(W/'scripts/construction'/step)],cwd=W,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=1800)
        rows.append({'step':step,'exit_code':result.returncode,'log_sha256':sha(log)})
        if result.returncode:raise SystemExit('Interface audit failed; inspect '+str(log))
    manifest=json.loads((W/'benchmarks/proof-interface/v1/manifest.json').read_text())
    assert len(manifest['contexts'])==71
    private=json.loads((PRIVATE/'mapping.json').read_text())
    expected=[r for r in private['protected_files'] if r['path'].startswith('benchmarks/proof-interface/v1/') and Path(r['path']).suffix in ('.v','.lean')]
    bad=[r['path'] for r in expected if sha(W/r['path'])!=r['sha256']]
    (PRIVATE/'interface-mismatches.json').write_text(json.dumps(bad,indent=2)+'\n')
    assert not bad,'Generated interface source differs from frozen snapshot.'
    verify()
    report={'schema_version':1,'status':'passed','contexts':71,'platform_instances':213,
      'protected_interface_files_checked':len(expected),'steps':rows,'frozen_manifest_sha256':sha(P/'manifest.json'),
      'scope':'explicit branch target modules type-checked on all three platforms; no final theorem proof or CompCert semantic execution'}
    (P/'interface-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print('All 71 branch interfaces checked on three platforms; no final proofs.')
if __name__=='__main__':main()
