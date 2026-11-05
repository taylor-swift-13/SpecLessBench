"""Verify a published reference report and recheck its proof locally."""
import argparse
import ast
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

from grade_sealed import grade
from single_task_runner import tree_digest
from sandbox import run_isolated

ROOT=Path(__file__).resolve().parents[2]
LEAN=Path('/home/yangfp/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean')


def at_commit(commit,path):
    return subprocess.check_output(['git','show',commit+':'+path],cwd=ROOT)


def source_binding(commit,claim):
    name='prepare_factorial.py' if claim=='equivalence' else 'prepare_factorial_cex.py'
    text=at_commit(commit,'scripts/pilot/'+name).decode('utf-8')
    module=ast.parse(text)
    values={}
    for node in module.body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id=='BINDING':
            values['binding']=ast.literal_eval(node.value)
    if 'binding' not in values:raise SystemExit('Missing frozen binding proof')
    # Historical runs used the old directory; newer runs use its renamed path.
    branch_path='benchmarks/proof-interface/lean/BranchTargets.lean'
    if subprocess.run(['git','cat-file','-e',commit+':'+branch_path],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:
        branch_path='benchmarks/proof-interface/v1/lean/BranchTargets.lean'
    branch=at_commit(commit,branch_path).decode('utf-8')
    expected=('def R_FAC_EQ_equivalence : Prop := SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid 0) (SpecLessBenchBasic.entry 0 0) (SpecLessBenchBasic.entry 0 1)' if claim=='equivalence' else
              'def R_FAC_CEX_equivalence : Prop := SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid 0) (SpecLessBenchBasic.entry 0 0) (SpecLessBenchBasic.entry 0 2)')
    if branch.splitlines().count(expected)!=1:raise SystemExit('Frozen named target differs from checked binding')
    if claim=='counterexample':
        expected_refutation='def R_FAC_CEX_refutationAt (x oa ob : List Int) : Prop :=\n  SpecLessBenchBasic.valid 0 x ∧ SpecLessBenchBasic.entry 0 0 x = some oa ∧ SpecLessBenchBasic.entry 0 2 x = some ob ∧ oa ≠ ob'
        if expected_refutation not in branch:raise SystemExit('Frozen refutation target differs from binding')
    binding=values['binding']
    if binding.count('example : Task.equivalent =')!=1 or binding.count('example (x oa ob : Task.Words)')!=1:
        raise SystemExit('Unexpected binding proof structure')
    return (binding.replace('example : Task.equivalent =','theorem projection_eq : Task.equivalent =')
            .replace('example (x oa ob : Task.Words)','theorem projection_refutation_eq (x oa ob : Task.Words)'))


BINDING_AUDIT='''import Lean
import Lean.Util.CollectAxioms
open Lean
def main : IO UInt32 := do
  initSearchPath "/home/yangfp/.elan/toolchains/leanprover--lean4---v4.34.0"
  let env ← importModules #[{ module := `Binding }] {} 0 (loadExts := false)
  let ctx : Core.Context := { fileName := "<binding-audit>", fileMap := FileMap.ofString "" }
  let state : Core.State := { env := env }
  for name in [`projection_eq, `projection_refutation_eq] do
    let axioms ← (collectAxioms name : CoreM (Array Name)).toIO' ctx state
    let allowed : List Name := [`propext, `Classical.choice, `Quot.sound]
    if !(axioms.filter (fun n => !allowed.contains n)).isEmpty then
      IO.eprintln s!"forbidden binding axioms in {name}: {axioms}"
      return 1
    IO.println s!"{name}: {axioms}"
  return 0
'''


def bridge_to_original(base,package,original,binding,proof,claim):
    """Kernel-check a direct theorem for the original goal in the sandbox."""
    submission=base/'submission';submission.mkdir();shutil.copyfile(proof,submission/'Submission.lean')
    compiled=run_isolated('lean',package,submission,[str(LEAN),'-j','1','-t','0','-R','/submission',
        '-o','/work/Submission.olean','/submission/Submission.lean'],collect=['Submission.olean'])
    if compiled['status']!='exited' or compiled['exit_code']!=0:raise SystemExit('Submission compilation for bridge failed')
    trusted=base/'bridge';trusted.mkdir()
    for folder,names in ((package,('Task.olean','Obligation.olean')),(original,('BasicNative.olean','BasicDomain.olean')),(binding,('Binding.olean',))):
        for name in names:shutil.copyfile(folder/name,trusted/name)
    (trusted/'Submission.olean').write_bytes(compiled['artifacts']['Submission.olean'])
    if claim=='equivalence':
        body='''theorem gold_original : SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid 0) (SpecLessBenchBasic.entry 0 0) (SpecLessBenchBasic.entry 0 1) := by
  have h : Task.equivalent := Submission.solve
  rw [projection_eq] at h
  exact h
'''
    else:
        body='''theorem gold_original : SpecLessBenchBasic.Counterexample (SpecLessBenchBasic.valid 0) (SpecLessBenchBasic.entry 0 0) (SpecLessBenchBasic.entry 0 2) := by
  refine ⟨[1], [1,1], [1,0], ?_⟩
  have h : Task.refutationAt [1] [1,1] [1,0] := Submission.solve
  rw [projection_refutation_eq] at h
  exact h
'''
    (trusted/'Bridge.lean').write_text('import Binding\nimport Obligation\nimport Submission\n'+body,encoding='utf-8')
    result=run_isolated('lean',trusted,submission,[str(LEAN),'-j','1','-t','0','-R','/trusted',
        '-o','/work/Bridge.olean','/trusted/Bridge.lean'],collect=['Bridge.olean'])
    if result['status']!='exited' or result['exit_code']!=0:
        raise SystemExit('Original theorem bridge failed: '+result.get('stdout','')+result.get('stderr',''))
    (trusted/'Bridge.olean').write_bytes(result['artifacts']['Bridge.olean'])
    audit=BINDING_AUDIT.replace('`Binding','`Bridge').replace('[`projection_eq, `projection_refutation_eq]','[`gold_original]')
    (trusted/'BridgeAudit.lean').write_text(audit,encoding='utf-8')
    result=run_isolated('lean',trusted,submission,[str(LEAN),'--run','/trusted/BridgeAudit.lean'])
    if result['status']!='exited' or result['exit_code']!=0:
        raise SystemExit('Original theorem bridge axiom audit failed: '+result.get('stdout','')+result.get('stderr',''))
    print(result['stdout'].strip())


def compile_lean(folder,name,paths):
    env=dict(os.environ,LEAN_PATH=':'.join(str(x) for x in paths))
    subprocess.run([str(LEAN),'-j','1','-o',str(folder/(name+'.olean')),str(folder/(name+'.lean'))],cwd=folder,env=env,check=True,timeout=120)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('reference');args=parser.parse_args()
    root=Path(args.reference)
    if root.is_symlink() or not root.is_dir():raise SystemExit('Invalid reference directory')
    expected={}
    for line in (root/'SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1)
        if Path(name).name!=name or name in expected:raise SystemExit('Unsafe or duplicate manifest entry')
        expected[name]=digest
    actual={p.name for p in root.iterdir() if p.is_file() and p.name!='SHA256SUMS'}
    if set(expected)!=actual:raise SystemExit('Reference file list differs from manifest')
    for name,digest in expected.items():
        p=root/name
        if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise SystemExit('Checksum mismatch: '+name)
    report=json.loads((root/'report.json').read_text());events=(root/'events.jsonl').read_text().splitlines()
    claim=report['configuration']['claim']
    if claim not in ('equivalence','counterexample'):raise SystemExit('Unsupported theorem branch')
    if hashlib.sha256((root/'Submission.lean').read_bytes()).hexdigest()!=report['proof_sha256']:
        raise SystemExit('Proof does not match report')
    commit=report['benchmark_commit']
    if not isinstance(commit,str) or len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit):
        raise SystemExit('Invalid recorded commit')
    runner=at_commit(commit,'scripts/pilot/run_codex_wsl.py')
    if hashlib.sha256(runner).hexdigest()!=report['configuration']['runner_sha256']:
        raise SystemExit('Recorded runner does not match commit')
    if not LEAN.is_file() or hashlib.sha256(LEAN.read_bytes()).hexdigest()!=report['configuration']['lean_executable_sha256']:
        raise SystemExit('Lean executable differs from recorded toolchain')
    times=[json.loads(x) for x in (root/'events.timestamps.jsonl').read_text().splitlines()]
    if len(events)!=report['transcript']['event_count'] or [x['line'] for x in times]!=list(range(1,len(events)+1)):
        raise SystemExit('Event timestamps do not match report')
    if any(a['received_utc']>b['received_utc'] for a,b in zip(times,times[1:])):raise SystemExit('Event timestamps out of order')
    parsed=[json.loads(x) for x in events]
    usage=[x.get('usage') for x in parsed if x.get('type')=='turn.completed' and x.get('usage')]
    if usage!=report['resources']['provider_usage_events']:raise SystemExit('Usage differs from event stream')
    env_path=root/'environment.json'
    if env_path.is_file():
        environment=json.loads(env_path.read_text())
        for name,expected_hash in environment['critical_file_sha256'].items():
            if hashlib.sha256(at_commit(commit,name)).hexdigest()!=expected_hash:raise SystemExit('Critical file did not match recorded commit: '+name)
        replay_files=('scripts/pilot/grade_sealed.py','scripts/pilot/lean_grader_core.py',
                      'scripts/pilot/TrustedLeanAudit.lean','scripts/pilot/sandbox.py',
                      'scripts/pilot/resource_supervisor.py','scripts/pilot/single_task_runner.py')
        for name in replay_files:
            if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=environment['critical_file_sha256'][name]:
                raise SystemExit('Replay checker differs from recorded run: '+name)
        from run_codex_wsl import fingerprint_tree
        current=fingerprint_tree(LEAN.parent.parent)
        recorded=environment['lean_toolchain_tree']
        if any(current[k]!=recorded[k] for k in ('sha256','file_count','total_bytes','scheme')):
            raise SystemExit('Lean toolchain tree differs from recorded environment')
    with tempfile.TemporaryDirectory(prefix='specless-reference-') as temp:
        base=Path(temp);package=base/'task';package.mkdir()
        with tarfile.open(root/'task.tar.gz','r:gz') as tar:
            members=tar.getmembers()
            if {m.name for m in members}!={'Task.lean','Task.olean','Obligation.lean','Obligation.olean'} or not all(m.isfile() for m in members):
                raise SystemExit('Unexpected task archive members')
            for member in members:(package/member.name).write_bytes(tar.extractfile(member).read())
        if claim=='counterexample':
            expected='import Task\nnamespace Obligation\ndef goal : Prop := Task.refutationAt [1] [1,1] [1,0]\nend Obligation\n'
            if (package/'Obligation.lean').read_text()!=expected or report['configuration'].get('fixed_witness')!={'input':[1],'left_observation':[1,1],'right_observation':[1,0]}:
                raise SystemExit('Counterexample witness does not match the fixed literal target')
        expected_task=report['configuration']['task_package_sha256']
        if tree_digest(package)!=expected_task:raise SystemExit('Task package hash mismatch')
        result=grade('lean',package,expected_task,root/'Submission.lean')
        if result['status']!=report['result']['status'] or result['status']!='accepted':raise SystemExit('Proof replay failed: '+json.dumps(result))
        # Rebuild the task from its source, rather than trusting bundled .olean
        # files. Check the projection against the named target in the commit.
        original=base/'original';original.mkdir();binding=base/'binding';binding.mkdir()
        for name in ('BasicNative.lean','BasicDomain.lean'):
            (original/name).write_bytes(at_commit(commit,'benchmarks/tasks/algorithms-core/lean/'+name))
        for name in ('Task','Obligation'):compile_lean(package,name,[package])
        for name in ('BasicNative','BasicDomain'):compile_lean(original,name,[original])
        (binding/'Binding.lean').write_text(source_binding(commit,claim),encoding='utf-8')
        compile_lean(binding,'Binding',[package,original])
        (binding/'BindingAudit.lean').write_text(BINDING_AUDIT,encoding='utf-8')
        env=dict(os.environ,LEAN_PATH=':'.join(map(str,(binding,package,original))))
        subprocess.run([str(LEAN),'--run',str(binding/'BindingAudit.lean')],cwd=binding,env=env,check=True,timeout=120)
        rebuilt=grade('lean',package,tree_digest(package),root/'Submission.lean')
        if rebuilt['status']!='accepted':raise SystemExit('Proof does not check against rebuilt source: '+json.dumps(rebuilt))
        bridge_to_original(base,package,original,binding,root/'Submission.lean',claim)
    print('Reference checksums, timestamps, source rebuild, frozen-target binding and original theorem proof check passed.')


if __name__=='__main__':main()
