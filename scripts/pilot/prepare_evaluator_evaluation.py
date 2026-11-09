"""Source-isolated expression evaluator with explicit result/cache transport."""
import hashlib
import json
import re
import resource
import time

from prepare_evaluation import ROOT, PACKAGES, compile_rocq
from prepare_classics_evaluation import declarations
from single_task_runner import tree_digest


def prepare_evaluator_rocq(row):
    ctx = row['context']
    if ctx.get('tranche') != 'boundaries' or ctx.get('family_index') != 3:
        return None
    package = PACKAGES / row['pilot_id'] / 'rocq'
    if (package / 'registry.json').exists():
        meta = json.loads((package / 'registry.json').read_text())
        if tree_digest(package / 'task') != meta['public_sha256']:
            raise ValueError('Existing evaluator package changed')
        return meta
    if package.exists():
        raise ValueError('Incomplete preparation requires inspection: ' + str(package))
    started = time.monotonic()
    source = ROOT / 'benchmarks/tasks/boundaries-core/rocq'
    raw = (source / 'BoundaryNative.v').read_text()
    native = declarations(raw)
    domains = declarations((source / 'BoundaryDomain.v').read_text())
    goals = declarations((source / 'BoundaryGoals.v').read_text())
    selected = [goals[ctx[k]] for k in ('equivalence_goal', 'refutation_at_goal')]
    styles = re.findall(r'BoundaryNative.entry\s+3\s+(\d+)', selected[0])
    if styles not in (['0', '1'], ['0', '2']):
        raise ValueError('Unexpected frozen evaluator pair')
    record = re.search(r'^Record result:.*?\.', raw, re.M | re.S).group()
    names = list(native)
    names = ['words', 'node', 'iz', 'put', 'finish', 'obind'] + names[names.index('missing'):names.index('evaluator')]
    pair = []
    prefix, tail = native['evaluator'].split('let* cache:=', 1)
    _, suffix = tail.split('in\n  let value:=', 1)
    for name, style in zip(('a', 'b'), styles):
        computation = ('eval_rec xs 64(n-1)initial' if style == '0' else
                       'Some(fold_left(fun cache i=>put cache i(match leaf xs i with Some v=>v|None=>combine ' +
                       ('true' if style == '2' else 'false') + ' xs i cache end))(seq 0 n)initial)')
        pair.append(prefix.replace('Definition evaluator style xs', 'Definition ' + name + ' xs', 1) +
                    'let* cache:=' + computation + ' in\n  let value:=' + suffix)
    pre, match = domains['validb'].split(':=', 1)[1].split('match domain with', 1)
    clauses = re.findall(r'\n  \| (.*?)=>(.*?)(?=\n  \| |\n  end\.)', match, re.S)
    bodies = [body for pat, body in clauses if pat.count('S') == 4 and pat.strip() != '_']
    if len(bodies) != 1:
        raise ValueError('Missing frozen evaluator domain')
    valid = 'Definition valid (xs:words) : Prop := (' + pre + bodies[0] + ')=true.'
    notation = 'Notation "\'let*\' x \':=\' c \'in\' b" := (obind c (fun x=>b)) (at level 200,x ident,c at level 100,b at level 200).'
    header = 'From Coq Require Import ZArith List Bool.\nImport ListNotations.\nOpen Scope nat_scope.\n'
    public = header + '\n'.join([native[n] for n in names[:6]] + [notation, record] + [native[n] for n in names[6:]] +
                               [domains['get'], domains['in_range'], valid, *pair]) + '''
Definition equivalent : Prop := forall x, valid x -> exists o, a x=Some o /\ b x=Some o.
Definition refutationAt (x oa ob:words) : Prop := valid x /\ a x=Some oa /\ b x=Some ob /\ oa<>ob.
'''
    public = re.sub(r'\bmutant\b', 'mode', public)
    task = package / 'task'; binding = package / 'binding'
    task.mkdir(parents=True, mode=0o700); binding.mkdir(mode=0o700)
    (task / 'Task.v').write_text(public)
    (task / 'Obligation.v').write_text('From Trusted Require Import Task.\nDefinition goal : Prop := Task.equivalent.\n')
    original = ROOT / '_build/pilot-v1/boundary-rocq-binding'
    original.mkdir(parents=True, exist_ok=True)
    paths = [(task, 'Trusted'), (binding, 'Binding'), (original, 'Frozen')]
    def compile_at(folder, name):
        return compile_rocq(folder, name, paths)
    logs = [compile_at(task, n) for n in ('Task', 'Obligation')]
    for name in ('BoundaryNative', 'BoundaryDomain'):
        src = source / (name + '.v'); dest = original / src.name
        if not dest.exists() or dest.read_bytes() != src.read_bytes() or not (original / (name + '.vo')).exists():
            dest.write_bytes(src.read_bytes()); logs.append(compile_at(original, name))
    (binding / 'FrozenTarget.v').write_text('From Frozen Require Import BoundaryNative BoundaryDomain.\n' + '\n'.join(selected) + '\n')
    logs.append(compile_at(binding, 'FrozenTarget'))
    bridge = header + '''From Trusted Require Import Task.
From Frozen Require Import BoundaryNative BoundaryDomain.
From Binding Require Import FrozenTarget.
Definition lift (r:Task.result) : BoundaryNative.result :=
 {| BoundaryNative.rc:=Task.rc r; BoundaryNative.re:=Task.re r; BoundaryNative.rv:=Task.rv r |}.
Definition cache_lift := map lift.
Ltac split_tests := repeat match goal with
 | |- context [if ?b then _ else _] => destruct b eqn:?; cbn; try congruence
 end.
Lemma nth_lift cache i : lift (nth i cache Task.missing) = nth i (cache_lift cache) BoundaryNative.missing.
Proof. revert i; induction cache; intros [|i]; cbn; try reflexivity; apply IHcache. Qed.
Lemma firstn_lift n xs : map lift (firstn n xs) = firstn n (map lift xs).
Proof. revert xs; induction n; intros [|x xs]; cbn; try reflexivity; now rewrite IHn. Qed.
Lemma skipn_lift n xs : map lift (skipn n xs) = skipn n (map lift xs).
Proof. revert xs; induction n; intros [|x xs]; cbn; try reflexivity; apply IHn. Qed.
Lemma put_lift cache i r : cache_lift (Task.put cache i r) = BoundaryNative.put (cache_lift cache) i (lift r).
Proof. unfold Task.put, BoundaryNative.put, cache_lift; repeat rewrite map_app;
 rewrite firstn_lift, skipn_lift; reflexivity. Qed.
Lemma leaf_lift xs i : option_map lift (Task.leaf xs i) = BoundaryNative.leaf xs i.
Proof. unfold Task.leaf, BoundaryNative.leaf, Task.expr, BoundaryNative.expr;
 change BoundaryNative.iz with Task.iz; cbn; split_tests; reflexivity. Qed.
Lemma combine_lift m xs i cache : lift (Task.combine m xs i cache) = BoundaryNative.combine m xs i (cache_lift cache).
Proof. unfold Task.combine, BoundaryNative.combine; cbn [Task.expr BoundaryNative.expr];
 change BoundaryNative.iz with Task.iz;
 repeat rewrite <- nth_lift; cbn [lift];
 cbv beta iota zeta delta [Nat.add Nat.mul]; split_tests; reflexivity. Qed.
Opaque Task.combine BoundaryNative.combine Task.leaf BoundaryNative.leaf.
Lemma rec_lift xs fuel i cache : option_map cache_lift (Task.eval_rec xs fuel i cache) =
 BoundaryNative.eval_rec xs fuel i (cache_lift cache).
Proof. revert i cache; induction fuel; intros;
 cbn [Task.eval_rec BoundaryNative.eval_rec]; rewrite <- nth_lift; cbn [lift];
 destruct (Z.geb (Task.rc (nth i cache Task.missing)) 0) eqn:C;
 cbn in C; cbn; try rewrite C; cbn; try reflexivity.
 rewrite <- leaf_lift. destruct (Task.leaf xs i) as [r|] eqn:L; cbn.
 - rewrite put_lift. reflexivity.
 - change BoundaryNative.iz with Task.iz.
   rewrite <- IHfuel.
   match goal with |- context [Task.eval_rec ?xs ?f ?j ?c] => destruct (Task.eval_rec xs f j c) as [first|] eqn:F end;
   cbn in F; cbn; try rewrite F; cbn; try reflexivity.
   repeat rewrite <- nth_lift; cbn [lift]; split_tests;
   try rewrite put_lift; try rewrite combine_lift; try reflexivity.
   rewrite <- IHfuel.
   match goal with |- context [Task.eval_rec ?xs ?f ?j ?c] => destruct (Task.eval_rec xs f j c) as [second|] eqn:S end;
   cbn in S; cbn; try rewrite S; cbn;
   try rewrite put_lift; try rewrite combine_lift; reflexivity.
Qed.
Opaque Task.eval_rec BoundaryNative.eval_rec.
Lemma repeat_lift n : cache_lift (repeat Task.missing n) = repeat BoundaryNative.missing n.
Proof. induction n; [reflexivity|].
 change ((lift Task.missing :: cache_lift (repeat Task.missing n)) =
 (BoundaryNative.missing :: repeat BoundaryNative.missing n)).
 now rewrite IHn. Qed.
Lemma fold_lift m xs is cache : cache_lift (fold_left
 (fun cache i=>Task.put cache i(match Task.leaf xs i with Some v=>v|None=>Task.combine m xs i cache end)) is cache) =
 fold_left (fun cache i=>BoundaryNative.put cache i(match BoundaryNative.leaf xs i with Some v=>v|None=>BoundaryNative.combine m xs i cache end)) is (cache_lift cache).
Proof. revert cache; induction is; intros; cbn; [reflexivity|].
 rewrite <- leaf_lift. destruct (Task.leaf xs a); cbn;
 try rewrite <- combine_lift; rewrite <- put_lift; apply IHis. Qed.
Definition task_observe cache n := Some(Task.finish
 [Task.rc(nth n cache Task.missing);Task.re(nth n cache Task.missing);Task.rv(nth n cache Task.missing)]).
Definition source_observe cache n := Some(BoundaryNative.finish
 [BoundaryNative.rc(nth n cache BoundaryNative.missing);BoundaryNative.re(nth n cache BoundaryNative.missing);BoundaryNative.rv(nth n cache BoundaryNative.missing)]).
Lemma observe_lift cache n : task_observe cache n = source_observe (cache_lift cache) n.
Proof. unfold task_observe, source_observe; rewrite <- nth_lift; reflexivity. Qed.
'''
    for name, style in zip(('a', 'b'), styles):
        mode = 'true' if style == '2' else 'false'
        computation = ('Task.eval_rec xs 64 (Z.to_nat(Task.iz xs 0)-1) initial' if style == '0' else
                       'Some(fold_left(fun cache i=>Task.put cache i(match Task.leaf xs i with Some v=>v|None=>Task.combine ' + mode + ' xs i cache end))(seq 0(Z.to_nat(Task.iz xs 0)))initial)')
        bridge += f'''Lemma {name}_binding xs : Task.{name} xs = BoundaryNative.entry 3 {style} xs.
Proof. unfold Task.{name}, BoundaryNative.entry, BoundaryNative.evaluator.
 change BoundaryNative.iz with Task.iz.
 rewrite <- repeat_lift.
 {'rewrite <- rec_lift.' if style == '0' else 'rewrite <- fold_lift.'}
 set (initial := repeat Task.missing (Z.to_nat(Task.iz xs 0))).
 change ((Task.obind ({computation}) (fun cache=>task_observe cache (Z.to_nat(Task.iz xs 0)-1))) =
 (BoundaryNative.obind (option_map cache_lift ({computation})) (fun cache=>source_observe cache (Z.to_nat(Task.iz xs 0)-1)))).
 destruct ({computation}) as [cache|]; cbn [Task.obind BoundaryNative.obind option_map]; [apply observe_lift|reflexivity].
Qed.
'''
    bridge += f'''Lemma domain_binding : Task.valid = BoundaryDomain.valid 4. Proof. reflexivity. Qed.
Example equivalent_binding : Task.equivalent <-> FrozenTarget.{ctx['equivalence_goal']}.
Proof. unfold Task.equivalent, FrozenTarget.{ctx['equivalence_goal']}, BoundaryNative.Equivalent.
 split; intros H x V; destruct (H x V) as [o [A B]]; exists o; split.
 - rewrite <- a_binding. exact A.
 - rewrite <- b_binding. exact B.
 - rewrite a_binding. exact A.
 - rewrite b_binding. exact B.
Qed.
Example refutation_binding (x oa ob:Task.words) : Task.refutationAt x oa ob <-> FrozenTarget.{ctx['refutation_at_goal']} x oa ob.
Proof. unfold Task.refutationAt, FrozenTarget.{ctx['refutation_at_goal']}, BoundaryNative.RefutationAt.
 rewrite <- domain_binding, <- a_binding, <- b_binding. tauto. Qed.
Print Assumptions equivalent_binding.
Print Assumptions refutation_binding.
'''
    (binding / 'Binding.v').write_text(bridge)
    logs.append(compile_at(binding, 'Binding'))
    (binding / 'compile.log').write_text('\n'.join(logs))
    meta = {'pilot_id': row['pilot_id'], 'platform': 'rocq', 'public_sha256': tree_digest(task),
            'binding': 'rocq-kernel-checked-result-cache-transport-and-exact-frozen-target',
            'source_context': row['source_context_id'], 'source_goal': ctx['equivalence_goal'],
            'frozen_source_sha256': {n: hashlib.sha256((source / (n + '.v')).read_bytes()).hexdigest()
                                     for n in ('BoundaryNative', 'BoundaryDomain', 'BoundaryGoals')},
            'preparation_wall_seconds': time.monotonic() - started,
            'preparation_controller_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'compiler_costs': 'compile-costs.jsonl', 'preparation_model_tokens': None,
            'final_proof_attempted': False}
    (package / 'registry.json').write_text(json.dumps(meta, indent=2) + '\n')
    return meta
