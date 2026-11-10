"""Source-isolated expression evaluator with explicit result/cache transport."""
import hashlib
import json
import re
import resource
import time

from prepare_evaluation import ROOT, PACKAGES, compile_rocq, compile_lean
from prepare_classics_evaluation import declarations, lean_declarations
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


def prepare_evaluator_lean(row):
    ctx = row['context']
    if ctx.get('tranche') != 'boundaries' or ctx.get('family_index') != 3:
        return None
    package = PACKAGES / row['pilot_id'] / 'lean'
    if (package / 'registry.json').exists():
        meta = json.loads((package / 'registry.json').read_text())
        if tree_digest(package / 'task') != meta['public_sha256']:
            raise ValueError('Existing evaluator package changed')
        return meta
    if package.exists():
        raise ValueError('Incomplete preparation requires inspection: ' + str(package))
    started = time.monotonic()
    source = ROOT / 'benchmarks/tasks/boundaries-core/lean'
    raw = (source / 'BoundaryNative.lean').read_text()
    native = lean_declarations(raw)
    domains = lean_declarations((source / 'BoundaryDomain.lean').read_text())
    goals = lean_declarations((source / 'BoundaryGoals.lean').read_text())
    styles = re.findall(r'entry\s+3\s+(\d+)', goals[ctx['equivalence_goal']])
    if styles not in (['0', '1'], ['0', '2']):
        raise ValueError('Unexpected frozen evaluator pair')
    record = raw.split('structure Result where', 1)[1].split('def missing', 1)[0]
    prefix, tail = native['evaluator'].split('  let cache ←', 1)
    _, suffix = tail.split('  let result :=', 1)
    pair = []
    for name, style in zip(('a', 'b'), styles):
        expr = ('evalRec xs 64 (n-1) initial' if style == '0' else
                'some ((List.range n).foldl (fun cache i => put cache i ((leaf xs i).getD (combine ' +
                ('true' if style == '2' else 'false') + ' xs i cache))) initial)')
        pair.append(prefix.replace('def evaluator (style : Nat)', 'def ' + name, 1) +
                    '  let cache ← ' + expr + '\n  let result :=' + suffix)
    pre, branches = domains['validB'].split(':=', 1)[1].split('match domain with', 1)
    body = branches.split('  | 4 =>', 1)[1].split('  | 5 =>', 1)[0]
    valid = 'def valid (xs : Words) : Prop := (' + pre + body + ') = true\n'
    names = ('Words', 'getOr', 'iz', 'put', 'finish', 'Node')
    public = 'import Lean\nnamespace Task\n' + '\n'.join(
        [native[n] for n in names] + ['structure Result where' + record] +
        [native[n] for n in ('missing', 'ok', 'failure', 'expr', 'leaf', 'quotient', 'combine', 'evalRec')] +
        [domains['inRange'], valid, *pair]) + '''
def equivalent : Prop := ∀ x, valid x → ∃ o, a x=some o ∧ b x=some o
def refutationAt (x oa ob : Words) : Prop := valid x ∧ a x=some oa ∧ b x=some ob ∧ oa≠ob
end Task
'''
    public = re.sub(r'\bmutant\b', 'modeFlag', public)
    public = re.sub(r'\bpure\b', 'return', public)
    task = package / 'task'; binding = package / 'binding'
    task.mkdir(parents=True, mode=0o700); binding.mkdir(mode=0o700)
    (task / 'Task.lean').write_text(public)
    (task / 'Obligation.lean').write_text('import Task\nnamespace Obligation\ndef goal : Prop := Task.equivalent\nend Obligation\n')
    original = ROOT / '_build/pilot-v1/boundary-lean-binding'
    original.mkdir(parents=True, exist_ok=True)
    def compile_at(folder, name):
        return compile_lean(folder, name, [task, original])
    logs = [compile_at(task, n) for n in ('Task', 'Obligation')]
    for name in ('BoundaryNative', 'BoundaryDomain', 'BoundaryGoals'):
        src = source / (name + '.lean'); dest = original / src.name
        if not dest.exists() or dest.read_bytes() != src.read_bytes() or not (original / (name + '.olean')).exists():
            dest.write_bytes(src.read_bytes()); logs.append(compile_at(original, name))
    bridge = '''import Task
import BoundaryGoals
open SpecLessBenchBoundary
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000
def lift (r : Task.Result) : Result := ⟨r.code,r.error,r.value⟩
def cacheLift := List.map lift
set_option allowUnsafeReducibility true
attribute [local reducible] Task.expr expr Task.iz iz Task.getOr getOr lift
theorem map_if {α β : Type} (f : α → β) (p : Prop) [Decidable p] (a b : α) :
 f (if p then a else b) = if p then f a else f b := by split <;> rfl
theorem expr_binding : Task.expr = expr := rfl
theorem get_lift (cache : List Task.Result) (i : Nat) :
 lift (Task.getOr cache i Task.missing) = getOr (cacheLift cache) i missing := by
 induction cache generalizing i with
 | nil => rfl
 | cons r rs ih => cases i with
   | zero => rfl
   | succ i => exact ih i
theorem put_lift (cache : List Task.Result) (i : Nat) (r : Task.Result) :
 cacheLift (Task.put cache i r) = put (cacheLift cache) i (lift r) := by
 simp [Task.put, put, cacheLift, List.map_append, List.map_take, List.map_drop]
theorem leaf_lift (xs : Task.Words) (i : Nat) :
 Option.map lift (Task.leaf xs i) = leaf xs i := by
 simp only [Task.leaf, leaf, expr_binding]
 simp only [map_if (Option.map lift), map_if lift, Option.map_some, Option.map_none]
 rfl
theorem combine_lift (m : Bool) (xs : Task.Words) (i : Nat) (cache : List Task.Result) :
 lift (Task.combine m xs i cache) = combine m xs i (cacheLift cache) := by
 simp only [Task.combine, combine, expr_binding]
 simp only [← get_lift]
 simp only [map_if lift]
 rfl
theorem rec_lift (xs : Task.Words) (fuel i : Nat) (cache : List Task.Result) :
 Option.map cacheLift (Task.evalRec xs fuel i cache) = evalRec xs fuel i (cacheLift cache) := by
 induction fuel generalizing i cache with
 | zero =>
   simp only [Task.evalRec, evalRec, expr_binding]
   rw [← get_lift]
   simp only [lift]
   split <;> rfl
 | succ fuel ih =>
   simp only [Task.evalRec, evalRec, expr_binding]
   rw [← get_lift]
   simp only [lift]
   split
   · rfl
   · rw [← leaf_lift]
     cases Task.leaf xs i with
     | some r => simpa only [Option.map_some] using congrArg some (put_lift cache i r)
     | none =>
       simp only [Option.map_none]
       rw [← ih]
       cases Task.evalRec xs fuel (expr xs i).2.1.toNat cache with
       | none => rfl
       | some first =>
         simp only [Option.map_some, Option.bind_eq_bind, Option.bind_some]
         rw [← get_lift]
         simp only [lift]
         split
         · simpa only [Option.pure_def, Option.bind_eq_bind, Option.bind_some, Option.map_some, ← combine_lift] using
             congrArg some (put_lift first i (Task.combine false xs i first))
         · rw [← ih]
           cases Task.evalRec xs fuel (expr xs i).2.2.toNat first with
           | none => rfl
           | some second =>
             simpa only [Option.pure_def, Option.map_some, Option.bind_eq_bind, Option.bind_some, ← combine_lift] using
               congrArg some (put_lift second i (Task.combine false xs i second))
theorem fold_lift (m : Bool) (xs : Task.Words) (is : List Nat) (cache : List Task.Result) :
 cacheLift (is.foldl (fun c i => Task.put c i ((Task.leaf xs i).getD (Task.combine m xs i c))) cache) =
 is.foldl (fun c i => put c i ((leaf xs i).getD (combine m xs i c))) (cacheLift cache) := by
 induction is generalizing cache with
 | nil => rfl
 | cons i is ih =>
   simp only [List.foldl_cons]
   rw [← leaf_lift]
   cases Task.leaf xs i with
   | none => simpa only [Option.map_none, Option.getD_none, ← combine_lift, ← put_lift] using
       (ih (Task.put cache i (Task.combine m xs i cache)))
   | some r => simpa only [Option.map_some, Option.getD_some, ← put_lift] using
       (ih (Task.put cache i r))
theorem initial_lift (n : Nat) : cacheLift (List.replicate n Task.missing) = List.replicate n missing := by
 simp [cacheLift, List.map_replicate, lift, Task.missing, missing]
'''
    for name, style in zip(('a', 'b'), styles):
        mode = 'true' if style == '2' else 'false'
        expr = ('Task.evalRec xs 64 (n-1) initial' if style == '0' else
                'some ((List.range n).foldl (fun c i => Task.put c i ((Task.leaf xs i).getD (Task.combine ' + mode + ' xs i c))) initial)')
        bridge += f'''theorem {name}_binding : Task.{name} = entry 3 {style} := by
 funext xs
 let n := (Task.iz xs 0).toNat
 let initial := List.replicate n Task.missing
 dsimp only [Task.{name}, entry, evaluator]
 rw [← initial_lift]
 {'rw [← rec_lift]' if style == '0' else 'rw [← fold_lift]'}
 change (({expr}).bind (fun c => some (Task.finish
   [(Task.getOr c (n-1) Task.missing).code,(Task.getOr c (n-1) Task.missing).error,(Task.getOr c (n-1) Task.missing).value]))) =
   ((Option.map cacheLift ({expr})).bind (fun c => some (finish
   [(getOr c (n-1) missing).code,(getOr c (n-1) missing).error,(getOr c (n-1) missing).value])))
 cases {expr} with
 | none => rfl
 | some c => simp only [Option.bind_eq_bind, Option.bind_some, Option.map_some, ← get_lift]; rfl
'''
    bridge += f'''theorem domain_binding : Task.valid = valid 4 := by rfl
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
            'binding': 'lean-kernel-checked-result-cache-transport-and-exact-frozen-target',
            'source_context': row['source_context_id'], 'source_goal': ctx['equivalence_goal'],
            'frozen_source_sha256': {n: hashlib.sha256((source / (n + '.lean')).read_bytes()).hexdigest()
                                     for n in ('BoundaryNative', 'BoundaryDomain', 'BoundaryGoals')},
            'preparation_wall_seconds': time.monotonic() - started,
            'preparation_controller_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'compiler_costs': 'compile-costs.jsonl', 'preparation_model_tokens': None,
            'final_proof_attempted': False}
    (package / 'registry.json').write_text(json.dumps(meta, indent=2) + '\n')
    return meta
