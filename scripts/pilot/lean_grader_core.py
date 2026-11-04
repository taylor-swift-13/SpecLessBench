"""Internal Lean proof-gate core for vetted, task-specific packages only.

No public task packages are certified yet. The release entry point must not
call this core on pilot tasks until source disclosure and target binding have
been audited. The core generates its own protected proof gate.
"""
import shutil,tempfile
from pathlib import Path
from sandbox import run_isolated,TOOLCHAINS
ROOT=Path(__file__).resolve().parents[2];LEAN=TOOLCHAINS['lean']+'/bin/lean'

def _result(status,stage,detail=None):return {'status':status,'stage':stage,'detail':detail}
def _valid_dir(path):
    path=Path(path)
    return path.is_dir() and not path.is_symlink() and not any(p.is_symlink()for p in path.rglob('*'))
def grade_prepared(package,submission,timeout=90):
    package=Path(package);submission=Path(submission)
    if not _valid_dir(package) or not _valid_dir(submission):return _result('infrastructure-error','input','invalid directory')
    if not (package/'Obligation.olean').is_file():return _result('infrastructure-error','input','incomplete trusted package')
    if any((package/name).exists()for name in ('Gate.lean','Gate.olean','Submission.lean','Submission.olean','TrustedLeanAudit.lean')):
        return _result('infrastructure-error','input','reserved package file')
    if {p.name for p in submission.iterdir()}!={'Submission.lean'} or not (submission/'Submission.lean').is_file():
        return _result('rejected','submission','expected only Submission.lean')
    if (submission/'Submission.lean').stat().st_size>1024*1024:return _result('rejected','submission','source exceeds size limit')
    with tempfile.TemporaryDirectory(prefix='specless-lean-core-')as temp:
        trusted=Path(temp)/'trusted';shutil.copytree(package,trusted)
        (trusted/'Gate.lean').write_text('import Obligation\nimport Submission\ntheorem pilot_checked : Obligation.goal := Submission.solve\n')
        shutil.copyfile(ROOT/'scripts/pilot/TrustedLeanAudit.lean',trusted/'TrustedLeanAudit.lean')
        def run(args,**kwargs):return run_isolated('lean',trusted,submission,args,timeout=timeout,**kwargs)
        compiled=run([LEAN,'-j','1','-t','0','-R','/submission','-o','/work/Submission.olean','/submission/Submission.lean'],collect=['Submission.olean'])
        if compiled['status']!='exited':return _result('infrastructure-error','submission',compiled['status'])
        if compiled['exit_code']!=0:return _result('rejected','submission','Lean did not compile submission')
        sub=compiled['artifacts']['Submission.olean']
        gate=run([LEAN,'-j','1','-t','0','-R','/trusted','-o','/work/Gate.olean','/trusted/Gate.lean'],artifacts={'Submission.olean':sub},collect=['Gate.olean'])
        if gate['status']!='exited':return _result('infrastructure-error','gate',gate['status'])
        if gate['exit_code']!=0:return _result('rejected','gate','submission does not inhabit the protected goal')
        audit=run([LEAN,'-j','1','--run','/trusted/TrustedLeanAudit.lean'],artifacts={'Submission.olean':sub,'Gate.olean':gate['artifacts']['Gate.olean']})
        if audit['status']!='exited':return _result('infrastructure-error','audit',audit['status'])
        if audit['exit_code']==0:return _result('accepted','audit')
        if 'forbidden axioms:' in audit['stderr'] or 'checked theorem does not have the fixed goal type' in audit['stderr']:
            return _result('rejected','audit','unapproved dependency or wrong goal')
        return _result('infrastructure-error','audit','trusted auditor failed')
