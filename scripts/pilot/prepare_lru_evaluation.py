"""Isolate frozen LRU caches and certify nested node/state representation maps."""
import hashlib
import json
import re
import resource
import time

from prepare_evaluation import ROOT, PACKAGES, compile_rocq
from prepare_classics_evaluation import declarations
from single_task_runner import tree_digest

LRU_BRIDGE = '''
Definition lift_node (n:Task.cache_node) : StatefulNative.cache_node :=
 {|StatefulNative.nk:=Task.nk n;StatefulNative.nv:=Task.nv n;StatefulNative.np:=Task.np n;
   StatefulNative.nn:=Task.nn n;StatefulNative.nl:=Task.nl n|}.
Definition lift_state (s:Task.cache_state) : StatefulNative.cache_state :=
 {|StatefulNative.cc:=Task.cc s;StatefulNative.co:=Task.co s;StatefulNative.cn:=map lift_node (Task.cn s);
   StatefulNative.ch:=Task.ch s;StatefulNative.ct:=Task.ct s|}.
Definition lift_pair (p:Task.cache_state*Task.words) := (lift_state (fst p),snd p).
Definition lift_items (p:Task.cache_state*list(Z*Z)) := (lift_state (fst p),snd p).
Definition lift_item (p:Task.cache_state*(Z*Z)) := (lift_state (fst p),snd p).
Definition lift_put (p:Task.cache_state*Z*list(Z*Z)) := let '(s,v,out):=p in (lift_state s,v,out).
Definition lift_query (p:Task.cache_state*Z*Z) := let '(s,status,v):=p in (lift_state s,status,v).
Ltac split_tests := repeat match goal with
 | |- context [if ?b then _ else _] => destruct b eqn:?; cbn; try congruence
 end.
Lemma nmake_lift k v p n l : lift_node(Task.nmake k v p n l) = StatefulNative.nmake k v p n l.
Proof. reflexivity. Qed.
Lemma cmake_lift cap order nodes head tail : lift_state(Task.cmake cap order nodes head tail) =
 StatefulNative.cmake cap order(map lift_node nodes)head tail.
Proof. reflexivity. Qed.
Lemma nth_lift ns i : lift_node (nth i ns Task.empty_node) = nth i (map lift_node ns) StatefulNative.empty_node.
Proof. revert i; induction ns; intros [|i]; cbn; try reflexivity; apply IHns. Qed.
Lemma put_lift ns i n : map lift_node (Task.put ns i n) = StatefulNative.put (map lift_node ns) i (lift_node n).
Proof. unfold Task.put, StatefulNative.put; repeat rewrite map_app;
 rewrite firstn_map, skipn_map; reflexivity. Qed.
Lemma initial_lift cap : lift_state (Task.cache_initial cap) = StatefulNative.cache_initial cap.
Proof. reflexivity. Qed.
Lemma node_lift s id : lift_node (Task.node_at s id) = StatefulNative.node_at (lift_state s) id.
Proof. unfold Task.node_at, StatefulNative.node_at; cbn [lift_state]; apply nth_lift. Qed.
Lemma set_node_lift s id n : lift_state (Task.set_node s id n) = StatefulNative.set_node (lift_state s) id (lift_node n).
Proof. destruct s; unfold Task.set_node, StatefulNative.set_node, lift_state, Task.cmake, StatefulNative.cmake; cbn;
 rewrite put_lift; reflexivity. Qed.
Opaque Task.set_node StatefulNative.set_node Task.node_at StatefulNative.node_at.
Lemma live_length ns : length (filter Task.nl ns) = length (filter StatefulNative.nl (map lift_node ns)).
Proof. induction ns; cbn; [reflexivity|]. destruct (Task.nl a); cbn; now rewrite IHns. Qed.
Lemma size_lift style s : Task.cache_size style s = StatefulNative.cache_size style (lift_state s).
Proof. unfold Task.cache_size, StatefulNative.cache_size; cbn [lift_state]; destruct (Nat.eqb style 0); [reflexivity|apply live_length]. Qed.
Lemma find_congr (p q:nat->bool) ids (H:forall i,p i=q i) : find p ids=find q ids.
Proof. induction ids; cbn; [reflexivity|]. rewrite H, IHids; reflexivity. Qed.
Lemma find_lift style order ns key ids :
 find (fun i=>if Nat.eqb style 0 then Z.eqb(fst(nth i order(0%Z,0%Z)))key else
   let n:=nth i ns Task.empty_node in Task.nl n&&Z.eqb(Task.nk n)key) ids =
 find (fun i=>if Nat.eqb style 0 then Z.eqb(fst(nth i order(0%Z,0%Z)))key else
   let n:=nth i (map lift_node ns) StatefulNative.empty_node in StatefulNative.nl n&&Z.eqb(StatefulNative.nk n)key) ids.
Proof. apply find_congr; intro i; rewrite <- nth_lift; destruct(Nat.eqb style 0); reflexivity. Qed.
Lemma lookup_lift style s key : Task.lookup_key style s key = StatefulNative.lookup_key style (lift_state s) key.
Proof. unfold Task.lookup_key, StatefulNative.lookup_key;
 cbv beta iota zeta delta [lift_state StatefulNative.cn StatefulNative.co]; rewrite <- find_lift; reflexivity. Qed.
Lemma item_lift style s id : Task.item_at style s id = StatefulNative.item_at style (lift_state s) id.
Proof. unfold Task.item_at, StatefulNative.item_at; rewrite <- node_lift; cbn [lift_state lift_node]; reflexivity. Qed.
Opaque Task.cache_size StatefulNative.cache_size Task.lookup_key StatefulNative.lookup_key Task.item_at StatefulNative.item_at.
Ltac transport := repeat first [rewrite <- cmake_lift | rewrite <- node_lift |
 rewrite <- nmake_lift | rewrite <- set_node_lift | progress cbn [lift_node]].
Lemma detach_lift s id : lift_state(Task.detach s id) = StatefulNative.detach (lift_state s) id.
Proof. unfold Task.detach, StatefulNative.detach; repeat rewrite <- node_lift; cbn [lift_node lift_state];
 split_tests; transport; reflexivity. Qed.
Opaque Task.detach StatefulNative.detach.
Lemma link_lift s id : lift_state(Task.link_front s id) = StatefulNative.link_front (lift_state s) id.
Proof. unfold Task.link_front, StatefulNative.link_front; repeat rewrite <- node_lift; cbn [lift_node lift_state];
 transport; split_tests; transport; reflexivity. Qed.
Opaque Task.link_front StatefulNative.link_front.
Lemma erase_lift style s id : lift_state(Task.erase_at style s id) = StatefulNative.erase_at style (lift_state s) id.
Proof. unfold Task.erase_at, StatefulNative.erase_at; destruct (Nat.eqb style 0); [reflexivity|].
 rewrite <- detach_lift, <- node_lift; cbn [lift_node]; rewrite <- nmake_lift; rewrite <- set_node_lift; reflexivity. Qed.
Lemma touch_lift style s id : lift_state(Task.touch style s id) = StatefulNative.touch style (lift_state s) id.
Proof. unfold Task.touch, StatefulNative.touch; destruct (Nat.eqb style 0); [rewrite <- item_lift; reflexivity|].
 rewrite <- detach_lift, <- link_lift; reflexivity. Qed.
Lemma value_lift style s id v : lift_state(Task.set_value style s id v) = StatefulNative.set_value style (lift_state s) id v.
Proof. unfold Task.set_value, StatefulNative.set_value; destruct (Nat.eqb style 0); [rewrite <- item_lift; reflexivity|].
 rewrite <- node_lift; cbn [lift_node]; rewrite <- nmake_lift; rewrite <- set_node_lift; reflexivity. Qed.
Lemma free_lift ns ids : find(fun i=>negb(Task.nl(nth i ns Task.empty_node)))ids =
 find(fun i=>negb(StatefulNative.nl(nth i(map lift_node ns)StatefulNative.empty_node)))ids.
Proof. apply find_congr; intro i; rewrite <- nth_lift; reflexivity. Qed.
Lemma insert_lift style s k v : lift_state(Task.insert_front style s k v) = StatefulNative.insert_front style (lift_state s) k v.
Proof. unfold Task.insert_front, StatefulNative.insert_front; destruct(Nat.eqb style 0); [reflexivity|].
 cbv beta iota zeta delta [lift_state StatefulNative.cn StatefulNative.co StatefulNative.ch StatefulNative.ct StatefulNative.cc];
 rewrite <- free_lift, <- (node_lift s); cbn [lift_node]; rewrite <- nmake_lift; rewrite <- (set_node_lift s), <- link_lift; reflexivity. Qed.
Lemma evict_lift style s : lift_item(Task.evict_tail style s) = StatefulNative.evict_tail style(lift_state s).
Proof. unfold Task.evict_tail, StatefulNative.evict_tail; cbn [lift_state]; rewrite <- erase_lift, <- item_lift; reflexivity. Qed.
Opaque Task.erase_at StatefulNative.erase_at Task.touch StatefulNative.touch Task.set_value StatefulNative.set_value
 Task.insert_front StatefulNative.insert_front Task.evict_tail StatefulNative.evict_tail.
Lemma put_cache_lift style s k v : lift_put(Task.cache_put style s k v) = StatefulNative.cache_put style(lift_state s)k v.
Proof. unfold Task.cache_put, StatefulNative.cache_put; rewrite <- lookup_lift, <- size_lift;
 change (StatefulNative.cc(lift_state s)) with (Task.cc s).
 destruct(Z.geb(Task.lookup_key style s k)0).
 - rewrite <- value_lift, <- touch_lift; reflexivity.
 - destruct(Nat.eqb(Task.cc s)0); [reflexivity|].
   destruct(Nat.eqb(Task.cache_size style s)(Task.cc s)).
   + rewrite <- evict_lift. destruct(Task.evict_tail style s) as [next item]; cbn [lift_item]; rewrite <- insert_lift; reflexivity.
   + rewrite <- insert_lift; reflexivity.
Qed.
Lemma query_lift style s k u : lift_query(Task.cache_query style s k u) = StatefulNative.cache_query style(lift_state s)k u.
Proof. unfold Task.cache_query, StatefulNative.cache_query; rewrite <- lookup_lift;
 split_tests; try rewrite <- touch_lift; try rewrite <- item_lift; reflexivity. Qed.
Opaque Task.cache_put StatefulNative.cache_put Task.cache_query StatefulNative.cache_query.
Lemma shrink_lift style fuel s out : option_map lift_items(Task.shrink_cache style fuel s out) =
 StatefulNative.shrink_cache style fuel (lift_state s)out.
Proof. revert s out; induction fuel; intros; cbn [Task.shrink_cache StatefulNative.shrink_cache];
 rewrite <- size_lift; change (StatefulNative.cc(lift_state s)) with (Task.cc s); destruct(Nat.leb(Task.cache_size style s)(Task.cc s)); try reflexivity.
 rewrite <- evict_lift; destruct(Task.evict_tail style s) as [next item]; cbn [lift_item]; apply IHfuel. Qed.
Opaque Task.shrink_cache StatefulNative.shrink_cache.
Lemma execute_lift style s op k v : option_map lift_pair(Task.execute_cache style s op k v) =
 StatefulNative.execute_cache style(lift_state s)op k v.
Proof. unfold Task.execute_cache, StatefulNative.execute_cache; destruct(Z.eqb op 0).
 - rewrite <- put_cache_lift. destruct(Task.cache_put style s k v) as [[next status]out]; reflexivity.
 - destruct(Z.eqb op 1||Z.eqb op 2).
   + rewrite <- query_lift. destruct(Task.cache_query style s k(Z.eqb op 1))as [[next status]value]; reflexivity.
   + destruct(Z.eqb op 3).
     * rewrite <- lookup_lift. destruct(Z.ltb(Task.lookup_key style s k)0);
       try rewrite <- erase_lift; try rewrite <- item_lift; reflexivity.
     * change (StatefulNative.cmake (Z.to_nat k)(StatefulNative.co(lift_state s))(StatefulNative.cn(lift_state s))(StatefulNative.ch(lift_state s))(StatefulNative.ct(lift_state s))) with
       (lift_state(Task.cmake(Z.to_nat k)(Task.co s)(Task.cn s)(Task.ch s)(Task.ct s))).
       rewrite <- shrink_lift. destruct(Task.shrink_cache style 8(Task.cmake(Z.to_nat k)(Task.co s)(Task.cn s)(Task.ch s)(Task.ct s))[])as [[next out]|]; reflexivity.
Qed.
Opaque Task.execute_cache StatefulNative.execute_cache.
Lemma view_lift fuel s id : Task.linked_view fuel s id = StatefulNative.linked_view fuel(lift_state s)id.
Proof. revert id; induction fuel; intros; cbn [Task.linked_view StatefulNative.linked_view];
 destruct(Z.ltb id 0); try reflexivity.
 rewrite <- node_lift; cbn [lift_node]; rewrite <- IHfuel; reflexivity. Qed.
Opaque Task.linked_view StatefulNative.linked_view.
Lemma command_lift style xs st i : option_map lift_pair(task_command style xs st i) =
 source_command style xs(option_map lift_pair st)i.
Proof. destruct st as [[s out]|]; [|reflexivity]. unfold task_command,source_command;
 cbn [Task.obind StatefulNative.obind option_map lift_pair]; change StatefulNative.iz with Task.iz;
 rewrite <- execute_lift; cbn. destruct(Task.execute_cache style s(Task.iz xs(2+3*i))(Task.iz xs(3+3*i))(Task.iz xs(4+3*i)))as [[next data]|] eqn:E; cbn in E; rewrite E; reflexivity. Qed.
Lemma commands_lift style xs is st : option_map lift_pair(fold_left(task_command style xs)is st) =
 fold_left(source_command style xs)is(option_map lift_pair st).
Proof. revert st; induction is; intros; cbn; [reflexivity|]. rewrite <- command_lift; apply IHis. Qed.
Lemma observe_lift style s out : task_observe style s out = source_observe style(lift_state s)out.
Proof. unfold task_observe,source_observe; cbn [lift_state]; rewrite <- view_lift, <- size_lift; reflexivity. Qed.
'''


