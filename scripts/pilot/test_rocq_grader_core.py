"""Exercise experimental Rocq/CompCert cores on synthetic toy goals only."""
import tempfile
from pathlib import Path
from sandbox import run_isolated,TOOLCHAINS
from rocq_grader_core import grade_prepared

def test(platform):
    coqc=TOOLCHAINS[platform]+'/bin/coqc'
    with tempfile.TemporaryDirectory(prefix='pilot-rocq-core-')as tmp:
        root=Path(tmp);package=root/'package';submission=root/'submission';package.mkdir();submission.mkdir()
        (package/'Obligation.v').write_text('Definition goal : Prop := True.\n')
        r=run_isolated(platform,package,submission,[coqc,'-q','-noglob','-Q','/trusted','Trusted','-Q','/work','Trusted','-o','/work/Obligation.vo','/trusted/Obligation.v'],timeout=90,collect=['Obligation.vo'])
        assert r['status']=='exited' and r['exit_code']==0,r
        (package/'Obligation.vo').write_bytes(r['artifacts']['Obligation.vo'])
        for name,proof,expected in [('valid','Definition solve : Obligation.goal := I.','accepted'),
          ('admitted','Theorem solve : Obligation.goal. Admitted.','rejected'),
          ('axiom','Axiom cheat : False. Definition solve : Obligation.goal := False_rect _ cheat.','rejected'),
          ('stdout-spoof','Goal True. idtac "Closed under the global context". exact I. Qed.\nAxiom cheat : False. Definition solve : Obligation.goal := False_rect _ cheat.','rejected'),
          ('wrong-type','Definition solve : False := I.','rejected')]:
            (submission/'Submission.v').write_text('From Trusted Require Import Obligation.\n'+proof+'\n')
            result=grade_prepared(platform,package,submission);assert result['status']==expected,(name,result)
            print(platform,name,result['status'],flush=True)
        (package/'Gate.v').write_text('Definition pilot_checked : True := I.\n')
        result=grade_prepared(platform,package,submission);assert result['status']=='infrastructure-error',result
        print(platform,'forged-gate package refused',flush=True)
for platform in ('rocq','compcert'):test(platform)
print('Only toy propositions were used; no benchmark theorem was proved.')
