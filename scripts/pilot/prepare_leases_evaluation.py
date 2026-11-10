"""Isolate frozen lease tables and certify lease/table representation transport."""
import hashlib
import json
import re
import resource
import time

from prepare_evaluation import ROOT, PACKAGES, compile_rocq
from prepare_classics_evaluation import declarations
from single_task_runner import tree_digest


LEASE_BRIDGE = '''
Definition lift_lease (x:Task.lease) : SystemsNative.lease :=
 SystemsNative.Lease (Task.live x) (Task.value x) (Task.deadline x).
Definition lift_state (s:Task.table) : SystemsNative.table :=
 SystemsNative.Table (Task.clock s) (map lift_lease (Task.entries s)) (Task.wheel s).
Definition lift_pair (p:Task.table*Task.words) := (lift_state(fst p),snd p).
Lemma table_lift c es w : lift_state(Task.Table c es w) =
 SystemsNative.Table c(map lift_lease es)w.
Proof. reflexivity. Qed.
Lemma nth_lift es key : lift_lease(nth key es Task.no_lease) =
 nth key(map lift_lease es)SystemsNative.no_lease.
Proof. revert key; induction es; intros [|key]; cbn; try reflexivity; apply IHes. Qed.
Lemma replace_lift es key x : map lift_lease(Task.replace_at es key x) =
 SystemsNative.replace_at(map lift_lease es)key(lift_lease x).
Proof. unfold Task.replace_at,SystemsNative.replace_at; repeat rewrite map_app;
 rewrite firstn_map,skipn_map; reflexivity. Qed.
Lemma lease_lift s key : lift_lease(Task.lease_at s key) = SystemsNative.lease_at(lift_state s)key.
Proof. unfold Task.lease_at,SystemsNative.lease_at; change
 (lift_lease(nth key(Task.entries s)Task.no_lease) = nth key(map lift_lease(Task.entries s))SystemsNative.no_lease).
 apply nth_lift. Qed.
Opaque Task.lease_at SystemsNative.lease_at.
Ltac split_tests := repeat match goal with
 | |- context [if ?b then _ else _] => destruct b eqn:?; cbn; try congruence
 end.
Lemma clear_lift style s key : lift_state(Task.clear_lease style s key) =
 SystemsNative.clear_lease style(lift_state s)key.
Proof. unfold Task.clear_lease,SystemsNative.clear_lease; rewrite <- lease_lift;
 cbn [lift_lease]; split_tests; destruct s; unfold lift_state; cbn;
 rewrite replace_lift; reflexivity. Qed.
Opaque Task.clear_lease SystemsNative.clear_lease.
Lemma set_lift style s key v ttl : lift_state(Task.set_lease style s key v ttl) =
 SystemsNative.set_lease style(lift_state s)key v ttl.
Proof. unfold Task.set_lease,SystemsNative.set_lease; destruct(Nat.eqb style 1);
 try rewrite <- clear_lift; cbn [lift_state]; split_tests;
 unfold lift_state; cbn; rewrite replace_lift; reflexivity. Qed.
Opaque Task.set_lease SystemsNative.set_lease.
Lemma word_binding : Task.word = SystemsNative.word. Proof. reflexivity. Qed.
Lemma wheel_index_binding : Task.wheel_index = SystemsNative.wheel_index. Proof. reflexivity. Qed.
Opaque Task.word SystemsNative.word Task.wheel_index SystemsNative.wheel_index.
Lemma expire_command_lift style st key :
 lift_pair(task_expire_command style st key) = source_expire_command style(lift_pair st)key.
Proof. destruct st as [s out]; unfold task_expire_command,source_expire_command;
 rewrite <- word_binding, <- wheel_index_binding;
 cbn [lift_pair]; rewrite <- lease_lift; cbn [lift_lease];
 change (SystemsNative.clock(lift_state s)) with (Task.clock s);
 change (SystemsNative.wheel(lift_state s)) with (Task.wheel s);
 split_tests; repeat rewrite <- table_lift; try rewrite <- clear_lift; reflexivity. Qed.
Lemma expire_commands_lift style ids st :
 lift_pair(fold_left(task_expire_command style)ids st) =
 fold_left(source_expire_command style)ids(lift_pair st).
Proof. revert st; induction ids; intros; [reflexivity|].
 change (lift_pair(fold_left(task_expire_command style)ids(task_expire_command style st a)) =
 fold_left(source_expire_command style)ids(source_expire_command style(lift_pair st)a)).
 rewrite <- expire_command_lift; apply IHids. Qed.
Lemma expire_lift style s keys : lift_pair(Task.expire_at_tick style s keys) =
 SystemsNative.expire_at_tick style(lift_state s)keys.
Proof. change (lift_pair(fold_left(task_expire_command style)Task.nodes
 (Task.Table(S(Task.clock s))(Task.entries s)(Task.wheel s),keys)) =
 fold_left(source_expire_command style)Task.nodes
 (SystemsNative.Table(S(Task.clock s))(map lift_lease(Task.entries s))(Task.wheel s),keys)).
 rewrite expire_commands_lift; reflexivity. Qed.
Opaque Task.expire_at_tick SystemsNative.expire_at_tick.
Lemma advance_commands_lift style (ids:list nat) st :
 lift_pair(fold_left(fun state _=>let '(s,keys):=state in Task.expire_at_tick style s keys)ids st) =
 fold_left(fun state _=>let '(s,keys):=state in SystemsNative.expire_at_tick style s keys)ids(lift_pair st).
Proof. revert st; induction ids; intros [s keys]; cbn; [reflexivity|].
 rewrite <- expire_lift. apply IHids. Qed.
Lemma advance_lift style s ticks : lift_pair(Task.advance_clock style s ticks) =
 SystemsNative.advance_clock style(lift_state s)ticks.
Proof. unfold Task.advance_clock,SystemsNative.advance_clock; apply advance_commands_lift. Qed.
Opaque Task.advance_clock SystemsNative.advance_clock.
Lemma step_lift style s op a v ttl : lift_pair(Task.lease_step style s op a v ttl) =
 SystemsNative.lease_step style(lift_state s)op a v ttl.
Proof. unfold Task.lease_step,SystemsNative.lease_step; destruct(Z.eqb op 0).
 - rewrite <- set_lift; reflexivity.
 - destruct(Z.eqb op 3).
   + rewrite <- advance_lift. destruct(Task.advance_clock style s a)as[next keys]; reflexivity.
   + rewrite <- lease_lift; cbn [lift_lease]; destruct(Z.eqb op 2);
     try rewrite <- clear_lift; reflexivity.
Qed.
Opaque Task.lease_step SystemsNative.lease_step.
Lemma command_lift style st cmd : lift_pair(task_command style st cmd) =
 source_command style(lift_pair st)cmd.
Proof. destruct st as[s out]; destruct cmd as[[[op a]b]c];
 unfold task_command,source_command; cbn [lift_pair]; rewrite <- step_lift; cbn;
 destruct(Task.lease_step style s op a b c)as[next obs]; reflexivity. Qed.
Lemma commands_lift style cmds st : lift_pair(fold_left(task_command style)cmds st) =
 fold_left(source_command style)cmds(lift_pair st).
Proof. revert st; induction cmds; intros; [reflexivity|].
 change (lift_pair(fold_left(task_command style)cmds(task_command style st a)) =
 fold_left(source_command style)cmds(source_command style(lift_pair st)a)).
 rewrite <- command_lift; apply IHcmds. Qed.
Lemma flat_map_congr (f g:nat->list Z) ids (H:forall i,f i=g i) : flat_map f ids=flat_map g ids.
Proof. induction ids; cbn; [reflexivity|]. rewrite H,IHids; reflexivity. Qed.
Lemma view_lift s ids : flat_map(fun key=>let item:=Task.lease_at s key in [Task.live item;Task.value item])ids =
 flat_map(fun key=>let item:=SystemsNative.lease_at(lift_state s)key in [SystemsNative.live item;SystemsNative.value item])ids.
Proof. apply flat_map_congr; intro key; rewrite <- lease_lift; reflexivity. Qed.
Lemma observe_lift s out : task_observe s out = source_observe(lift_state s)out.
Proof. unfold task_observe,source_observe; rewrite <- view_lift; reflexivity. Qed.
'''


