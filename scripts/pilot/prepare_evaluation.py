"""Prepare source-bound, single-pair evaluation packages (never gold proofs)."""
import json
import fcntl
import os
import re
import resource
import hashlib
import subprocess
import time
from pathlib import Path

from private_paths import PRIVATE
from selection import selection
from single_task_runner import tree_digest
from verify_freeze import main as verify_freeze

ROOT = Path(__file__).resolve().parents[2]
PACKAGES = Path.home()/'.local/share/speclessbench/packages'
LEAN = Path.home()/'.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean'
SOURCE = ROOT/'benchmarks/tasks/algorithms-core/lean'
ROCQ = Path.home()/'.opam/qcp-8.20'


def compile_rocq(folder, name, paths):
    argv = [str(ROCQ/'bin/coqc'), '-q', '-noglob']
    for path, logical in paths:
        argv += ['-Q', str(path), logical]
    result = subprocess.run(argv+[str(folder/(name+'.v'))], cwd=folder,
                            capture_output=True, text=True, timeout=180)
    if result.returncode:
        (folder/(name+'.failure.log')).write_text(result.stdout+result.stderr)
        raise RuntimeError(name+':\n'+result.stdout+result.stderr)
    return result.stdout+result.stderr


def compile_lean(folder, name, paths):
    result = subprocess.run([str(LEAN), '-j', '1', '-o', str(folder/(name+'.olean')),
                             str(folder/(name+'.lean'))], cwd=folder,
                            env=dict(os.environ, LEAN_PATH=':'.join(map(str, paths))),
                            capture_output=True, text=True, timeout=180)
    if result.returncode:
        (folder/(name+'.failure.log')).write_text(result.stdout+result.stderr)
        raise RuntimeError(name+':\n'+result.stdout+result.stderr)
    return result.stdout+result.stderr


def definition(source, name):
    match = re.search(r'^def '+re.escape(name)+r'\b.*?(?=\n(?:def |end )|\Z)', source, re.M | re.S)
    if not match:
        raise ValueError('Missing frozen definition: '+name)
    return match.group().strip()+'\n'


def matrix_definition(name, style):
    header = f'''def {name} (xs : Words) : Words :=
  let r := (iz xs 0).toNat; let k := (iz xs 1).toNat; let c := (iz xs 2).toNat
'''
    if style == 1:
        return header+'''  (List.range r).foldl (fun out i =>
    (List.range k).foldl (fun out t => (List.range c).foldl (fun out j =>
      put out (i*c+j) (iz out (i*c+j)+iz xs (3+i*k+t)*iz xs (3+r*k+t*c+j))) out) out)
    (List.replicate (r*c) 0)
'''
    index = 'j*k+t' if style == 2 else 't*c+j'
    return header+f'''  (List.range (r*c)).map (fun pos =>
    let i := pos/c; let j := pos%c
    (List.range k).foldl (fun a t => a+iz xs (3+i*k+t)*iz xs (3+r*k+({index}))) 0)
'''


def queue_definition(name, style):
    push = '(front++[v],rear,out++[0,0])' if style == 0 else '(front,v::rear,out++[0,0])'
    transfer = '(front,rear)' if style == 0 else ('if front.isEmpty then (reverseRec rear,'+('rear' if style == 2 else '[]')+') else (front,rear)')
    return f'''def {name} (xs : Words) : Words :=
  let (_,_,out) := (List.range (iz xs 0).toNat).foldl (fun (front,rear,out) i =>
    let op := iz xs (1+2*i); let v := iz xs (2+2*i)
    if op == 0 then {push}
    else
      let (f,r) := {transfer}
      match f with
      | [] => (f,r,out++[op,0,0])
      | a::rest => (if op == 1 then rest else f,r,out++[op,1,a]))
    (([] : Words),([] : Words),([] : Words))
  out
'''


