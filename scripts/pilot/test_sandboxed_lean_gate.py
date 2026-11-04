"""End-to-end isolated gate checks on synthetic propositions only."""
import shutil,tempfile
from pathlib import Path
from sandbox import run_isolated,TOOLCHAINS
ROOT=Path(__file__).resolve().parents[2];LEAN=TOOLCHAINS['lean']+'/bin/lean'
def compile_stage(trusted,submission,source,out,artifacts=None):
    result=run_isolated('lean',trusted,submission,
      [LEAN,'-j','1','-t','0','-R','/trusted' if source.startswith('/trusted/') else '/submission',
       '-o','/work/'+out,source],timeout=90,artifacts=artifacts,collect=[out])
    if result['exit_code']!=0:raise AssertionError(result)
    return result['artifacts'][out]
def main():
    with tempfile.TemporaryDirectory(prefix='pilot-gate-test-')as tmp:
        root=Path(tmp);trusted=root/'trusted';submission=root/'submission';trusted.mkdir();submission.mkdir()
        (trusted/'Obligation.lean').write_text('namespace Obligation\ndef goal : Prop := True\nend Obligation\n')
        (trusted/'Gate.lean').write_text('import Obligation\nimport Submission\ntheorem pilot_checked : Obligation.goal := Submission.solve\n')
        shutil.copyfile(ROOT/'scripts/pilot/TrustedLeanAudit.lean',trusted/'TrustedLeanAudit.lean')
        obligation=compile_stage(trusted,submission,'/trusted/Obligation.lean','Obligation.olean')
        (trusted/'Obligation.olean').write_bytes(obligation)
        for name,proof,expected in [
          ('valid','theorem solve : Obligation.goal := True.intro',True),
          ('sorry','theorem solve : Obligation.goal := by sorry',False),
          ('axiom','axiom cheat : False\ntheorem solve : Obligation.goal := False.elim cheat',False)]:
            (submission/'Submission.lean').write_text('import Obligation\nnamespace Submission\n'+proof+'\nend Submission\n')
            compiled=compile_stage(trusted,submission,'/submission/Submission.lean','Submission.olean')
            gate=compile_stage(trusted,submission,'/trusted/Gate.lean','Gate.olean',{'Submission.olean':compiled})
            result=run_isolated('lean',trusted,submission,[LEAN,'-j','1','--run','/trusted/TrustedLeanAudit.lean'],timeout=90,
              artifacts={'Submission.olean':compiled,'Gate.olean':gate})
            if (result['exit_code']==0)!=expected:raise AssertionError((name,result))
            print(name,'accepted'if expected else'rejected',flush=True)
        (submission/'Submission.lean').write_text('import Obligation\nnamespace Submission\ntheorem solve : Obligation.goal := True.intro\nend Submission\n')
        compiled=compile_stage(trusted,submission,'/submission/Submission.lean','Submission.olean')
        (trusted/'Gate.lean').write_text('import Obligation\nimport Submission\ntheorem pilot_checked : True := True.intro\n')
        fake=compile_stage(trusted,submission,'/trusted/Gate.lean','Gate.olean',{'Submission.olean':compiled})
        result=run_isolated('lean',trusted,submission,[LEAN,'-j','1','--run','/trusted/TrustedLeanAudit.lean'],timeout=90,
          artifacts={'Submission.olean':compiled,'Gate.olean':fake})
        assert result['exit_code']!=0,result
        print('wrong-goal rejected',flush=True)
    print('Only toy propositions were used; no benchmark theorem was proved.')
if __name__=='__main__':main()
