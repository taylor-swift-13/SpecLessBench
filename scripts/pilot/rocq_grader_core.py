"""Experimental Rocq proof gate for trusted, task-specific packages.

Not enabled for pilot tasks: assumption reporting and loader behavior still
need adversarial review. Native Rocq rejects all assumptions; CompCert admits
its own fully qualified assumptions and named Rocq library dependencies.
"""
import re,shutil,tempfile
from pathlib import Path
from sandbox import run_isolated,TOOLCHAINS

# CompCert's own fully qualified namespace is trusted. Its Rocq dependencies
# are accepted only by exact name; the submission namespace is never trusted.
COMPCERT_ROCQ_ASSUMPTIONS = frozenset({
    'Stdlib.Reals.ClassicalDedekindReals.sig_not_dec',
    'Stdlib.Reals.ClassicalDedekindReals.sig_forall_dec',
    'Stdlib.Logic.FunctionalExtensionality.functional_extensionality_dep',
    'Stdlib.Logic.Classical_Prop.classic',
})

def allowed_assumptions(platform, output):
    output = output.strip()
    if output == 'Closed under the global context': return True
    if platform != 'compcert' or not output.startswith('Axioms:\n'): return False
    lines = output.splitlines()[1:]
    if not lines: return False
    names = []
    for line in lines:
        if not line: return False
        if line[0].isspace():
            if not names: return False
            continue
        match = re.fullmatch(r"([A-Za-z0-9_\.']+)\s*:.*", line)
        if not match: return False
        names.append(match.group(1))
    return len(names) == len(set(names)) and all(
        name.startswith('compcert.') or name in COMPCERT_ROCQ_ASSUMPTIONS for name in names)

def _result(status,stage,detail=None):return {'status':status,'stage':stage,'detail':detail}
def _valid_dir(path):
    path=Path(path)
    return path.is_dir() and not path.is_symlink() and not any(p.is_symlink()for p in path.rglob('*'))
def grade_prepared(platform,package,submission,timeout=90,trace=None):
    package=Path(package);submission=Path(submission)
    if platform not in ('rocq','compcert') or not _valid_dir(package) or not _valid_dir(submission):return _result('infrastructure-error','input','invalid platform or directory')
    if not (package/'Obligation.vo').is_file():return _result('infrastructure-error','input','incomplete trusted package')
    if any((package/name).exists()for name in ('candidate','Gate.v','Gate.vo','Audit.v','Submission.vo')):return _result('infrastructure-error','input','reserved package file')
    if {p.name for p in submission.iterdir()}!={'Submission.v'} or not (submission/'Submission.v').is_file():return _result('rejected','submission','expected only Submission.v')
    if (submission/'Submission.v').stat().st_size>1024*1024:return _result('rejected','submission','source exceeds size limit')
    coqc=TOOLCHAINS[platform]+'/bin/coqc';coqchk=TOOLCHAINS[platform]+'/bin/coqchk'
    with tempfile.TemporaryDirectory(prefix='specless-rocq-core-')as temp:
        trusted=Path(temp)/'trusted';shutil.copytree(package,trusted);(trusted/'candidate').mkdir()
        (trusted/'Gate.v').write_text('From Trusted Require Import Obligation.\nFrom Candidate Require Import Submission.\nDefinition pilot_checked : Obligation.goal := Submission.solve.\n')
        (trusted/'Audit.v').write_text('Set Printing Fully Qualified.\nFrom Trusted Require Import Gate.\nPrint Assumptions Gate.pilot_checked.\n')
        def run(args,**kwargs):
            result=run_isolated(platform,trusted,submission,args,timeout=timeout,phase='evaluation-checker' if trace is not None else 'synthetic-prototype',**kwargs)
            if trace is not None:trace.append({k:result.get(k) for k in ('status','exit_code','stdout','stderr','output_truncated','resources')})
            return result
        common=[coqc,'-q','-noglob','-Q','/trusted','Trusted']
        sub=run(common+['-Q','/submission','Candidate','-Q','/work','Candidate','-o','/work/Submission.vo','/submission/Submission.v'],collect=['Submission.vo'])
        if sub['status']!='exited':return _result('infrastructure-error','submission',sub['status'])
        if sub['exit_code']!=0:return _result('rejected','submission','Rocq did not compile submission')
        (trusted/'candidate/Submission.vo').write_bytes(sub['artifacts']['Submission.vo'])
        gate=run(common+['-Q','/trusted/candidate','Candidate','-Q','/work','Trusted','-o','/work/Gate.vo','/trusted/Gate.v'],collect=['Gate.vo'])
        if gate['status']!='exited':return _result('infrastructure-error','gate',gate['status'])
        if gate['exit_code']!=0:return _result('rejected','gate','submission does not inhabit the protected goal')
        (trusted/'Gate.vo').write_bytes(gate['artifacts']['Gate.vo'])
        vm=['-bytecode-compiler','yes'] if platform=='compcert' else []
        checked=run([coqchk,*vm,'-Q','/trusted','Trusted','-Q','/trusted/candidate','Candidate','Trusted.Gate'])
        if checked['status']!='exited' or checked['exit_code']!=0:return _result('infrastructure-error','kernel','independent kernel check failed')
        audit=run(common+['-Q','/trusted/candidate','Candidate','-Q','/work','Trusted','-o','/work/Audit.vo','/trusted/Audit.v'],collect=['Audit.vo'])
        if audit['status']!='exited' or audit['exit_code']!=0:return _result('infrastructure-error','audit','assumptions check failed')
        if not audit.get('output_truncated') and allowed_assumptions(platform,audit['stdout']):return _result('accepted','audit')
        return _result('rejected','audit','unapproved assumptions or unexpected audit output')