def prepare(row):
    """Native sequence/matrix adapters; other families remain pending."""
    ctx = row['context']; family = ctx.get('family_index')
    if ctx.get('tranche') != 'algorithms' or family not in (1, 2, 3, 5):
        return None
    package = PACKAGES/row['pilot_id']/'lean'
    if (package/'registry.json').exists():
        meta = json.loads((package/'registry.json').read_text())
        if tree_digest(package/'task') != meta['public_sha256']:
            raise ValueError('Existing package changed: '+str(package))
        return meta
    started = time.monotonic()
    if package.exists():
        raise ValueError('Incomplete preparation needs inspection: '+str(package))
    task = package/'task'; binding = package/'binding'
    task.mkdir(parents=True, mode=0o700); binding.mkdir(mode=0o700)
    native = (SOURCE/'BasicNative.lean').read_text()
    targets = (ROOT/'benchmarks/proof-interface/lean/BranchTargets.lean').read_text()
    target = definition(targets, ctx['equivalence_goal'])
    styles = re.findall(r'SpecLessBenchBasic.entry '+str(family)+r' (\d+)', target)
    if styles[0] != '0' or len(styles) != 2 or styles[1] not in ('1', '2'):
        raise ValueError('Unsupported frozen pair')
    style = int(styles[1])
    names = {1: ('reverseRec', 'reverseAcc'), 2: ('sumRec', 'sumAcc'), 3: (), 5: ('reverseRec',)}[family]
    definitions = ''.join(definition(native, n) for n in ('iz', 'finish', *names))
    left = 'reverseRec data' if family == 1 else '[sumRec data]'
    right = ('reverseAcc data '+('[0]' if style == 2 else '[]')) if family == 1 else (
        '[sumAcc '+('(data.take (data.length-1))' if style == 2 else 'data')+' 0]')
    source = 'import Lean\nnamespace Task\nabbrev Words := List Int\n'+definitions+'''
def inRange (v lo hi : Int) : Bool := lo ≤ v && v ≤ hi
def valid (xs : Words) : Prop :=
  (inRange (iz xs 0) 0 64 && xs.length == 1+(iz xs 0).toNat &&
   (xs.drop 1).all (fun v => inRange v (-1000000) 1000000)) = true
'''
    data_prefix = '  let data := (xs.drop 1).take (iz xs 0).toNat\n'
    if family == 3:
        source = 'import Lean\nnamespace Task\nabbrev Words := List Int\n'+definitions+definition(native, 'put')
        source += matrix_definition('matrixA', 0)+matrix_definition('matrixB', style)+'''
def inRange (v lo hi : Int) : Bool := lo ≤ v && v ≤ hi
def valid (xs : Words) : Prop :=
  (let a := iz xs 0; let b := iz xs 1; let c := iz xs 2
   let n := a.toNat; let m := b.toNat; let z := c.toNat
   inRange a 0 6 && inRange b 0 6 && inRange c 0 6 && xs.length == 3+n*m+m*z &&
     (xs.drop 3).all (fun v => inRange v (-1000) 1000)) = true
'''
        left, right, data_prefix = 'matrixA xs', 'matrixB xs', ''
    elif family == 5:
        source = 'import Lean\nnamespace Task\nabbrev Words := List Int\n'+definitions
        source += queue_definition('queueA', 0)+queue_definition('queueB', style)+'''
def inRange (v lo hi : Int) : Bool := lo ≤ v && v ≤ hi
def valid (xs : Words) : Prop :=
  (inRange (iz xs 0) 0 64 && xs.length == 1+2*(iz xs 0).toNat &&
   (List.range (iz xs 0).toNat).all (fun i =>
     let op := iz xs (1+2*i); let v := iz xs (2+2*i)
     inRange op 0 2 && (if op == 0 then inRange v (-1000000) 1000000 else v == 0))) = true
'''
        left, right, data_prefix = 'queueA xs', 'queueB xs', ''
    for name, expr in (('a', left), ('b', right)):
        source += f'def {name} (xs : Words) : Option Words :=\n'+data_prefix+f'  some (finish ({expr}))\n'
    source += '''def equivalent : Prop := ∀ x, valid x → ∃ o, a x = some o ∧ b x = some o
def refutationAt (x oa ob : Words) : Prop := valid x ∧ a x = some oa ∧ b x = some ob ∧ oa ≠ ob
end Task
'''
    (task/'Task.lean').write_text(source)
    (task/'Obligation.lean').write_text('import Task\nnamespace Obligation\ndef goal : Prop := Task.equivalent\nend Obligation\n')
    logs = [compile_lean(task, name, [task]) for name in ('Task', 'Obligation')]
    original = ROOT/'_build/pilot-v1/evaluation-binding'
    original.mkdir(parents=True, exist_ok=True)
    for name in ('BasicNative', 'BasicDomain'):
        path = original/(name+'.lean'); frozen = SOURCE/path.name
        if not path.exists() or path.read_bytes() != frozen.read_bytes() or not (original/(name+'.olean')).exists():
            path.write_bytes(frozen.read_bytes()); logs.append(compile_lean(original, name, [original]))
    helper = ''
    for name in names:
        acc = name.endswith('Acc')
        params = '(xs a : Task.Words)' if family == 1 and acc else ('(xs : Task.Words) (a : Int)' if acc else '(xs : Task.Words)')
        args = 'xs a' if acc else 'xs'
        helper += f'''theorem {name}_eq {params} : Task.{name} {args} = SpecLessBenchBasic.{name} {args} := by
  induction xs {'generalizing a' if acc else ''} with
  | nil => rfl
  | cons x xs ih => simp [Task.{name}, SpecLessBenchBasic.{name}, ih]
'''
    helper_names = ', '.join(n+'_eq' for n in names)
    for name, selected in (('a', 0), ('b', style)):
        if family == 3:
            helper += f'theorem {name}_eq (x : Task.Words) : Task.{name} x = SpecLessBenchBasic.entry {family} {selected} x := by rfl\n'
        elif family == 5:
            helper += f'''theorem {name}_eq (x : Task.Words) : Task.{name} x = SpecLessBenchBasic.entry {family} {selected} x := by
  simp [Task.{name}, Task.queue{'A' if name == 'a' else 'B'}, Task.finish, Task.iz, SpecLessBenchBasic.entry, SpecLessBenchBasic.queue, SpecLessBenchBasic.finish, SpecLessBenchBasic.iz, reverseRec_eq]
  <;> constructor <;> rfl
'''
        else:
            helper += f'''theorem {name}_eq (x : Task.Words) : Task.{name} x = SpecLessBenchBasic.entry {family} {selected} x := by
  simp [Task.{name}, Task.finish, Task.iz, SpecLessBenchBasic.entry, SpecLessBenchBasic.finish, SpecLessBenchBasic.iz, {helper_names}]
'''
    helper += f'''theorem valid_eq : Task.valid = SpecLessBenchBasic.valid {family} := by funext x; rfl
example : Task.equivalent = SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid {family}) (SpecLessBenchBasic.entry {family} 0) (SpecLessBenchBasic.entry {family} {style}) := by
  unfold Task.equivalent SpecLessBenchBasic.Equivalent
  rw [valid_eq, funext a_eq, funext b_eq]
example (x oa ob : Task.Words) : Task.refutationAt x oa ob = (SpecLessBenchBasic.valid {family} x ∧ SpecLessBenchBasic.entry {family} 0 x = some oa ∧ SpecLessBenchBasic.entry {family} {style} x = some ob ∧ oa ≠ ob) := by
  unfold Task.refutationAt
  rw [valid_eq, a_eq x, b_eq x]
'''
    (binding/'Binding.lean').write_text('import BasicDomain\nimport Task\n'+helper)
    logs.append(compile_lean(binding, 'Binding', [task, original]))
    (binding/'compile.log').write_text('\n'.join(logs))
    meta = {'pilot_id': row['pilot_id'], 'platform': 'lean', 'public_sha256': tree_digest(task),
            'binding': 'lean-kernel-checked-correspondence-for-both-branches',
            'source_goal': ctx['equivalence_goal'], 'source_context': row['source_context_id'],
            'preparation_wall_seconds': time.monotonic()-started,
            'preparation_controller_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
            'final_proof_attempted': False}
    (package/'registry.json').write_text(json.dumps(meta, indent=2)+'\n')
    return meta


