"""Isolate frozen frame streams and certify their record representation map."""
import hashlib
import json
import re
import resource
import time

from prepare_evaluation import ROOT, PACKAGES, compile_rocq, compile_lean
from prepare_classics_evaluation import declarations, lean_declarations
from single_task_runner import tree_digest


def prepare_frames_rocq(row):
    ctx = row['context']
    if ctx.get('tranche') != 'stateful' or ctx.get('family_index') != 0:
        return None
    package = PACKAGES / row['pilot_id'] / 'rocq'
    if (package / 'registry.json').exists():
        meta = json.loads((package / 'registry.json').read_text())
        if tree_digest(package / 'task') != meta['public_sha256']:
            raise ValueError('Existing frame package changed')
        return meta
    if package.exists():
        raise ValueError('Incomplete preparation requires inspection: ' + str(package))
    started = time.monotonic()
    source = ROOT / 'benchmarks/tasks/stateful-core/rocq'
    raw = (source / 'StatefulNative.v').read_text()
    native = declarations(raw)
    domains = declarations((source / 'StatefulDomain.v').read_text())
    goals = declarations((source / 'StatefulGoals.v').read_text())
    selected = [goals[ctx[k]] for k in ('equivalence_goal', 'refutation_at_goal')]
    styles = re.findall(r'StatefulNative.entry\s+0\s+(\d+)', selected[0])
    if styles not in (['0', '1'], ['0', '2']):
        raise ValueError('Unexpected frozen frame pair')
    record = re.search(r'^Record stream_state:.*?\.', raw, re.M | re.S).group()
    names = list(native)
    names = ['words', 'iz', 'put', 'finish', 'obind'] + names[names.index('smake'):names.index('frames')]
    pair = [re.sub(r'\bstyle\b', style, native['frames'].replace('Definition frames style xs', 'Definition ' + name + ' xs', 1))
            for name, style in zip(('a', 'b'), styles)]
    pre, match = domains['validb'].split(':=', 1)[1].split('match family with', 1)
    clauses = re.findall(r'\n \| (.*?)=>(.*?)(?=\n \| |\n end\.)', match, re.S)
    bodies = [body for pat, body in clauses if pat.strip() == 'O']
    if len(bodies) != 1:
        raise ValueError('Missing frozen frame domain')
    valid = 'Definition valid (xs:words) : Prop := (' + pre + bodies[0] + ')=true.'
    notation = 'Notation "\'let*\' x \':=\' c \'in\' b" := (obind c (fun x=>b)) (at level 200,x ident,c at level 100,b at level 200).'
    header = 'From Coq Require Import ZArith List Bool.\nImport ListNotations.\nOpen Scope nat_scope.\n'
    public = header + '\n'.join([native[n] for n in names[:5]] + [notation, record] + [native[n] for n in names[5:]] +
                               [domains['get'], domains['in_range'], valid, *pair]) + '''
Definition equivalent : Prop := forall x, valid x -> exists o, a x=Some o /\ b x=Some o.
Definition refutationAt (x oa ob:words) : Prop := valid x /\ a x=Some oa /\ b x=Some ob /\ oa<>ob.
'''
    task = package / 'task'; binding = package / 'binding'
    task.mkdir(parents=True, mode=0o700); binding.mkdir(mode=0o700)
    (task / 'Task.v').write_text(public)
    (task / 'Obligation.v').write_text('From Trusted Require Import Task.\nDefinition goal : Prop := Task.equivalent.\n')
    original = ROOT / '_build/pilot-v1/stateful-rocq-binding'
    original.mkdir(parents=True, exist_ok=True)
    paths = [(task, 'Trusted'), (binding, 'Binding'), (original, 'Frozen')]
    def compile_at(folder, name):
        return compile_rocq(folder, name, paths)
    logs = [compile_at(task, n) for n in ('Task', 'Obligation')]
    for name in ('StatefulNative', 'StatefulDomain'):
        src = source / (name + '.v'); dest = original / src.name
        if not dest.exists() or dest.read_bytes() != src.read_bytes() or not (original / (name + '.vo')).exists():
            dest.write_bytes(src.read_bytes()); logs.append(compile_at(original, name))
    (binding / 'FrozenTarget.v').write_text('From Frozen Require Import StatefulNative StatefulDomain.\n' + '\n'.join(selected) + '\n')
    logs.append(compile_at(binding, 'FrozenTarget'))
    command = native['frames'].split('fold_left(', 1)[1].split('\n   (seq', 1)[0].rsplit(')', 1)[0]
    tokens = set(native) | {'stream_state', 'sd', 'sh', 'sn', 'sb', 'sc', 'sp'}
    def qualify(text, module):
        return re.sub(r'\b[A-Za-z_][A-Za-z_0-9]*\b', lambda m: module + '.' + m.group() if m.group() in tokens else m.group(), text)
    bridge = header + 'From Trusted Require Import Task.\nFrom Frozen Require Import StatefulNative StatefulDomain.\nFrom Binding Require Import FrozenTarget.\n'
    bridge += 'Definition task_command style (xs:Task.words) := ' + qualify(command, 'Task') + '.\n'
    bridge += 'Definition source_command style (xs:StatefulNative.words) := ' + qualify(command, 'StatefulNative') + '.\n'
    bridge += '''
Definition lift (s:Task.stream_state) : StatefulNative.stream_state :=
 {| StatefulNative.sd:=Task.sd s; StatefulNative.sh:=Task.sh s;
    StatefulNative.sn:=Task.sn s; StatefulNative.sb:=Task.sb s;
    StatefulNative.sc:=Task.sc s; StatefulNative.sp:=Task.sp s |}.
Definition lift_pair (p:Task.stream_state*Task.words) := (lift (fst p),snd p).
Definition lift_triple (p:Task.stream_state*nat*Task.words) := let '(s,n,out):=p in (lift s,n,out).
Ltac split_tests := repeat match goal with
 | |- context [if ?b then _ else _] => destruct b eqn:?; cbn
 end.
Lemma push_lift style s c : lift (Task.push_byte style s c) = StatefulNative.push_byte style (lift s) c.
Proof. destruct s; reflexivity. Qed.
Lemma push_fold_lift style xs s : lift (fold_left (Task.push_byte style) xs s) =
 fold_left (StatefulNative.push_byte style) xs (lift s).
Proof. revert s; induction xs; intros; cbn; [reflexivity|]. rewrite <- push_lift. apply IHxs. Qed.
Lemma drain_lift style fuel s n out : option_map lift_triple (Task.drain_frames style fuel s n out) =
 StatefulNative.drain_frames style fuel (lift s) n out.
Proof. revert s n out; induction fuel; intros; destruct s;
 cbn [Task.drain_frames StatefulNative.drain_frames lift];
 unfold Task.checksum_frame, StatefulNative.checksum_frame; cbn;
 split_tests; try rewrite IHfuel; reflexivity. Qed.
Opaque Task.drain_frames StatefulNative.drain_frames.
Lemma feed_lift style s xs : option_map lift_triple (Task.feed_chunk style s xs) =
 StatefulNative.feed_chunk style (lift s) xs.
Proof. destruct s; unfold Task.feed_chunk, StatefulNative.feed_chunk; cbn; split_tests;
 try rewrite drain_lift; try rewrite push_fold_lift; reflexivity. Qed.
Opaque Task.feed_chunk StatefulNative.feed_chunk.
Lemma observe_lift style op s n out : Task.stream_observe style op s n out =
 StatefulNative.stream_observe style op (lift s) n out.
Proof. destruct s; reflexivity. Qed.
Lemma initial_lift style : lift (Task.stream_init style) = StatefulNative.stream_init style.
Proof. reflexivity. Qed.
Lemma finish_lift s : lift (Task.finish_stream s) = StatefulNative.finish_stream (lift s).
Proof. destruct s; unfold Task.finish_stream, StatefulNative.finish_stream; cbn; split_tests; reflexivity. Qed.
Lemma command_lift style xs st i : option_map lift_pair (task_command style xs st i) =
 source_command style xs (option_map lift_pair st) i.
Proof. destruct st as [[s out]|]; [|reflexivity].
 unfold task_command, source_command; cbn [Task.obind StatefulNative.obind option_map lift_pair];
 change StatefulNative.iz with Task.iz;
 destruct (Z.eqb (Task.iz xs (1+10*i)) 0) eqn:E.
 - rewrite <- feed_lift. destruct (Task.feed_chunk style s (firstn (Z.to_nat (Task.iz xs (1+10*i+1))) (skipn (1+10*i+2) xs))) as [[[next n] data]|] eqn:F;
   cbn in F; cbn; try rewrite F; cbn; try rewrite observe_lift; reflexivity.
 - destruct (Z.eqb (Task.iz xs (1+10*i)) 1); cbn;
   try rewrite <- finish_lift; try rewrite <- initial_lift; try rewrite <- observe_lift; reflexivity.
Qed.
Lemma commands_lift style xs is st : option_map lift_pair (fold_left (task_command style xs) is st) =
 fold_left (source_command style xs) is (option_map lift_pair st).
Proof. revert st; induction is; intros; cbn; [reflexivity|]. rewrite <- command_lift. apply IHis. Qed.
'''
    for name, style in zip(('a', 'b'), styles):
        bridge += f'''Lemma {name}_binding xs : Task.{name} xs = StatefulNative.entry 0 {style} xs.
Proof. change ((match fold_left (task_command {style} xs) (seq 0 (Z.to_nat (Task.iz xs 0)))
 (Some (Task.stream_init {style},([]:Task.words))) with Some result=>Some(Task.finish(snd result))|None=>None end) =
 (match fold_left (source_command {style} xs) (seq 0 (Z.to_nat (Task.iz xs 0)))
 (Some (StatefulNative.stream_init {style},([]:Task.words))) with Some result=>Some(StatefulNative.finish(snd result))|None=>None end)).
 rewrite <- initial_lift.
 change (Some (lift (Task.stream_init {style}),([]:Task.words))) with
 (option_map lift_pair (Some (Task.stream_init {style},([]:Task.words)))).
 rewrite <- commands_lift.
 destruct (fold_left (task_command {style} xs) (seq 0 (Z.to_nat (Task.iz xs 0))) (Some(Task.stream_init {style},([]:Task.words)))) as [[s out]|]; reflexivity.
Qed.
'''
    bridge += f'''Lemma domain_binding : Task.valid = StatefulDomain.valid 0. Proof. reflexivity. Qed.
Example equivalent_binding : Task.equivalent <-> FrozenTarget.{ctx['equivalence_goal']}.
Proof. unfold Task.equivalent, FrozenTarget.{ctx['equivalence_goal']}, StatefulNative.Equivalent.
 split; intros H x V; destruct (H x V) as [o [A B]]; exists o; split.
 - rewrite <- a_binding. exact A.
 - rewrite <- b_binding. exact B.
 - rewrite a_binding. exact A.
 - rewrite b_binding. exact B.
Qed.
Example refutation_binding (x oa ob:Task.words) : Task.refutationAt x oa ob <-> FrozenTarget.{ctx['refutation_at_goal']} x oa ob.
Proof. unfold Task.refutationAt, FrozenTarget.{ctx['refutation_at_goal']}, StatefulNative.RefutationAt.
 rewrite <- domain_binding, <- a_binding, <- b_binding. tauto. Qed.
Print Assumptions equivalent_binding.
Print Assumptions refutation_binding.
'''
    (binding / 'Binding.v').write_text(bridge)
    logs.append(compile_at(binding, 'Binding'))
    (binding / 'compile.log').write_text('\n'.join(logs))
    meta = {'pilot_id': row['pilot_id'], 'platform': 'rocq', 'public_sha256': tree_digest(task),
            'binding': 'rocq-kernel-checked-record-transport-and-exact-frozen-target',
            'source_context': row['source_context_id'], 'source_goal': ctx['equivalence_goal'],
            'frozen_source_sha256': {n: hashlib.sha256((source / (n + '.v')).read_bytes()).hexdigest()
                                     for n in ('StatefulNative', 'StatefulDomain', 'StatefulGoals')},
            'preparation_wall_seconds': time.monotonic() - started,
            'preparation_controller_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'compiler_costs': 'compile-costs.jsonl', 'preparation_model_tokens': None,
            'final_proof_attempted': False}
    (package / 'registry.json').write_text(json.dumps(meta, indent=2) + '\n')
    return meta


