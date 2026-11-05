"""Prepare source-bound, single-pair evaluation packages (never gold proofs)."""
import json
import fcntl
import os
import re
import resource
import hashlib
import subprocess
import signal
import tempfile
import datetime as dt
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
COMPCERT = Path.home()/'.opam/five'


def run_compiler(folder, name, argv, env):
    """Keep per-command wall time and GNU time's process maximum RSS."""
    started = time.monotonic(); timed_out = False
    with tempfile.TemporaryDirectory(prefix='specless-compiler-cost-') as temp:
        metrics = Path(temp)/'rss.txt'; timer = Path('/usr/bin/time')
        command = [str(timer), '-f', '%M %U %S', '-o', str(metrics), '--', *argv] if timer.exists() else argv
        proc = subprocess.Popen(command, cwd=folder, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
        try:
            stdout, stderr = proc.communicate(timeout=180)
        except subprocess.TimeoutExpired:
            timed_out = True; os.killpg(proc.pid, signal.SIGKILL); stdout, stderr = proc.communicate()
        observed = metrics.read_text().splitlines()[-1].split() if metrics.exists() and metrics.read_text().strip() else []
        try:
            rss, user, system = int(observed[0])*1024, float(observed[1]), float(observed[2])
        except (IndexError, ValueError):
            rss = user = system = None
    row = {'ended_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'module': name, 'argv': argv,
           'status': 'timeout' if timed_out else 'exited', 'exit_code': proc.returncode,
           'wall_seconds': time.monotonic()-started, 'peak_rss_bytes': rss, 'user_seconds': user, 'system_seconds': system,
           'memory_scope': 'GNU time process maximum RSS, including waited-for children; not an aggregate cgroup peak or hosted-model memory',
           'model_tokens': None}
    with (folder.parent/'compile-costs.jsonl').open('a') as log:
        log.write(json.dumps(row)+'\n'); log.flush(); os.fsync(log.fileno())
    if timed_out or proc.returncode:
        (folder/(name+'.failure.log')).write_text(stdout+stderr)
        raise RuntimeError(name+(': compiler timeout\n' if timed_out else ':\n')+stdout+stderr)
    return stdout+stderr


def compile_rocq(folder, name, paths, toolchain=ROCQ):
    argv = [str(toolchain/'bin/coqc'), '-q', '-noglob']
    for path, logical in paths:
        argv += ['-Q', str(path), logical]
    return run_compiler(folder, name, argv+[str(folder/(name+'.v'))],
                        dict(os.environ, OCAMLFIND_CONF=str(toolchain/'lib/findlib.conf'), OCAMLPATH=str(toolchain/'lib')))


def compile_lean(folder, name, paths):
    return run_compiler(folder, name, [str(LEAN), '-j', '1', '-o', str(folder/(name+'.olean')), str(folder/(name+'.lean'))],
                        dict(os.environ, LEAN_PATH=':'.join(map(str, paths))))


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


def rocq_matrix_definition(name, style):
    header = f'''Definition {name} xs :=
  let r := Z.to_nat (iz xs 0) in let k := Z.to_nat (iz xs 1) in let c := Z.to_nat (iz xs 2) in
'''
    if style == 1:
        return header+'''  fold_left (fun out i => fold_left (fun out t => fold_left (fun out j =>
    put out (i*c+j) (iz out (i*c+j)+iz xs (3+i*k+t)*iz xs (3+r*k+t*c+j))%Z) (seq 0 c) out) (seq 0 k) out)
    (seq 0 r) (repeat 0%Z (r*c)).
'''
    index = 'j*k+t' if style == 2 else 't*c+j'
    return header+f'''  map (fun pos => let i := pos/c in let j := pos mod c in
    fold_left (fun a t => (a+iz xs (3+i*k+t)*iz xs (3+r*k+({index})))%Z) (seq 0 k) 0%Z) (seq 0 (r*c)).
'''


def rocq_queue_definition(name, style):
    push = '(front++[v],rear,out++[0%Z;0%Z])' if style == 0 else '(front,v::rear,out++[0%Z;0%Z])'
    transfer = '(front,rear)' if style == 0 else ('if Nat.eqb (length front) 0 then (reverse_rec rear,'+('rear' if style == 2 else '[]')+') else (front,rear)')
    return f'''Definition {name} xs :=
  let '(_,_,out) := fold_left (fun state i => let '(front,rear,out) := state in
    let op := iz xs (1+2*i) in let v := iz xs (2+2*i) in
    if Z.eqb op 0 then {push}
    else let '(f,r) := {transfer} in
    match f with [] => (f,r,out++[op;0%Z;0%Z]) | a::rest =>
      (if Z.eqb op 1 then rest else f,r,out++[op;1%Z;a]) end)
    (seq 0 (Z.to_nat (iz xs 0))) (([]:words),([]:words),([]:words)) in out.
'''


def prepare(row):
    """Native sequence/matrix adapters; other families remain pending."""
    ctx = row['context']; family = ctx.get('family_index')
    if ctx.get('tranche') != 'algorithms' or family not in (1, 2, 3, 4, 5):
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
    names = {1: ('reverseRec', 'reverseAcc'), 2: ('sumRec', 'sumAcc'), 3: (),
             4: ('matchAt', 'naiveSearch', 'fallback', 'prefixTable', 'kmpLoop', 'kmp'), 5: ('reverseRec',)}[family]
    definitions = ''.join(definition(native, n) for n in ('iz', 'finish', *names)).replace('mutant', 'mode')
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
    elif family == 4:
        source = 'import Lean\nnamespace Task\nabbrev Words := List Int\n'+definitions+'''
def inRange (v lo hi : Int) : Bool := lo ≤ v && v ≤ hi
def valid (xs : Words) : Prop :=
  (let a := iz xs 0; let b := iz xs 1
   inRange a 0 64 && inRange b 0 32 && xs.length == 2+a.toNat+b.toNat &&
     (xs.drop 2).all (fun v => inRange v 0 255)) = true
'''
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
        if family == 4:
            source += f'''def {name} (xs : Words) : Option Words := do
  let n := (iz xs 0).toNat; let m := (iz xs 1).toNat
  let text := (xs.drop 2).take n; let pat := (xs.drop (2+n)).take m
'''
            source += ('  let result ← some (naiveSearch text pat)\n' if name == 'a' else
                       '  let result ← kmp '+('true' if style == 2 else 'false')+' text pat\n')
            source += '  pure (finish [result])\n'
        else:
            source += f'def {name} (xs : Words) : Option Words :=\n'+data_prefix+f'  some (finish ({expr}))\n'
    source += '''def equivalent : Prop := ∀ x, valid x → ∃ o, a x = some o ∧ b x = some o
def refutationAt (x oa ob : Words) : Prop := valid x ∧ a x = some oa ∧ b x = some ob ∧ oa ≠ ob
end Task
'''
    if family == 4:
        # Task.pure is Lean's asynchronous Task constructor, not Option's pure.
        source = re.sub(r'(?<![A-Za-z0-9_.])pure\b', 'Pure.pure', source)
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
    if family == 4:
        helper = '''theorem fallback_eq (mode : Bool) (pat : Task.Words) (tab : List Nat) (b : Int) (fuel j : Nat) :
  Task.fallback mode pat tab b fuel j = SpecLessBenchBasic.fallback mode pat tab b fuel j := by
  induction fuel generalizing j with
  | zero => rfl
  | succ fuel ih => simp [Task.fallback, SpecLessBenchBasic.fallback, Task.iz, SpecLessBenchBasic.iz, ih]
theorem prefix_eq (pat : Task.Words) : Task.prefixTable pat = SpecLessBenchBasic.prefixTable pat := by
  simp [Task.prefixTable, SpecLessBenchBasic.prefixTable, fallback_eq, Task.iz, SpecLessBenchBasic.iz]
theorem loop_eq (mode : Bool) (text pat : Task.Words) (tab : List Nat) (fuel i j : Nat) :
  Task.kmpLoop mode text pat tab fuel i j = SpecLessBenchBasic.kmpLoop mode text pat tab fuel i j := by
  induction fuel generalizing i j with
  | zero => rfl
  | succ fuel ih => simp [Task.kmpLoop, SpecLessBenchBasic.kmpLoop, fallback_eq, Task.iz, SpecLessBenchBasic.iz, ih]
theorem kmp_eq (mode : Bool) (text pat : Task.Words) : Task.kmp mode text pat = SpecLessBenchBasic.kmp mode text pat := by
  simp [Task.kmp, SpecLessBenchBasic.kmp, prefix_eq, loop_eq]
'''
    for name in (names if family != 4 else ()):
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
        if family == 4 and name == 'b':
            helper += f'''theorem {name}_eq (x : Task.Words) : Task.{name} x = SpecLessBenchBasic.entry {family} {selected} x := by
  simp [Task.b, SpecLessBenchBasic.entry, Task.finish, SpecLessBenchBasic.finish, Task.iz, SpecLessBenchBasic.iz, kmp_eq]
'''
        elif family in (3, 4):
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
    if ctx.get('tranche') != 'algorithms' or family not in (1, 2, 3, 4, 5):
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
    style = int(styles[1]); names = {1: ('reverse_rec', 'reverse_acc'), 2: ('sum_rec', 'sum_acc'), 3: ('put',),
                                   4: ('obind', 'matches', 'naive_search', 'fallback', 'prefix_table', 'kmp_loop', 'kmp'), 5: ('reverse_rec',)}[family]
    def extract(name):
        match = re.search(r'^(?:Definition|Fixpoint) '+re.escape(name)+r'\b.*?(?=\n(?:Definition|Fixpoint|Notation) |\Z)', native, re.M | re.S)
        if not match:
            raise ValueError('Missing frozen Rocq definition: '+name)
        text = match.group().strip().replace('mutant', 'mode')+'\n'
        if name == 'obind':
            text += '''Notation "'let*' x ':=' c 'in' b" := (obind c (fun x => b)) (at level 200, x ident, c at level 100, b at level 200).
'''
        return text
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
    data_prefix = '  let data := firstn (Z.to_nat (iz xs 0)) (skipn 1 xs) in '
    if family == 3:
        text = text[:text.index('Definition in_range')]+rocq_matrix_definition('matrixA', 0)+rocq_matrix_definition('matrixB', style)+'''
Definition in_range v lo hi := Z.leb lo v && Z.leb v hi.
Definition valid (xs : words) : Prop :=
  (let a := iz xs 0 in let b := iz xs 1 in let c := iz xs 2 in
   let n := Z.to_nat a in let m := Z.to_nat b in let z := Z.to_nat c in
   in_range a 0 6 && in_range b 0 6 && in_range c 0 6 && Nat.eqb (length xs) (3+n*m+m*z) &&
   forallb (fun v => in_range v (-1000) 1000) (skipn 3 xs)) = true.
'''
        left, right, data_prefix = 'matrixA xs', 'matrixB xs', ''
    elif family == 4:
        text = text[:text.index('Definition in_range')]+'''
Definition in_range v lo hi := Z.leb lo v && Z.leb v hi.
Definition valid (xs : words) : Prop :=
  (let a := iz xs 0 in let b := iz xs 1 in
   in_range a 0 64 && in_range b 0 32 && Nat.eqb (length xs) (2+Z.to_nat a+Z.to_nat b) &&
   forallb (fun v => in_range v 0 255) (skipn 2 xs)) = true.
'''
    elif family == 5:
        text = text[:text.index('Definition in_range')]+rocq_queue_definition('queueA', 0)+rocq_queue_definition('queueB', style)+'''
Definition in_range v lo hi := Z.leb lo v && Z.leb v hi.
Definition valid (xs : words) : Prop :=
  (in_range (iz xs 0) 0 64 && Nat.eqb (length xs) (1+2*Z.to_nat (iz xs 0)) &&
   forallb (fun i => let op := iz xs (1+2*i) in let v := iz xs (2+2*i) in
     in_range op 0 2 && (if Z.eqb op 0 then in_range v (-1000000) 1000000 else Z.eqb v 0))
     (seq 0 (Z.to_nat (iz xs 0)))) = true.
'''
        left, right, data_prefix = 'queueA xs', 'queueB xs', ''
    for name, expression in (('a', left), ('b', right)):
        if family == 4:
            text += f'''Definition {name} (xs : words) : option words :=
  let n := Z.to_nat (iz xs 0) in let m := Z.to_nat (iz xs 1) in
  let text := firstn n (skipn 2 xs) in let pat := firstn m (skipn (2+n) xs) in
'''
            expression = 'Some (naive_search text pat)' if name == 'a' else ('kmp '+('true' if style == 2 else 'false')+' text pat')
            text += '  obind ('+expression+') (fun result => Some (finish [result])).\n'
        else:
            text += f'Definition {name} (xs : words) : option words :=\n'+data_prefix+f'Some (finish ({expression})).\n'
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
    from prepare_clight_evaluation import prepare_compcert
    from prepare_classics_evaluation import prepare_classics, prepare_classics_lean
    os.umask(0o077)
    PACKAGES.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (PACKAGES/'activity.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        verify_freeze()
        eligible = {r['pilot_id'] for r in selection()[0]}
        rows = json.loads((PRIVATE/'mapping.json').read_text())['contexts']
        for row in rows:
            if row['pilot_id'] in eligible:
                for adapter in (prepare, prepare_rocq, prepare_classics, prepare_classics_lean, prepare_compcert):
                    meta = adapter(row)
                    if meta:
                        print(json.dumps({'task': meta['pilot_id'], 'platform': meta['platform'], 'prepared': True}), flush=True)


if __name__ == '__main__':
    main()