def bind_rocq_target(row, package, meta):
    """Check the literal frozen Rocq aliases, independently of Lean metadata."""
    if meta.get('exact_frozen_target_binding'):
        return meta
    started = time.monotonic(); ctx = row['context']; binding = package/'binding'
    targets = (ROOT/'benchmarks/proof-interface/rocq/BranchTargets.v').read_text()
    selected = []
    for key in ('equivalence_goal', 'refutation_at_goal'):
        match = re.search(r'^Definition '+re.escape(ctx[key])+r'\b.*?(?=\nDefinition |\Z)', targets, re.M | re.S)
        if not match:
            raise ValueError('Missing frozen Rocq target')
        selected.append(match.group().strip())
    (binding/'FrozenTarget.v').write_text('From Coq Require Import ZArith List.\nFrom Frozen Require Import BasicNative BasicDomain.\n'+'\n'.join(selected)+'\n')
    paths = [(package/'task', 'Trusted'), (ROOT/'_build/pilot-v1/evaluation-rocq-binding', 'Frozen'), (binding, 'Binding')]
    logs = [compile_rocq(binding, 'FrozenTarget', paths)]
    (binding/'ExactTargetBinding.v').write_text(f'''From Trusted Require Import Task.
From Binding Require Import FrozenTarget.
Example exact_equivalence_binding : Task.equivalent = FrozenTarget.{ctx['equivalence_goal']}. Proof. reflexivity. Qed.
Example exact_refutation_binding (x oa ob : Task.words) : Task.refutationAt x oa ob = FrozenTarget.{ctx['refutation_at_goal']} x oa ob. Proof. reflexivity. Qed.
''')
    logs.append(compile_rocq(binding, 'ExactTargetBinding', paths))
    (binding/'exact-target.log').write_text('\n'.join(logs))
    meta.update(exact_frozen_target_binding='rocq-kernel-checked', exact_frozen_target_source_sha256=hashlib.sha256(targets.encode()).hexdigest(),
                additional_exact_binding_wall_seconds=time.monotonic()-started)
    (package/'registry.json').write_text(json.dumps(meta, indent=2)+'\n')
    return meta


