"""Rebuild frozen targets in a separate workspace, never in the pilot sources."""
import hashlib,json,os,subprocess,sys,tarfile
from pathlib import Path
from private_paths import PRIVATE
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'benchmarks/pilot';OUT=ROOT/'_build/pilot-v1/platform-audit'
sys.path.insert(0,str(ROOT/'scripts/pilot'))
from verify_freeze import main as verify
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    verify()
    if OUT.exists():raise SystemExit('Audit workspace exists: retain it; choose a fresh revision instead of deleting evidence.')
    OUT.mkdir(parents=True);work=OUT/'workspace';work.mkdir()
    private=json.loads((PRIVATE/'mapping.json').read_text())
    inputs=private['protected_files'][:]
    for file in ('validator-dependencies.json','audit-inputs.json','audit-extras.json'):
        inputs.extend(json.loads((PRIVATE/file).read_text())['files'])
    paths={r['path']:r['sha256']for r in inputs}
    # Rebuild the historical snapshot from its pinned private archive. Its
    # original path names remain meaningful inside this isolated workspace.
    archive=PRIVATE/'frozen-sources.tar.gz'
    assert sha(archive)==json.loads((P/'manifest.json').read_text())['private_source_archive_sha256']
    with tarfile.open(archive,'r:gz') as tar:
        for name,expected in paths.items():
            target=(work/name).resolve()
            assert target.is_relative_to(work.resolve()),name
            member=tar.getmember(name);assert member.isfile(),name
            data=tar.extractfile(member).read();assert hashlib.sha256(data).hexdigest()==expected,name
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    steps=['build_three_platform.py','export_compcert.py','build_algorithms.py','build_boundaries.py',
      'build_stateful.py','build_systems.py','build_base64.py','build_classics.py','build_graphsuite.py','build_countsort.py']
    rows=[];status='passed'
    try:
        for step in steps:
            print('Checking',step,flush=True);log=OUT/(step+'.log')
            with log.open('wb')as stream:
                result=subprocess.run([sys.executable,'-u',str(work/'scripts/construction'/step)],cwd=work,stdout=stream,stderr=subprocess.STDOUT,timeout=1800)
            rows.append({'step':step,'exit_code':result.returncode,'log_sha256':sha(log)})
            if result.returncode:status='failed';break
        verify()
    except Exception:
        status='failed';raise
    finally:
        report={'schema_version':1,'status':status,'steps':rows,'contexts':71,'platform_instances':213,
          'scope':'fresh-copy source/AST and pending-goal type checking, no final theorem proofs and no CompCert semantic execution',
          'frozen_manifest_sha256':sha(P/'manifest.json'),'audit_inputs_sha256':sha(PRIVATE/'audit-inputs.json')}
        (P/'platform-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    if status!='passed':raise SystemExit('Platform build failed; inspect retained audit workspace log.')
    print('All platform build steps passed; final target proofs were not attempted.')
if __name__=='__main__':main()