def prepare_lru_rocq(row):
    ctx = row['context']
    if ctx.get('tranche') != 'stateful' or ctx.get('family_index') != 2:
        return None
    package = PACKAGES / row['pilot_id'] / 'rocq'
    if (package / 'registry.json').exists():
        meta = json.loads((package / 'registry.json').read_text())
        if tree_digest(package / 'task') != meta['public_sha256']:
            raise ValueError('Existing LRU package changed')
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
    styles = re.findall(r'StatefulNative.entry\s+2\s+(\d+)', selected[0])
    if styles not in (['0', '1'], ['0', '2']):
        raise ValueError('Unexpected frozen LRU pair')
    node_record = re.search(r'^Record cache_node:.*?\.', raw, re.M | re.S).group()
    state_record = re.search(r'^Record cache_state:.*?\.', raw, re.M | re.S).group()
    names = list(native)
    helpers = names[names.index('nmake'):names.index('lru')]
    pair = [re.sub(r'\bstyle\b', style, native['lru'].replace('Definition lru style xs', 'Definition ' + name + ' xs', 1))
            for name, style in zip(('a', 'b'), styles)]
    pre, match = domains['validb'].split(':=', 1)[1].split('match family with', 1)
    clauses = re.findall(r'\n \| (.*?)=>(.*?)(?=\n \| |\n end\.)', match, re.S)
    bodies = [body for pat, body in clauses if pat.strip() == '_']
    if len(bodies) != 1:
        raise ValueError('Missing frozen LRU domain')
    valid = 'Definition valid (xs:words) : Prop := (' + pre + bodies[0] + ')=true.'
    notation = 'Notation "\'let*\' x \':=\' c \'in\' b" := (obind c (fun x=>b)) (at level 200,x ident,c at level 100,b at level 200).'
    header = 'From Coq Require Import ZArith List Bool.\nImport ListNotations.\nOpen Scope nat_scope.\n'
    public = header + '\n'.join([native[n] for n in ('words', 'iz', 'put', 'finish', 'obind')] +
        [notation, node_record, native['nmake'], native['empty_node'], state_record] +
        [native[n] for n in helpers if n not in ('nmake', 'empty_node')] +
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
    command = native['lru'].split('fold_left(', 1)[1].split('\n (seq', 1)[0].rsplit(')', 1)[0]
    observe = native['lru'].split(" let '(s,out):=result in", 1)[1].rstrip('.')
    tokens = set(native) | {'cache_node', 'cache_state', 'nk', 'nv', 'np', 'nn', 'nl', 'cc', 'co', 'cn', 'ch', 'ct'}
    def qualify(text, module):
        return re.sub(r'\b[A-Za-z_][A-Za-z_0-9]*\b', lambda m: module + '.' + m.group() if m.group() in tokens else m.group(), text)
    bridge = header + 'From Trusted Require Import Task.\nFrom Frozen Require Import StatefulNative StatefulDomain.\nFrom Binding Require Import FrozenTarget.\n'
    bridge += 'Definition task_command style (xs:Task.words) := ' + qualify(command, 'Task') + '.\n'
    bridge += 'Definition source_command style (xs:StatefulNative.words) := ' + qualify(command, 'StatefulNative') + '.\n'
    bridge += 'Definition task_observe style (s:Task.cache_state) (out:Task.words) := ' + qualify(observe, 'Task') + '.\n'
    bridge += 'Definition source_observe style (s:StatefulNative.cache_state) (out:StatefulNative.words) := ' + qualify(observe, 'StatefulNative') + '.\n'
    bridge += LRU_BRIDGE
    for name, style in zip(('a', 'b'), styles):
        bridge += f'''Lemma {name}_binding xs : Task.{name} xs = StatefulNative.entry 2 {style} xs.
Proof. change ((Task.obind (fold_left (task_command {style} xs) (seq 0 (Z.to_nat (Task.iz xs 1)))
 (Some (Task.cache_initial (Z.to_nat (Task.iz xs 0)),([]:Task.words)))) (fun result=>let '(s,out):=result in task_observe {style} s out)) =
 (StatefulNative.obind (fold_left (source_command {style} xs) (seq 0 (Z.to_nat (Task.iz xs 1)))
 (Some (StatefulNative.cache_initial (Z.to_nat (Task.iz xs 0)),([]:Task.words)))) (fun result=>let '(s,out):=result in source_observe {style} s out))).
 rewrite <- initial_lift.
 change (Some (lift_state (Task.cache_initial (Z.to_nat (Task.iz xs 0))),([]:Task.words))) with
 (option_map lift_pair (Some (Task.cache_initial (Z.to_nat (Task.iz xs 0)),([]:Task.words)))).
 rewrite <- commands_lift.
 destruct (fold_left (task_command {style} xs) (seq 0 (Z.to_nat (Task.iz xs 1))) (Some(Task.cache_initial (Z.to_nat (Task.iz xs 0)),([]:Task.words)))) as [[s out]|];
 cbn [Task.obind StatefulNative.obind option_map lift_pair]; [apply observe_lift|reflexivity].
Qed.
'''
    bridge += f'''Lemma domain_binding : Task.valid = StatefulDomain.valid 2. Proof. reflexivity. Qed.
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
            'binding': 'rocq-kernel-checked-node-state-transport-and-exact-frozen-target',
            'source_context': row['source_context_id'], 'source_goal': ctx['equivalence_goal'],
            'frozen_source_sha256': {n: hashlib.sha256((source / (n + '.v')).read_bytes()).hexdigest()
                                     for n in ('StatefulNative', 'StatefulDomain', 'StatefulGoals')},
            'preparation_wall_seconds': time.monotonic() - started,
            'preparation_controller_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'compiler_costs': 'compile-costs.jsonl', 'preparation_model_tokens': None,
            'final_proof_attempted': False}
    (package / 'registry.json').write_text(json.dumps(meta, indent=2) + '\n')
    return meta

