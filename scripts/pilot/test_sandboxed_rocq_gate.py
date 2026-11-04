"""Toy-only isolated Rocq/CompCert kernel and assumptions tests.

This prototype does not claim a complete adversarial assumptions audit.
"""
import tempfile
from pathlib import Path
from sandbox import run_isolated,TOOLCHAINS

def must(result):
    if result['status']!='exited' or result['exit_code']!=0:raise AssertionError(result)
    return result

def test(platform):
    coqc=TOOLCHAINS[platform]+'/bin/coqc';coqchk=TOOLCHAINS[platform]+'/bin/coqchk'
    with tempfile.TemporaryDirectory(prefix='pilot-rocq-gate-')as tmp:
        root=Path(tmp);trusted=root/'trusted';submission=root/'submission';trusted.mkdir();submission.mkdir()
        (trusted/'Obligation.v').write_text('Definition goal : Prop := True.\n')
        (trusted/'Gate.v').write_text('From Trusted Require Import Obligation.\nFrom Candidate Require Import Submission.\nDefinition pilot_checked : Obligation.goal := Submission.solve.\n')
        (trusted/'Audit.v').write_text('From Trusted Require Import Gate.\nPrint Assumptions Gate.pilot_checked.\n')
        common=[coqc,'-q','-noglob','-Q','/trusted','Trusted']
        r=must(run_isolated(platform,trusted,submission,common+['-Q','/work','Trusted','-o','/work/Obligation.vo','/trusted/Obligation.v'],timeout=90,collect=['Obligation.vo']))
        (trusted/'Obligation.vo').write_bytes(r['artifacts']['Obligation.vo'])
        (trusted/'candidate').mkdir()
        for name,proof,expected in [('valid','Definition solve : Obligation.goal := I.',True),
          ('admitted','Theorem solve : Obligation.goal. Admitted.',False),
          ('axiom','Axiom cheat : False. Definition solve : Obligation.goal := False_rect _ cheat.',False)]:
            (submission/'Submission.v').write_text('From Trusted Require Import Obligation.\n'+proof+'\n')
            r=must(run_isolated(platform,trusted,submission,common+['-Q','/submission','Candidate','-Q','/work','Candidate','-o','/work/Submission.vo','/submission/Submission.v'],timeout=90,collect=['Submission.vo']))
            sub=r['artifacts']['Submission.vo']
            (trusted/'candidate/Submission.vo').write_bytes(sub)
            r=must(run_isolated(platform,trusted,submission,common+['-Q','/trusted/candidate','Candidate','-Q','/work','Trusted','-o','/work/Gate.vo','/trusted/Gate.v'],timeout=90,collect=['Gate.vo']))
            (trusted/'Gate.vo').write_bytes(r['artifacts']['Gate.vo'])
            r=must(run_isolated(platform,trusted,submission,[coqchk,'-Q','/trusted','Trusted','-Q','/trusted/candidate','Candidate','Trusted.Gate'],timeout=90))
            r=must(run_isolated(platform,trusted,submission,common+['-Q','/trusted/candidate','Candidate','-Q','/work','Trusted','-o','/work/Audit.vo','/trusted/Audit.v'],timeout=90,collect=['Audit.vo']))
            accepted='Closed under the global context' in r['stdout'] and 'Axioms:' not in r['stdout']
            if accepted!=expected:raise AssertionError((platform,name,r))
            print(platform,name,'accepted'if accepted else'rejected',flush=True)
if __name__=='__main__':
    for p in ('rocq','compcert'):test(p)
    print('Only toy propositions were used; no benchmark theorem was proved.')
