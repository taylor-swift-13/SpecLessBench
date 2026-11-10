"""Lean proof gate for vetted source-bound packages and a protected exact goal.

Standard axioms are allowed. Native-decide-shaped closed computation facts are
accepted only after the trusted auditor independently proves them by kernel
reduction; their names alone do not establish provenance or acceptance.
"""
import json,shutil,tempfile
from pathlib import Path
from sandbox import run_isolated,TOOLCHAINS
AUDITOR=Path(__file__).with_name('TrustedLeanAudit.lean');LEAN=TOOLCHAINS['lean']+'/bin/lean'
LEAN_GRADING_POLICY = 'lean-native-kernel-replay-v1'
STANDARD_AXIOMS = ('propext', 'Classical.choice', 'Quot.sound')

def _result(status,stage,detail=None,**extra):
    return {'status':status,'stage':stage,'detail':detail,
            'grading_policy':LEAN_GRADING_POLICY,**extra}

def audit_evidence(stdout):
    """Read only the trusted auditor's exact, versioned success record."""
    records=[line[len('native_audit: '):] for line in stdout.splitlines()
             if line.startswith('native_audit: ')]
    if len(records)!=1:
        raise ValueError('Expected one trusted native-audit record')
    value=json.loads(records[0])
    if type(value) is not dict or value.get('policy')!=LEAN_GRADING_POLICY:
        raise ValueError('Unknown native-audit policy')
    if (value.get('verification')!='independent-kernel-reduction' or
            type(value.get('trust_level')) is not int or value['trust_level']!=0):
        raise ValueError('Unknown native-audit verification method')
    for field in ('verified_native_decide_axioms','standard_axioms'):
        if (type(value.get(field)) is not list or
                not all(type(n) is str and n for n in value[field]) or
                len(set(value[field]))!=len(value[field])):
            raise ValueError('Malformed native-audit dependencies')
    if not set(value['standard_axioms']).issubset(STANDARD_AXIOMS):
        raise ValueError('Unexpected standard axiom')
    return value
def _valid_dir(path):
    path=Path(path)
    return path.is_dir() and not path.is_symlink() and not any(p.is_symlink()for p in path.rglob('*'))
def grade_prepared(package,submission,timeout=90,trace=None,deadline=None):
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
        shutil.copyfile(AUDITOR,trusted/'TrustedLeanAudit.lean')
        def run(args,**kwargs):
            result=run_isolated('lean',trusted,submission,args,timeout=timeout,deadline=deadline,phase='evaluation-checker' if trace is not None else 'synthetic-prototype',**kwargs)
            if trace is not None:trace.append({k:result.get(k) for k in ('status','exit_code','stdout','stderr','output_truncated','resources')})
            return result
        compiled=run([LEAN,'-j','1','-t','0','-R','/submission','-o','/work/Submission.olean','/submission/Submission.lean'],collect=['Submission.olean'])
        if compiled['status']!='exited':return _result('infrastructure-error','submission',compiled['status'])
        if compiled['exit_code']!=0:return _result('rejected','submission','Lean did not compile submission')
        sub=compiled['artifacts']['Submission.olean']
        gate=run([LEAN,'-j','1','-t','0','-R','/trusted','-o','/work/Gate.olean','/trusted/Gate.lean'],artifacts={'Submission.olean':sub},collect=['Gate.olean'])
        if gate['status']!='exited':return _result('infrastructure-error','gate',gate['status'])
        if gate['exit_code']!=0:return _result('rejected','gate','submission does not inhabit the protected goal')
        audit=run([LEAN,'-j','1','--run','/trusted/TrustedLeanAudit.lean'],artifacts={'Submission.olean':sub,'Gate.olean':gate['artifacts']['Gate.olean']})
        if audit['status']!='exited':return _result('infrastructure-error','audit',audit['status'])
        if audit['exit_code']==3 and 'native_decide kernel replay incomplete:' in audit['stderr']:
            return _result('infrastructure-error','audit','native_decide kernel replay incomplete',
                           native_replay_status='incomplete')
        if audit['exit_code']==0:
            try:
                evidence=audit_evidence(audit['stdout'])
            except (ValueError,TypeError) as error:
                return _result('infrastructure-error','audit','trusted auditor output: '+str(error))
            return _result('accepted','audit',audit_evidence=evidence)
        if ('forbidden axioms:' in audit['stderr'] or
                'checked theorem does not have the fixed goal type' in audit['stderr'] or
                'native_decide kernel replay failed:' in audit['stderr']):
            return _result('rejected','audit','unapproved dependency or wrong goal')
        return _result('infrastructure-error','audit','trusted auditor failed')