def prepare_rocq(row):
    ctx = row['context']; family = ctx.get('family_index')
    if ctx.get('tranche') != 'algorithms' or family not in (1, 2):
        return None
    package = PACKAGES/row['pilot_id']/'rocq'
    if (package/'registry.json').exists():
        meta = json.loads((package/'registry.json').read_text())
        if tree_digest(package/'task') != meta['public_sha256']:
            raise ValueError('Existing Rocq package changed')
        return bind_rocq_target(row, package, meta)
    if package.exists():
        raise ValueError('Incomplete Rocq preparation needs inspection: '+str(package))
    started = time.monotonic(); task = package/'task'; binding = package/'binding'
    task.mkdir(parents=True, mode=0o700); binding.mkdir(mode=0o700)
    source = ROOT/'benchmarks/tasks/algorithms-core/rocq'
    native = (source/'BasicNative.v').read_text()
    targets = (ROOT/'benchmarks/proof-interface/lean/BranchTargets.lean').read_text()
    styles = re.findall(r'SpecLessBenchBasic.entry '+str(family)+r' (\d+)', definition(targets, ctx['equivalence_goal']))
    if len(styles) != 2 or styles[0] != '0' or styles[1] not in ('1', '2'):
        raise ValueError('Unsupported frozen Rocq pair')
    style = int(styles[1]); names = ('reverse_rec', 'reverse_acc') if family == 1 else ('sum_rec', 'sum_acc')
    def extract(name):
        match = re.search(r'^(?:Definition|Fixpoint) '+re.escape(name)+r'\b.*?(?=\n(?:Definition|Fixpoint|Notation) |\Z)', native, re.M | re.S)
        if not match:
            raise ValueError('Missing frozen Rocq definition: '+name)
        return match.group().strip()+'\n'
    text = 'From Coq Require Import ZArith List Bool.\nImport ListNotations.\nOpen Scope nat_scope.\n'
    text += ''.join(extract(n) for n in ('words', 'iz', 'finish', *names))
    text += '''Definition in_range v lo hi := Z.leb lo v && Z.leb v hi.
Definition valid (xs : words) : Prop :=
  (in_range (iz xs 0) 0 64 && Nat.eqb (length xs) (1+Z.to_nat (iz xs 0)) &&
   forallb (fun v => in_range v (-1000000) 1000000) (skipn 1 xs)) = true.
'''
    left = 'reverse_rec data' if family == 1 else '[sum_rec data]'
    right = ('reverse_acc data '+('[0%Z]' if style == 2 else '[]')) if family == 1 else (
        '[sum_acc '+('(firstn (length data-1) data)' if style == 2 else 'data')+' 0%Z]')
    for name, expression in (('a', left), ('b', right)):
        text += f'Definition {name} (xs : words) : option words :=\n  let data := firstn (Z.to_nat (iz xs 0)) (skipn 1 xs) in Some (finish ({expression})).\n'
    text += '''Definition equivalent : Prop := forall x, valid x -> exists o, a x = Some o /\ b x = Some o.
Definition refutationAt (x oa ob : words) : Prop := valid x /\ a x = Some oa /\ b x = Some ob /\ oa <> ob.
'''
    (task/'Task.v').write_text(text)
    (task/'Obligation.v').write_text('From Trusted Require Import Task.\nDefinition goal : Prop := Task.equivalent.\n')
    logs = [compile_rocq(task, name, [(task, 'Trusted')]) for name in ('Task', 'Obligation')]
    original = ROOT/'_build/pilot-v1/evaluation-rocq-binding'; original.mkdir(parents=True, exist_ok=True)
    for name in ('BasicNative', 'BasicDomain'):
        path = original/(name+'.v'); frozen = source/path.name
        if not path.exists() or path.read_bytes() != frozen.read_bytes() or not (original/(name+'.vo')).exists():
            path.write_bytes(frozen.read_bytes()); logs.append(compile_rocq(original, name, [(original, 'Frozen')]))
    correspondence = f'''From Trusted Require Import Task.
From Frozen Require Import BasicNative BasicDomain.
Example domain_binding (x : Task.words) : Task.valid x = BasicDomain.valid {family} x. Proof. reflexivity. Qed.
Example left_binding (x : Task.words) : Task.a x = BasicNative.entry {family} 0 x. Proof. reflexivity. Qed.
Example right_binding (x : Task.words) : Task.b x = BasicNative.entry {family} {style} x. Proof. reflexivity. Qed.
Example equivalence_binding : Task.equivalent = BasicNative.Equivalent (BasicDomain.valid {family}) (BasicNative.entry {family} 0) (BasicNative.entry {family} {style}). Proof. reflexivity. Qed.
Example refutation_binding (x oa ob : Task.words) : Task.refutationAt x oa ob = (BasicDomain.valid {family} x /\ BasicNative.entry {family} 0 x = Some oa /\ BasicNative.entry {family} {style} x = Some ob /\ oa <> ob). Proof. reflexivity. Qed.
'''
    (binding/'Binding.v').write_text(correspondence)
    logs.append(compile_rocq(binding, 'Binding', [(task, 'Trusted'), (original, 'Frozen'), (binding, 'Binding')]))
    (binding/'compile.log').write_text('\n'.join(logs))
    meta = {'pilot_id': row['pilot_id'], 'platform': 'rocq', 'public_sha256': tree_digest(task),
            'binding': 'rocq-kernel-checked-correspondence-for-both-branches',
            'source_goal': ctx['equivalence_goal'], 'source_context': row['source_context_id'],
            'frozen_source_sha256': {n: hashlib.sha256((source/n).read_bytes()).hexdigest() for n in ('BasicNative.v', 'BasicDomain.v')},
            'preparation_wall_seconds': time.monotonic()-started,
            'preparation_controller_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
            'preparation_model_tokens': None, 'preparation_accounting_scope': 'Isolated packaging; curator model usage not exposed',
            'final_proof_attempted': False}
    (package/'registry.json').write_text(json.dumps(meta, indent=2)+'\n')
    return bind_rocq_target(row, package, meta)


def main():
    os.umask(0o077)
    PACKAGES.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (PACKAGES/'activity.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        verify_freeze()
        eligible = {r['pilot_id'] for r in selection()[0]}
        rows = json.loads((PRIVATE/'mapping.json').read_text())['contexts']
        for row in rows:
            if row['pilot_id'] in eligible:
                for adapter in (prepare, prepare_rocq):
                    meta = adapter(row)
                    if meta:
                        print(json.dumps({'task': meta['pilot_id'], 'platform': meta['platform'], 'prepared': True}), flush=True)


if __name__ == '__main__':
    main()
