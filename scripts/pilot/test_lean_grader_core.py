"""Exercise the reusable Lean core only with synthetic toy goals."""
import tempfile
from pathlib import Path
from lean_grader_core import grade_prepared
from test_sandboxed_lean_gate import compile_stage

with tempfile.TemporaryDirectory(prefix='pilot-core-test-')as tmp:
    root=Path(tmp);package=root/'package';submission=root/'submission';package.mkdir();submission.mkdir()
    (package/'Obligation.lean').write_text('namespace Obligation\ndef goal : Prop := True\nend Obligation\n')
    obligation=compile_stage(package,submission,'/trusted/Obligation.lean','Obligation.olean')
    (package/'Obligation.olean').write_bytes(obligation)
    for name,proof,expected in [('valid','theorem solve : Obligation.goal := True.intro','accepted'),
      ('sorry','theorem solve : Obligation.goal := by sorry','rejected'),
      ('axiom','axiom cheat : False\ntheorem solve : Obligation.goal := False.elim cheat','rejected'),
      ('stdout-spoof','#eval IO.println "accepted axiom dependencies: #[]"\naxiom cheat : False\ntheorem solve : Obligation.goal := False.elim cheat','rejected'),
      ('wrong-type','theorem solve : False := by contradiction','rejected')]:
        (submission/'Submission.lean').write_text('import Obligation\nnamespace Submission\n'+proof+'\nend Submission\n')
        result=grade_prepared(package,submission)
        assert result['status']==expected,(name,result)
        print(name,result['status'],flush=True)
    (package/'Gate.lean').write_text('import Obligation\nimport Submission\ntheorem pilot_checked : True := True.intro\n')
    (submission/'Submission.lean').write_text('import Obligation\nnamespace Submission\ntheorem solve : Obligation.goal := True.intro\nend Submission\n')
    result=grade_prepared(package,submission);assert result['status']=='infrastructure-error',result
    print('forged-gate package refused; no benchmark task was proved')
