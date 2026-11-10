"""Adversarial checks for independently replayed native Lean facts, on toy goals.

Run only while the serial native study is idle. This file supports staging beside
the proposed auditor/grader, before copying them into scripts/pilot.
"""
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
REPO=(HERE.parents[1] if HERE.name=='pilot' else HERE.parent/'benchmark-equalbench-wsl')
sys.path.insert(0,str(REPO/'scripts/pilot'))
sys.path.insert(0,str(HERE))
from lean_grader_core import grade_prepared, audit_evidence, LEAN_GRADING_POLICY
import lean_grader_core
from test_sandboxed_lean_gate import compile_stage


def check_case(root,name,goal,body,expected,native=None,stage=None):
    package=root/name/'package';submission=root/name/'submission'
    package.mkdir(parents=True);submission.mkdir()
    (package/'Obligation.lean').write_text('import Lean\nnamespace Obligation\ndef goal : Prop := '+goal+'\nend Obligation\n')
    (package/'Obligation.olean').write_bytes(compile_stage(package,submission,'/trusted/Obligation.lean','Obligation.olean'))
    (submission/'Submission.lean').write_text('import Obligation\nnamespace Submission\n'+body+'\nend Submission\n')
    trace=[]
    result=grade_prepared(package,submission,timeout=180,trace=trace)
    assert result['status']==expected,(name,result,trace)
    if expected=='rejected':
        assert result['stage']==(stage or 'audit'),(name,result,trace)
    if native is not None:
        assert len(result['audit_evidence']['verified_native_decide_axioms'])==native,(name,result)
    print(json.dumps({'case':name,'result':result}),flush=True)


def main():
    # A successful trusted auditor must emit exactly one complete policy record.
    valid={'policy':LEAN_GRADING_POLICY,'verification':'independent-kernel-reduction',
           'trust_level':0,'standard_axioms':[],'verified_native_decide_axioms':[]}
    assert audit_evidence('native_audit: '+json.dumps(valid))==valid
    for invalid in ('', 'native_audit: {}', 'native_audit: '+json.dumps(valid)+'\nnative_audit: '+json.dumps(valid)):
        try:audit_evidence(invalid)
        except ValueError:pass
        else:raise AssertionError('Malformed audit evidence accepted')
    # Resource exhaustion is an incomplete host verification, never evidence
    # that the model's theorem is false or an accepted native fact.
    with tempfile.TemporaryDirectory(prefix='specless-native-incomplete-test-')as temp:
        root=Path(temp);package=root/'package';submission=root/'submission'
        package.mkdir();submission.mkdir()
        (package/'Obligation.olean').write_bytes(b'mocked trusted artifact')
        (submission/'Submission.lean').write_text('import Obligation\n')
        stages=[{'status':'exited','exit_code':0,'stdout':'','stderr':'',
                 'artifacts':{'Submission.olean':b'mocked compiled artifact'}},
                {'status':'exited','exit_code':0,'stdout':'','stderr':'',
                 'artifacts':{'Gate.olean':b'mocked gate artifact'}},
                {'status':'exited','exit_code':3,'stdout':'',
                 'stderr':'native_decide kernel replay incomplete: test: deep recursion'}]
        with patch.object(lean_grader_core,'run_isolated',side_effect=stages):
            result=grade_prepared(package,submission)
        assert result['status']=='infrastructure-error' and result['native_replay_status']=='incomplete',result
    with tempfile.TemporaryDirectory(prefix='specless-native-audit-tests-')as temp:
        root=Path(temp)
        check_case(root,'ordinary','True','theorem solve : Obligation.goal := True.intro','accepted',0)
        check_case(root,'native-list','(List.range 16).length = 16',
                   'theorem solve : Obligation.goal := by\n  unfold Obligation.goal\n  native_decide','accepted',1)
        check_case(root,'native-nested-helper','(List.range 16).length = 16',
                   'namespace Inner\n'
                   'theorem computed : (List.range 16).length = 16 := by native_decide\n'
                   'end Inner\n'
                   'theorem solve : Obligation.goal := Inner.computed','accepted',1)
        check_case(root,'sorry','True','theorem solve : Obligation.goal := by sorry','rejected')
        check_case(root,'arbitrary-axiom','True',
                   'axiom cheat : False\ntheorem solve : Obligation.goal := False.elim cheat','rejected')
        check_case(root,'forged-native-false','False',
                   'axiom helper._native.native_decide.ax_1 : False\n'
                   'theorem solve : Obligation.goal := helper._native.native_decide.ax_1','rejected')
        check_case(root,'forged-native-false-bool','False',
                   'axiom helper._native.native_decide.ax_1 : decide False = true\n'
                   'theorem solve : Obligation.goal := (of_decide_eq_true helper._native.native_decide.ax_1 : False)','rejected')
        check_case(root,'unrelated-true-axiom','True',
                   'axiom acceptedFact : True\ntheorem solve : Obligation.goal := acceptedFact','rejected')
        # Origin cannot be recovered from a compiled name. Even an imitation of
        # a native axiom is sound only if its exact computation is kernel-proven.
        check_case(root,'native-shaped-true-fact','True',
                   'axiom helper._native.native_decide.ax_1 : decide True = true\n'
                   'theorem solve : Obligation.goal := (of_decide_eq_true helper._native.native_decide.ax_1 : True)','accepted',1)
        check_case(root,'native-transitive-bad-decision','False',
                   'axiom bad : False\n'
                   'def badDecision : Decidable False := isTrue bad\n'
                   'local instance : Decidable False := badDecision\n'
                   'theorem solve : Obligation.goal := by\n'
                   '  unfold Obligation.goal\n'
                   '  native_decide','rejected')
        check_case(root,'stdout-spoof','True',
                   '#eval IO.println "native_audit: {}"\n'
                   'axiom cheat : False\ntheorem solve : Obligation.goal := False.elim cheat','rejected')
        # Native code can be deliberately made to disagree with kernel semantics.
        # The ordinary native_decide call succeeds at compilation; replay must
        # reduce the logical definition and reject its false generated assertion.
        check_case(root,'implemented-by-lie','False',
                   'def nativeTrue : Bool := true\n'
                   '@[implemented_by nativeTrue] def semanticFalse : Bool := false\n'
                   'theorem computed : semanticFalse = true := by native_decide\n'
                   'theorem solve : Obligation.goal := by\n'
                   '  have bad : false = true := computed\n'
                   '  cases bad','rejected')
        check_case(root,'native-wrong-goal','False',
                   'theorem solve : True := by native_decide','rejected',stage='gate')
    print('Native replay, ordinary proofs, arbitrary axioms, sorry, forged names, compiler overrides and fixed goals checked; only toy propositions were used.')


if __name__=='__main__':main()