def prepare_leases_rocq(row):
    ctx = row['context']
    if ctx.get('tranche') != 'systems' or ctx.get('family_index') != 2:
        return None
    package = PACKAGES / row['pilot_id'] / 'rocq'
    if (package / 'registry.json').exists():
        meta = json.loads((package / 'registry.json').read_text())
        if tree_digest(package / 'task') != meta['public_sha256']:
            raise ValueError('Existing leases package changed')
        return meta
    if package.exists():
        raise ValueError('Incomplete preparation requires inspection: ' + str(package))
    started = time.monotonic()
    source = ROOT / 'benchmarks/tasks/systems-core/rocq'
    raw = (source / 'SystemsNative.v').read_text()
    native = declarations(raw)
    domains = declarations((source / 'SystemsDomain.v').read_text())
    goals = declarations((source / 'SystemsGoals.v').read_text())
    selected = [goals[ctx[k]] for k in ('equivalence_goal', 'refutation_at_goal')]
    styles = re.findall(r'SystemsNative.entry\s+2\s+(\d+)', selected[0])
    if styles not in (['0', '1'], ['0', '2']):
        raise ValueError('Unexpected frozen leases pair')
    records = [re.search(r'^Record '+name+r'\s*:.*?\.', raw, re.M | re.S).group() for name in ('lease', 'table')]
    names = list(native)
    helpers = names[names.index('no_lease'):names.index('leases')]
    pair = [re.sub(r'\bstyle\b', style, native['leases'].replace('Definition leases style input', 'Definition '+name+' input', 1))
            for name, style in zip(('a', 'b'), styles)]
    command_domain = domains['valid_command'].split('  | _ =>', 1)[1].split('\n  end.', 1)[0]
    valid_command = 'Definition valid_command op a b c := ' + command_domain + '.'
    valid_body = domains['valid_familyb'].split('  let q :=', 1)[1]
    q, valid_body = valid_body.split('  if Nat.eqb family 3 then', 1)
    valid_body = valid_body.split('\n  else\n', 1)[1].rstrip('.')
    valid_body = valid_body.replace('valid_command family', 'valid_command')
    valid = 'Definition valid input : Prop := (let q :=' + q + valid_body.replace('xs', 'input') + ')=true.'
    # The q prefix also refers to xs; substitute only its standalone binder.
    valid = re.sub(r'\bxs\b', 'input', valid)
    notation = 'Notation "\'let*\' x \':=\' c \'in\' b" := (obind c (fun x=>b)) (at level 200,x ident,c at level 100,b at level 200).'
    header = 'From Coq Require Import ZArith List Bool.\nImport ListNotations.\nOpen Scope nat_scope.\n'
    public = header + '\n'.join([native[n] for n in ('words', 'word', 'replace_at', 'finish', 'obind', 'commands', 'nodes', 'zeroes')] +
        [notation, *records] + [native[n] for n in helpers] + [domains['between'], valid_command, valid, *pair]) + '''
Definition equivalent : Prop := forall x, valid x -> exists o, a x=Some o /\ b x=Some o.
Definition refutationAt (x oa ob:words) : Prop := valid x /\ a x=Some oa /\ b x=Some ob /\ oa<>ob.
'''
    task = package / 'task'; binding = package / 'binding'
    task.mkdir(parents=True, mode=0o700); binding.mkdir(mode=0o700)
    (task / 'Task.v').write_text(public)
    (task / 'Obligation.v').write_text('From Trusted Require Import Task.\nDefinition goal : Prop := Task.equivalent.\n')
    original = ROOT / '_build/pilot-v1/systems-rocq-binding'
    original.mkdir(parents=True, exist_ok=True)
    paths = [(task, 'Trusted'), (binding, 'Binding'), (original, 'Frozen')]
    def compile_at(folder, name):
        return compile_rocq(folder, name, paths)
    logs = [compile_at(task, n) for n in ('Task', 'Obligation')]
    for name in ('SystemsNative', 'SystemsDomain'):
        src = source / (name + '.v'); dest = original / src.name
        if not dest.exists() or dest.read_bytes() != src.read_bytes() or not (original / (name + '.vo')).exists():
            dest.write_bytes(src.read_bytes()); logs.append(compile_at(original, name))
    (binding / 'FrozenTarget.v').write_text('From Frozen Require Import SystemsNative SystemsDomain.\n' + '\n'.join(selected) + '\n')
    logs.append(compile_at(binding, 'FrozenTarget'))
    command = native['leases'].split('fold_left (', 1)[1].split(' (commands input)', 1)[0].rstrip().rsplit(')', 1)[0]
    expire_command = native['expire_at_tick'].split('fold_left (', 1)[1].split(' nodes (tick,keys)', 1)[0].rstrip().rsplit(')', 1)[0]
    observe = native['leases'].split('  finish ', 1)[1].rstrip('.')
    tokens = set(native) | {'lease', 'Lease', 'table', 'Table', 'live', 'value', 'deadline', 'clock', 'entries', 'wheel'}
    def qualify(text, module):
        return re.sub(r'\b[A-Za-z_][A-Za-z_0-9]*\b', lambda m: module + '.' + m.group() if m.group() in tokens else m.group(), text)
    bridge = header + 'From Trusted Require Import Task.\nFrom Frozen Require Import SystemsNative SystemsDomain.\nFrom Binding Require Import FrozenTarget.\n'
    for module, prefix in (('Task', 'task'), ('SystemsNative', 'source')):
        bridge += 'Definition '+prefix+'_expire_command style := '+qualify(expire_command, module)+'.\n'
        bridge += 'Definition '+prefix+'_command style := '+qualify(command, module)+'.\n'
        bridge += 'Definition '+prefix+'_observe (s:'+module+'.table) (out:'+module+'.words) := '+module+'.finish '+qualify(observe, module)+'.\n'
    bridge += LEASE_BRIDGE
    for name, style in zip(('a', 'b'), styles):
        bridge += f'''Lemma {name}_binding input : Task.{name} input = SystemsNative.entry 2 {style} input.
Proof. change ((let '(s,out):=fold_left(task_command {style})(Task.commands input)
 (Task.Table 0(repeat Task.no_lease 8)(Task.zeroes 72),([]:Task.words))in task_observe s out) =
 (let '(s,out):=fold_left(source_command {style})(Task.commands input)
 (SystemsNative.Table 0(repeat SystemsNative.no_lease 8)(Task.zeroes 72),([]:Task.words))in source_observe s out)).
 change (SystemsNative.Table 0(repeat SystemsNative.no_lease 8)(Task.zeroes 72),([]:Task.words)) with
 (lift_pair(Task.Table 0(repeat Task.no_lease 8)(Task.zeroes 72),([]:Task.words))).
 rewrite <- commands_lift.
 destruct(fold_left(task_command {style})(Task.commands input)
 (Task.Table 0(repeat Task.no_lease 8)(Task.zeroes 72),([]:Task.words)))as[s out]; apply observe_lift.
Qed.
'''
    bridge += f'''Lemma domain_binding : Task.valid = SystemsDomain.valid 2. Proof. reflexivity. Qed.
Example equivalent_binding : Task.equivalent <-> FrozenTarget.{ctx['equivalence_goal']}.
Proof. unfold Task.equivalent,FrozenTarget.{ctx['equivalence_goal']},SystemsNative.Equivalent.
 split; intros H x V; destruct(H x V)as[o[A B]]; exists o; split.
 - rewrite <- a_binding; exact A.
 - rewrite <- b_binding; exact B.
 - rewrite a_binding; exact A.
 - rewrite b_binding; exact B.
Qed.
Example refutation_binding(x oa ob:Task.words) : Task.refutationAt x oa ob <-> FrozenTarget.{ctx['refutation_at_goal']} x oa ob.
Proof. unfold Task.refutationAt,FrozenTarget.{ctx['refutation_at_goal']},SystemsNative.RefutationAt.
 rewrite <- domain_binding, <- a_binding, <- b_binding; tauto. Qed.
Print Assumptions equivalent_binding.
Print Assumptions refutation_binding.
'''
    (binding / 'Binding.v').write_text(bridge)
    audit_log = compile_at(binding, 'Binding')
    logs.append(audit_log)
    (binding / 'compile.log').write_text('\n'.join(logs))
    if audit_log.count('Closed under the global context') != 2 or 'Axioms:' in audit_log:
        raise ValueError('Lease target correspondence is not closed')
    meta = {'pilot_id': row['pilot_id'], 'platform': 'rocq', 'public_sha256': tree_digest(task),
            'binding': 'rocq-kernel-checked-lease-table-transport-and-exact-frozen-target',
            'source_context': row['source_context_id'], 'source_goal': ctx['equivalence_goal'],
            'frozen_source_sha256': {n: hashlib.sha256((source / (n + '.v')).read_bytes()).hexdigest()
                                     for n in ('SystemsNative', 'SystemsDomain', 'SystemsGoals')},
            'preparation_wall_seconds': time.monotonic() - started,
            'preparation_controller_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'compiler_costs': 'compile-costs.jsonl', 'preparation_model_tokens': None,
            'final_proof_attempted': False}
    (package / 'registry.json').write_text(json.dumps(meta, indent=2) + '\n')
    return meta
