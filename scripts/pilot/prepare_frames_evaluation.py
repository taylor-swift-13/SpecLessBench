"""Isolate frozen frame streams and certify their record representation map."""
import hashlib
import json
import re
import resource
import time

from prepare_evaluation import ROOT, PACKAGES, compile_rocq
from prepare_classics_evaluation import declarations
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
