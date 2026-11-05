"""Isolate the frozen block/stream encoding pair; check source correspondence."""
import hashlib
import json
import re
import resource
import time

from prepare_evaluation import ROOT, PACKAGES, compile_lean, compile_rocq
from prepare_classics_evaluation import declarations, lean_declarations
from single_task_runner import tree_digest


def prepare_base64(row, platform):
    ctx = row['context']
    if ctx.get('tranche') != 'base64':
        return None
    package = PACKAGES/row['pilot_id']/platform
    if (package/'registry.json').exists():
        meta = json.loads((package/'registry.json').read_text())
        if tree_digest(package/'task') != meta['public_sha256']:
            raise ValueError('Existing encoding task changed')
        return meta
    if package.exists():
        raise ValueError('Incomplete encoding preparation needs inspection: '+str(package))
    started = time.monotonic(); task = package/'task'; binding = package/'binding'
    task.mkdir(parents=True, mode=0o700); binding.mkdir(mode=0o700)
    lean = platform == 'lean'; ext = '.lean' if lean else '.v'
    source = ROOT/'benchmarks/tasks/base64-core'/platform
    parse = lean_declarations if lean else declarations
    native = parse((source/('Base64Native'+ext)).read_text())
    domain = parse((source/('Base64Domain'+ext)).read_text())
    goals = parse((source/('Base64Goals'+ext)).read_text())
    selected = [goals[ctx[k]] for k in ('equivalence_goal', 'refutation_at_goal')]
    styles = re.findall(r'(?:Base64Native\.)?entry\s+0\s+(\d+)', selected[0])
    if len(styles) != 2 or styles[0] != '0' or styles[1] not in ('1', '2'):
        raise ValueError('Unexpected frozen encoding pair')
    style = styles[1]
    stream = native['stream']
    if lean:
        stream = stream.replace('(style : Nat) ', '', 1).replace('if style == 2 then min padding 1 else padding', 'min padding 1' if style == '2' else 'padding')
        entry = native['entry'].replace('(_family style : Nat) ', '', 1)
        pair = [entry.replace('def entry ', 'def '+name+' ', 1).replace(
            'if style == 0 then blocks 64 bytes else some (stream style bytes)',
            'blocks 64 bytes' if name == 'a' else 'some (stream bytes)') for name in ('a', 'b')]
        valid = domain['validFamilyB'].replace('def validFamilyB (_family : Nat)', 'def validB', 1)
        body = '\n'.join([d for n,d in native.items() if n in ('Words','get','alphabet','blocks','emitSextets')]+[stream,valid,
            'def valid (xs : Words) : Prop := validB xs = true',*pair])+'''
def equivalent : Prop := ∀ x, valid x → ∃ o, a x = some o ∧ b x = some o
def refutationAt (x oa ob : Words) : Prop := valid x ∧ a x = some oa ∧ b x = some ob ∧ oa ≠ ob
'''
        body = re.sub(r'(?<![A-Za-z0-9_.])pure\b','Pure.pure',body)
        body = re.sub(r'\bget\b', 'wordAt', body)
        (task/'Task.lean').write_text('import Lean\nnamespace Task\n'+body+'end Task\n')
        (task/'Obligation.lean').write_text('import Task\nnamespace Obligation\ndef goal : Prop := Task.equivalent\nend Obligation\n')
    else:
        stream = stream.replace('Definition stream style bytes', 'Definition stream bytes',1).replace(
            'if Nat.eqb style 2 then Nat.min padding 1 else padding','Nat.min padding 1' if style == '2' else 'padding')
        entry = native['entry'].replace('(_family style:nat) ', '', 1)
        pair = [entry.replace('Definition entry ', 'Definition '+name+' ',1).replace(
            'if Nat.eqb style 0 then blocks 64 bytes else Some (stream style bytes)',
            'blocks 64 bytes' if name == 'a' else 'Some (stream bytes)') for name in ('a','b')]
        valid = domain['valid_familyb'].replace('Definition valid_familyb (_family:nat)', 'Definition validb',1)
        body = '\n'.join([d for n,d in native.items() if n in ('words','get','alphabet','blocks','emit_sextets')]+[stream,valid,
            'Definition valid xs : Prop := validb xs = true.',*pair])+'''
Definition equivalent : Prop := forall x, valid x -> exists o, a x = Some o /\ b x = Some o.
Definition refutationAt (x oa ob : words) : Prop := valid x /\ a x = Some oa /\ b x = Some ob /\ oa <> ob.
'''
        (task/'Task.v').write_text('From Coq Require Import ZArith List Bool.\nImport ListNotations.\nOpen Scope nat_scope.\n'+body)
        (task/'Obligation.v').write_text('From Trusted Require Import Task.\nDefinition goal : Prop := Task.equivalent.\n')
    if any(re.search(r'\bstyle\b', d) for d in (stream,*pair)):
        raise ValueError('Unresolved encoding dispatcher')
    original = ROOT/('_build/pilot-v1/base64-'+platform+'-binding');original.mkdir(parents=True,exist_ok=True)
    paths = [task,original] if lean else [(task,'Trusted'),(binding,'Binding'),(original,'Frozen')]
    def compile_at(folder,name):
        return compile_lean(folder,name,paths) if lean else compile_rocq(folder,name,paths)
    logs = [compile_at(task,n) for n in ('Task','Obligation')]
    for name in ('Base64Native','Base64Domain')+ (('Base64Goals',) if lean else ()):
        src = source/(name+ext);dest = original/src.name
        if not dest.exists() or dest.read_bytes()!=src.read_bytes() or not (original/(name+('.olean' if lean else '.vo'))).exists():
            dest.write_bytes(src.read_bytes());logs.append(compile_at(original,name))
    if lean:
        bridge = '''import Task
import Base64Goals
theorem blocks_eq (fuel : Nat) (xs : List Nat) : Task.blocks fuel xs = SpecLessBenchBase64.blocks fuel xs := by
  induction fuel generalizing xs with
  | zero => cases xs <;> rfl
  | succ fuel ih => cases xs with
    | nil => rfl
    | cons a tail =>
      simp only [Task.blocks, SpecLessBenchBase64.blocks, ih]
      rfl
theorem emit_eq (fuel buffer bits : Nat) (out : Task.Words) : Task.emitSextets fuel buffer bits out = SpecLessBenchBase64.emitSextets fuel buffer bits out := by
  induction fuel generalizing buffer bits out with
  | zero => rfl
  | succ fuel ih =>
    simp only [Task.emitSextets, SpecLessBenchBase64.emitSextets, ih]
    rfl
'''+f'''theorem stream_eq : Task.stream = SpecLessBenchBase64.stream {style} := by
  have h : Task.emitSextets = SpecLessBenchBase64.emitSextets := by
    funext fuel buffer bits out
    exact emit_eq fuel buffer bits out
  unfold Task.stream SpecLessBenchBase64.stream
  rw [h]
  rfl
theorem a_eq : Task.a = SpecLessBenchBase64.entry 0 0 := by
  have h : Task.blocks = SpecLessBenchBase64.blocks := by
    funext fuel xs
    exact blocks_eq fuel xs
  exact congrArg (fun (f : Nat → List Nat → Option Task.Words) => fun (xs : Task.Words) => do
    let bytes := ((xs.drop 1).take (Task.get xs 0).toNat).map Int.toNat
    let out ← f 64 bytes
    Pure.pure (Int.ofNat out.length::out)) h
theorem b_eq : Task.b = SpecLessBenchBase64.entry 0 {style} := by
  exact congrArg (fun (f : List Nat → Task.Words) => fun (xs : Task.Words) => do
    let bytes := ((xs.drop 1).take (Task.get xs 0).toNat).map Int.toNat
    let out ← some (f bytes)
    Pure.pure (Int.ofNat out.length::out)) stream_eq
theorem valid_eq : Task.valid = SpecLessBenchBase64.valid 0 := by rfl
example : Task.equivalent = SpecLessBenchBase64.{ctx['equivalence_goal']} := by
  unfold Task.equivalent SpecLessBenchBase64.{ctx['equivalence_goal']} SpecLessBenchBase64.Equivalent
  rw [valid_eq,a_eq,b_eq]
example (x oa ob : Task.Words) : Task.refutationAt x oa ob = SpecLessBenchBase64.{ctx['refutation_at_goal']} x oa ob := by
  unfold Task.refutationAt SpecLessBenchBase64.{ctx['refutation_at_goal']} SpecLessBenchBase64.RefutationAt
  rw [valid_eq,a_eq,b_eq]
'''
    else:
        (binding/'FrozenTarget.v').write_text('From Frozen Require Import Base64Native Base64Domain.\n'+'\n'.join(selected)+'\n')
        logs.append(compile_at(binding,'FrozenTarget'))
        bridge = 'From Coq Require Import ZArith List Bool.\nImport ListNotations.\nOpen Scope nat_scope.\nFrom Trusted Require Import Task.\nFrom Frozen Require Import Base64Native Base64Domain.\nFrom Binding Require Import FrozenTarget.\n'
        helpers = []
        for name in ('get','alphabet','blocks','emit_sextets'):
            rewrites = ''.join('try rewrite clone_'+n+'.\n' for n in helpers if re.search(r'\b'+n+r'\b',native[name]))
            bridge += f'Lemma clone_{name} : @Task.{name} = @Base64Native.{name}.\nProof. unfold Task.{name}, Base64Native.{name}.\n'+rewrites+'reflexivity. Qed.\n'
            helpers.append(name)
        bridge += f'''Lemma clone_stream : Task.stream = Base64Native.stream {style}.
Proof. unfold Task.stream, Base64Native.stream. rewrite clone_emit_sextets, clone_alphabet. reflexivity. Qed.
Opaque Task.blocks Base64Native.blocks Task.stream Base64Native.stream.
Lemma a_eq : Task.a = Base64Native.entry 0 0.
Proof. exact (@f_equal _ (Task.words -> option Task.words)
 (fun f => fun xs => let bytes:=map Z.to_nat (firstn (Z.to_nat (Task.get xs 0)) (skipn 1 xs)) in
 match f 64 bytes with None=>None|Some out=>Some (Z.of_nat (length out)::out) end)
 Task.blocks Base64Native.blocks clone_blocks). Qed.
Lemma b_eq : Task.b = Base64Native.entry 0 {style}.
Proof. exact (@f_equal _ (Task.words -> option Task.words)
 (fun f => fun xs => let bytes:=map Z.to_nat (firstn (Z.to_nat (Task.get xs 0)) (skipn 1 xs)) in
 match Some (f bytes) with None=>None|Some out=>Some (Z.of_nat (length out)::out) end)
 Task.stream (Base64Native.stream {style}) clone_stream). Qed.
Lemma valid_eq : Task.valid = Base64Domain.valid 0. Proof. reflexivity. Qed.
Example equivalent_binding : Task.equivalent = FrozenTarget.{ctx['equivalence_goal']}.
Proof. unfold Task.equivalent, FrozenTarget.{ctx['equivalence_goal']}, Base64Native.Equivalent.
rewrite <- a_eq, <- b_eq, <- valid_eq. reflexivity. Qed.
Example refutation_binding (x oa ob : Task.words) : Task.refutationAt x oa ob = FrozenTarget.{ctx['refutation_at_goal']} x oa ob.
Proof. unfold Task.refutationAt, FrozenTarget.{ctx['refutation_at_goal']}, Base64Native.RefutationAt.
rewrite <- a_eq, <- b_eq, <- valid_eq. reflexivity. Qed.
'''
    if lean:
        bridge = bridge.replace('Task.get ', 'Task.wordAt ')
    (binding/('Binding'+ext)).write_text(bridge);logs.append(compile_at(binding,'Binding'))
    (binding/'compile.log').write_text('\n'.join(logs))
    meta = {'pilot_id':row['pilot_id'],'platform':platform,'public_sha256':tree_digest(task),
        'binding':'kernel-checked-exact-frozen-target-for-both-branches','source_context':row['source_context_id'],
        'source_goal':ctx['equivalence_goal'],'frozen_source_sha256':{n:hashlib.sha256((source/(n+ext)).read_bytes()).hexdigest() for n in ('Base64Native','Base64Domain','Base64Goals')},
        'preparation_wall_seconds':time.monotonic()-started,'preparation_controller_peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
        'compiler_costs':'compile-costs.jsonl','preparation_model_tokens':None,'final_proof_attempted':False}
    (package/'registry.json').write_text(json.dumps(meta,indent=2)+'\n');return meta


def prepare_base64_rocq(row):
    return prepare_base64(row,'rocq')


def prepare_base64_lean(row):
    return prepare_base64(row,'lean')
