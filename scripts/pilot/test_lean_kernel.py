"""Synthetic proof-gate checks only; no benchmark theorem is proved."""
import os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEAN='/home/yangfp/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean'
AUDIT=ROOT/'scripts/pilot/TrustedLeanAudit.lean'

def run_case(name,submission,expected,gate_override=None):
    with tempfile.TemporaryDirectory(prefix='pilot-lean-toy-')as tmp:
        d=Path(tmp);env=dict(os.environ,LEAN_PATH=str(d))
        (d/'Obligation.lean').write_text('namespace Obligation\ndef goal : Prop := True\nend Obligation\n')
        (d/'Submission.lean').write_text('import Obligation\nnamespace Submission\n'+submission+'\nend Submission\n')
        (d/'Gate.lean').write_text('import Obligation\nimport Submission\n'+(gate_override or 'theorem pilot_checked : Obligation.goal := Submission.solve')+'\n')
        for name2 in ('Obligation','Submission','Gate'):
            r=subprocess.run([LEAN,'-t','0','-o',str(d/(name2+'.olean')),str(d/(name2+'.lean'))],cwd=d,env=env,capture_output=True,text=True,timeout=120)
            if r.returncode:raise AssertionError((name,name2,r.stdout,r.stderr))
        r=subprocess.run([LEAN,'--run',str(AUDIT)],cwd=d,env=env,capture_output=True,text=True,timeout=120)
        if (r.returncode==0)!=expected:raise AssertionError((name,r.returncode,r.stdout,r.stderr))
        print(name,'accepted'if r.returncode==0 else'rejected',flush=True)
def main():
    run_case('valid','theorem solve : Obligation.goal := True.intro',True)
    run_case('sorry','theorem solve : Obligation.goal := by sorry',False)
    run_case('axiom','axiom cheat : False\ntheorem solve : Obligation.goal := False.elim cheat',False)
    run_case('wrong-goal','theorem solve : Obligation.goal := True.intro',False,
             'theorem pilot_checked : True := True.intro')
if __name__=='__main__':main()