def prepare_frames_lean(row):
    ctx = row['context']
    if ctx.get('tranche') != 'stateful' or ctx.get('family_index') != 0:
        return None
    package = PACKAGES / row['pilot_id'] / 'lean'
    if (package / 'registry.json').exists():
        meta = json.loads((package / 'registry.json').read_text())
        if tree_digest(package / 'task') != meta['public_sha256']:
            raise ValueError('Existing frame package changed')
        return meta
    if package.exists():
        raise ValueError('Incomplete preparation requires inspection: ' + str(package))
    started = time.monotonic()
    source = ROOT / 'benchmarks/tasks/stateful-core/lean'
    raw = (source / 'StatefulNative.lean').read_text()
    native = lean_declarations(raw)
    domains = lean_declarations((source / 'StatefulDomain.lean').read_text())
    goals = lean_declarations((source / 'StatefulGoals.lean').read_text())
    styles = re.findall(r'entry\s+0\s+(\d+)', goals[ctx['equivalence_goal']])
    if styles not in (['0', '1'], ['0', '2']):
        raise ValueError('Unexpected frozen frame pair')
    record = raw.split('structure StreamState where', 1)[1].split('def streamInit', 1)[0]
    names = list(native)
    names = ['Words', 'getOr', 'iz', 'put', 'finish'] + names[names.index('streamInit'):names.index('frames')]
    pair = [re.sub(r'\bstyle\b', style, native['frames'].replace('def frames (style : Nat)', 'def ' + name, 1)).replace('pure (', 'return (')
            for name, style in zip(('a', 'b'), styles)]
    pre, branches = domains['validB'].split(':=', 1)[1].split('match family with', 1)
    body = branches.split('  | 0 =>', 1)[1].split('  | 1 =>', 1)[0]
    valid = 'def valid (xs : Words) : Prop := (' + pre + body + ') = true\n'
    task = package / 'task'; binding = package / 'binding'
    task.mkdir(parents=True, mode=0o700); binding.mkdir(mode=0o700)
    (task / 'Task.lean').write_text('import Lean\nnamespace Task\n' + '\n'.join(
        [native[n] for n in names[:5]] + ['structure StreamState where' + record] + [native[n] for n in names[5:]] +
        [domains['inRange'], valid, *pair]) + '''
def equivalent : Prop := ∀ x, valid x → ∃ o, a x=some o ∧ b x=some o
def refutationAt (x oa ob : Words) : Prop := valid x ∧ a x=some oa ∧ b x=some ob ∧ oa≠ob
end Task
''')
    (task / 'Obligation.lean').write_text('import Task\nnamespace Obligation\ndef goal : Prop := Task.equivalent\nend Obligation\n')
    original = ROOT / '_build/pilot-v1/stateful-lean-binding'
    original.mkdir(parents=True, exist_ok=True)
    def compile_at(folder, name):
        return compile_lean(folder, name, [task, original])
    logs = [compile_at(task, n) for n in ('Task', 'Obligation')]
    for name in ('StatefulNative', 'StatefulDomain', 'StatefulGoals'):
        src = source / (name + '.lean'); dest = original / src.name
        if not dest.exists() or dest.read_bytes() != src.read_bytes() or not (original / (name + '.olean')).exists():
            dest.write_bytes(src.read_bytes()); logs.append(compile_at(original, name))
    bridge = '''import Task
import StatefulGoals
open SpecLessBenchStateful
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000
set_option backward.isDefEq.respectTransparency false
def lift (s : Task.StreamState) : StreamState := ⟨s.data,s.head,s.count,s.base,s.code,s.pos⟩
def liftPair (p : Task.StreamState × Task.Words) : StreamState × Words := (lift p.1,p.2)
def liftTriple (p : Task.StreamState × Nat × Task.Words) : StreamState × Nat × Words := (lift p.1,p.2)
theorem push_lift (style : Nat) (s : Task.StreamState) (c : Int) :
  lift (Task.pushByte style s c) = pushByte style (lift s) c := by rfl
theorem push_fold_lift (style : Nat) (xs : Task.Words) (s : Task.StreamState) :
  lift (xs.foldl (Task.pushByte style) s) = xs.foldl (pushByte style) (lift s) := by
  induction xs generalizing s with
  | nil => rfl
  | cons c xs ih => simpa only [List.foldl_cons, push_lift] using ih (Task.pushByte style s c)
theorem drain_lift (style fuel : Nat) (s : Task.StreamState) (n : Nat) (out : Task.Words) :
  Option.map liftTriple (Task.drainFrames style fuel s n out) = drainFrames style fuel (lift s) n out := by
  have map_if (P : Prop) [Decidable P] (a b : Option (Task.StreamState × Nat × Task.Words)) :
    Option.map liftTriple (if P then a else b) = if P then Option.map liftTriple a else Option.map liftTriple b := by
    split <;> rfl
  induction fuel generalizing s n out with
  | zero =>
    dsimp only [Task.drainFrames, drainFrames]
    simp only [map_if, Option.map_some, Option.map_none]
    rfl
  | succ fuel ih =>
    dsimp only [Task.drainFrames, drainFrames]
    simp only [map_if, Option.map_some, Option.map_none, ih]
    rfl
theorem feed_lift (style : Nat) (s : Task.StreamState) (xs : Task.Words) :
  Option.map liftTriple (Task.feedChunk style s xs) = feedChunk style (lift s) xs := by
  cases s
  dsimp only [Task.feedChunk, feedChunk, lift]
  split
  · rfl
  · split <;> try simp_all
    all_goals rw [drain_lift]
    all_goals try rw [push_fold_lift]
    all_goals rfl
theorem finish_lift (s : Task.StreamState) : lift (Task.finishStream s) = finishStream (lift s) := by
  cases s
  dsimp only [Task.finishStream, finishStream, Task.streamError, streamError, lift]
  repeat first | rfl | split
theorem observe_lift (style : Nat) (op : Int) (s : Task.StreamState) (n : Nat) (out : Task.Words) :
  Task.streamObserve style op s n out = streamObserve style op (lift s) n out := by rfl
def taskCommand (style : Nat) (xs : Task.Words) (state : Task.StreamState × Task.Words) (i : Nat) : Option (Task.StreamState × Task.Words) := do
  let (s,out) := state
  let p := 1+10*i; let op := Task.iz xs p; let len := (Task.iz xs (p+1)).toNat
  let (next,n,data) ← if op == 0 then Task.feedChunk style s ((xs.drop (p+2)).take len)
    else some (if op == 1 then Task.finishStream s else Task.streamInit style,0,[])
  return (next,out++Task.streamObserve style op next n data)
def sourceCommand (style : Nat) (xs : Words) (state : StreamState × Words) (i : Nat) : Option (StreamState × Words) := do
  let (s,out) := state
  let p := 1+10*i; let op := iz xs p; let len := (iz xs (p+1)).toNat
  let (next,n,data) ← if op == 0 then feedChunk style s ((xs.drop (p+2)).take len)
    else some (if op == 1 then finishStream s else streamInit style,0,[])
  return (next,out++streamObserve style op next n data)
theorem command_lift (style : Nat) (xs : Task.Words) (p : Task.StreamState × Task.Words) (i : Nat) :
  Option.map liftPair (taskCommand style xs p i) = sourceCommand style xs (liftPair p) i := by
  cases p with
  | mk s out =>
    unfold taskCommand sourceCommand
    dsimp only [liftPair]
    by_cases h0 : (Task.iz xs (1+10*i) == 0) = true
    · simp only [show iz = Task.iz from rfl, if_pos h0]
      rw [← feed_lift]
      cases Task.feedChunk style s ((xs.drop (1+10*i+2)).take (Task.iz xs (1+10*i+1)).toNat) with
      | none => rfl
      | some result =>
        cases result with
        | mk next rest =>
          cases rest
          simp only [Option.map_some, Option.bind_some]
          rfl
    · simp only [show iz = Task.iz from rfl, if_neg h0]
      by_cases h1 : (Task.iz xs (1+10*i) == 1) = true
      · simp only [if_pos h1, ← finish_lift]
        rfl
      · simp only [if_neg h1]
        rfl
theorem commands_lift (style : Nat) (xs : Task.Words) (is : List Nat) (p : Task.StreamState × Task.Words) :
  Option.map liftPair (is.foldlM (taskCommand style xs) p) = is.foldlM (sourceCommand style xs) (liftPair p) := by
  induction is generalizing p with
  | nil => rfl
  | cons i is ih =>
    simp only [List.foldlM_cons]
    rw [← command_lift]
    cases taskCommand style xs p i with
    | none => rfl
    | some next => exact ih next
'''
    for name, style in zip(('a', 'b'), styles):
        bridge += f'''theorem {name}_binding : Task.{name} = entry 0 {style} := by
  funext xs
  change (((List.range (Task.iz xs 0).toNat).foldlM (taskCommand {style} xs) (Task.streamInit {style},[])).bind
    (fun result => some (Task.finish result.2))) =
    (((List.range (Task.iz xs 0).toNat).foldlM (sourceCommand {style} xs) (streamInit {style},[])).bind
    (fun result => some (finish result.2)))
  have h := commands_lift {style} xs (List.range (Task.iz xs 0).toNat) (Task.streamInit {style},[])
  have init : liftPair (Task.streamInit {style},[]) = (streamInit {style},[]) := rfl
  rw [init] at h
  rw [← h]
  cases (List.range (Task.iz xs 0).toNat).foldlM (taskCommand {style} xs) (Task.streamInit {style},[]) <;> rfl
'''
    bridge += f'''theorem domain_binding : Task.valid = valid 0 := by rfl
theorem equivalent_binding : Task.equivalent = {ctx['equivalence_goal']} := by
  unfold Task.equivalent {ctx['equivalence_goal']} Equivalent
  rw [domain_binding, a_binding, b_binding]
theorem refutation_binding (x oa ob : Task.Words) : Task.refutationAt x oa ob = {ctx['refutation_at_goal']} x oa ob := by
  unfold Task.refutationAt {ctx['refutation_at_goal']} RefutationAt
  rw [domain_binding, a_binding, b_binding]
#print axioms equivalent_binding
#print axioms refutation_binding
'''
    (binding / 'Binding.lean').write_text(bridge)
    logs.append(compile_at(binding, 'Binding'))
    (binding / 'compile.log').write_text('\n'.join(logs))
    meta = {'pilot_id': row['pilot_id'], 'platform': 'lean', 'public_sha256': tree_digest(task),
            'binding': 'lean-kernel-checked-record-transport-and-exact-frozen-target',
            'source_context': row['source_context_id'], 'source_goal': ctx['equivalence_goal'],
            'frozen_source_sha256': {n: hashlib.sha256((source / (n + '.lean')).read_bytes()).hexdigest()
                                     for n in ('StatefulNative', 'StatefulDomain', 'StatefulGoals')},
            'preparation_wall_seconds': time.monotonic() - started,
            'preparation_controller_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'compiler_costs': 'compile-costs.jsonl', 'preparation_model_tokens': None,
            'final_proof_attempted': False}
    (package / 'registry.json').write_text(json.dumps(meta, indent=2) + '\n')
    return meta
