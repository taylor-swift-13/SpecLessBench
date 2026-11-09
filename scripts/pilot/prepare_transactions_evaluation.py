"""Source-isolated transaction store with constructive record transport."""
import hashlib
import json
import re
import resource
import time

from prepare_evaluation import ROOT, PACKAGES, compile_rocq, compile_lean
from prepare_classics_evaluation import declarations, lean_declarations
from single_task_runner import tree_digest


def prepare_transactions_rocq(row):
    ctx = row['context']
    if ctx.get('tranche') != 'stateful' or ctx.get('family_index') != 1:
        return None
    package = PACKAGES / row['pilot_id'] / 'rocq'
    if (package / 'registry.json').exists():
        meta = json.loads((package / 'registry.json').read_text())
        if tree_digest(package / 'task') != meta['public_sha256']:
            raise ValueError('Existing transaction package changed')
        return meta
    if package.exists():
        raise ValueError('Incomplete preparation requires inspection: ' + str(package))
    started = time.monotonic()
    source = ROOT / 'benchmarks/tasks/stateful-core/rocq'
    raw = (source / 'StatefulNative.v').read_text()
    native = declarations(raw)
    domain = declarations((source / 'StatefulDomain.v').read_text())
    goals = declarations((source / 'StatefulGoals.v').read_text())
    selected = [goals[ctx[k]] for k in ('equivalence_goal', 'refutation_at_goal')]
    styles = re.findall(r'StatefulNative.entry\s+1\s+(\d+)', selected[0])
    if styles not in (['0', '1'], ['0', '2']):
        raise ValueError('Unexpected frozen transaction pair')
    record = re.search(r'^Record tx_state:.*?\.', raw, re.M | re.S).group()
    names = list(native)
    names = ['words', 'iz', 'put', 'finish'] + names[names.index('tmake'):names.index('transactions')]
    pair = [re.sub(r'\bstyle\b', style, native['transactions'].replace('Definition transactions style xs', 'Definition ' + name + ' xs', 1))
            for name, style in zip(('a', 'b'), styles)]
    pre, match = domain['validb'].split(':=', 1)[1].split('match family with', 1)
    clauses = re.findall(r'\n \| (.*?)=>(.*?)(?=\n \| |\n end\.)', match, re.S)
    bodies = [body for pat, body in clauses if pat.strip() == 'S O']
    if len(bodies) != 1:
        raise ValueError('Missing frozen transaction domain')
    valid = 'Definition valid (xs:words) : Prop := (' + pre + bodies[0] + ')=true.'
    header = 'From Coq Require Import ZArith List Bool.\nImport ListNotations.\nOpen Scope nat_scope.\n'
    public = header + '\n'.join([native[n] for n in names[:4]] + [record] + [native[n] for n in names[4:]] +
                               [domain['get'], domain['in_range'], valid, *pair]) + '''
Definition equivalent : Prop := forall x, valid x -> exists o, a x=Some o /\ b x=Some o.
Definition refutationAt (x oa ob:words) : Prop := valid x /\ a x=Some oa /\ b x=Some ob /\ oa<>ob.
'''
    task = package / 'task'
    binding = package / 'binding'
    task.mkdir(parents=True, mode=0o700)
    binding.mkdir(mode=0o700)
    (task / 'Task.v').write_text(public)
    (task / 'Obligation.v').write_text('From Trusted Require Import Task.\nDefinition goal : Prop := Task.equivalent.\n')
    original = ROOT / '_build/pilot-v1/stateful-rocq-binding'
    original.mkdir(parents=True, exist_ok=True)
    paths = [(task, 'Trusted'), (binding, 'Binding'), (original, 'Frozen')]
    def compile_at(folder, name):
        return compile_rocq(folder, name, paths)
    logs = [compile_at(task, n) for n in ('Task', 'Obligation')]
    for name in ('StatefulNative', 'StatefulDomain'):
        src = source / (name + '.v')
        dest = original / src.name
        if not dest.exists() or dest.read_bytes() != src.read_bytes() or not (original / (name + '.vo')).exists():
            dest.write_bytes(src.read_bytes())
            logs.append(compile_at(original, name))
    (binding / 'FrozenTarget.v').write_text('From Frozen Require Import StatefulNative StatefulDomain.\n' + '\n'.join(selected) + '\n')
    logs.append(compile_at(binding, 'FrozenTarget'))
    bridge = header + '''From Trusted Require Import Task.
From Frozen Require Import StatefulNative StatefulDomain.
From Binding Require Import FrozenTarget.
Definition lift (s:Task.tx_state) : StatefulNative.tx_state :=
 {| StatefulNative.ts:=Task.ts s; StatefulNative.tt:=Task.tt s;
    StatefulNative.tu:=Task.tu s; StatefulNative.tm:=Task.tm s |}.
Definition lift_pair (p:Task.tx_state*Task.words) := (lift (fst p),snd p).
Ltac split_tests := repeat match goal with
 | |- context [if ?b then _ else _] => destruct b eqn:?; cbn in *; try congruence
 end.
Lemma restore_lift s u : lift (Task.restore_undo s u) = StatefulNative.restore_undo (lift s) u.
Proof. destruct s; destruct u as [[k f] v]; reflexivity. Qed.
Lemma restore_fold_lift us s : lift (fold_left Task.restore_undo us s) =
 fold_left StatefulNative.restore_undo us (lift s).
Proof. revert s; induction us; intros; cbn; [reflexivity|].
 rewrite <- restore_lift. apply IHus. Qed.
Lemma undo_lift s mark : lift (Task.undo_to s mark) = StatefulNative.undo_to (lift s) mark.
Proof. destruct s; unfold Task.undo_to, StatefulNative.undo_to; cbn [lift];
 rewrite <- restore_fold_lift. reflexivity. Qed.
Opaque Task.undo_to StatefulNative.undo_to.
Lemma depth_lift style s : Task.tx_depth style s = StatefulNative.tx_depth style (lift s).
Proof. destruct s; reflexivity. Qed.
Lemma execute_lift style s op key value :
 lift_pair (Task.execute_tx style s op key value) = StatefulNative.execute_tx style (lift s) op key value.
Proof. destruct s; unfold Task.words, StatefulNative.words in *;
 pose proof (undo_lift {|Task.ts:=ts;Task.tt:=tt;Task.tu:=tu;Task.tm:=tm|} (nth 0 tm 0)) as undo_eq;
 cbv beta iota zeta delta [lift Task.ts Task.tt Task.tu Task.tm] in undo_eq;
 unfold Task.execute_tx, StatefulNative.execute_tx;
 cbv beta iota zeta delta [Task.tx_write StatefulNative.tx_write
 Task.append_undo StatefulNative.append_undo Task.tx_depth StatefulNative.tx_depth
 Task.read_slot StatefulNative.read_slot Task.write_slot StatefulNative.write_slot
 Task.tx_begin StatefulNative.tx_begin Task.tx_commit StatefulNative.tx_commit
 Task.tx_rollback StatefulNative.tx_rollback Task.tmake StatefulNative.tmake
 lift_pair lift Task.ts Task.tt Task.tu Task.tm
 StatefulNative.ts StatefulNative.tt StatefulNative.tu StatefulNative.tm];
 split_tests; repeat rewrite <- undo_eq; cbn in *;
 unfold Task.words, StatefulNative.words in *;
 try congruence; reflexivity. Qed.
Opaque Task.execute_tx StatefulNative.execute_tx.
Lemma initial_lift : lift Task.tx_initial = StatefulNative.tx_initial. Proof. reflexivity. Qed.
Lemma commands_lift style xs is p :
 lift_pair (fold_left (fun state i=>let '(s,out):=state in
 let '(next,data):=Task.execute_tx style s (Task.iz xs(1+3*i)) (Task.iz xs(2+3*i)) (Task.iz xs(3+3*i)) in (next,out++data)) is p) =
 fold_left (fun state i=>let '(s,out):=state in
 let '(next,data):=StatefulNative.execute_tx style s (StatefulNative.iz xs(1+3*i)) (StatefulNative.iz xs(2+3*i)) (StatefulNative.iz xs(3+3*i)) in (next,out++data)) is (lift_pair p).
Proof. revert p; induction is as [|i is IH]; intros [s out]; cbn; [reflexivity|].
 rewrite <- execute_lift. destruct (Task.execute_tx style s (Task.iz xs(1+3*i)) (Task.iz xs(2+3*i)) (Task.iz xs(3+3*i))) as [next data] eqn:command_eq.
 cbv beta iota zeta delta [Task.iz StatefulNative.iz] in command_eq |- *.
 cbn in command_eq.
 try rewrite command_eq. cbn [lift_pair]. apply IH. Qed.
'''
    for name, style in zip(('a', 'b'), styles):
        bridge += f'''Lemma {name}_binding xs : Task.{name} xs = StatefulNative.entry 1 {style} xs.
Proof. unfold Task.{name}, StatefulNative.entry, StatefulNative.transactions.
 pose proof (commands_lift {style} xs (seq 0 (Z.to_nat (Task.iz xs 0))) (Task.tx_initial,([]:Task.words))) as commands_eq.
 cbv beta iota zeta delta [lift_pair Task.iz StatefulNative.iz Task.words StatefulNative.words] in commands_eq |- *.
 cbn in commands_eq. try rewrite initial_lift in commands_eq. cbn.
 rewrite <- commands_eq.
 match goal with |- context [fold_left ?f ?is ?p] => destruct (fold_left f is p) as [s out] end.
 cbn [lift_pair]. try rewrite <- depth_lift. reflexivity. Qed.
'''
    bridge += f'''Lemma domain_binding : Task.valid = StatefulDomain.valid 1. Proof. reflexivity. Qed.
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


def prepare_transactions_lean(row):
    ctx = row['context']
    if ctx.get('tranche') != 'stateful' or ctx.get('family_index') != 1:
        return None
    package = PACKAGES / row['pilot_id'] / 'lean'
    if (package / 'registry.json').exists():
        meta = json.loads((package / 'registry.json').read_text())
        if tree_digest(package / 'task') != meta['public_sha256']:
            raise ValueError('Existing transaction package changed')
        return meta
    if package.exists():
        raise ValueError('Incomplete preparation requires inspection: ' + str(package))
    started = time.monotonic()
    source = ROOT / 'benchmarks/tasks/stateful-core/lean'
    raw = (source / 'StatefulNative.lean').read_text()
    native = lean_declarations(raw)
    domains = lean_declarations((source / 'StatefulDomain.lean').read_text())
    goals = lean_declarations((source / 'StatefulGoals.lean').read_text())
    styles = re.findall(r'entry\s+1\s+(\d+)', goals[ctx['equivalence_goal']])
    if styles not in (['0', '1'], ['0', '2']):
        raise ValueError('Unexpected frozen transaction pair')
    record = raw.split('structure TxState where', 1)[1].split('def txDepth', 1)[0]
    names = list(native)
    names = ['Words', 'Item', 'getOr', 'iz', 'put', 'finish'] + names[names.index('txDepth'):names.index('transactions')]
    pair = [re.sub(r'\bstyle\b', style, native['transactions'].replace('def transactions (style : Nat)', 'def ' + name, 1))
            for name, style in zip(('a', 'b'), styles)]
    pre, branches = domains['validB'].split(':=', 1)[1].split('match family with', 1)
    body = branches.split('  | 1 =>', 1)[1].split('  | _ =>', 1)[0]
    valid = 'def valid (xs : Words) : Prop := (' + pre + body + ') = true\n'
    task = package / 'task'; binding = package / 'binding'
    task.mkdir(parents=True, mode=0o700); binding.mkdir(mode=0o700)
    public = 'import Lean\nnamespace Task\n' + '\n'.join(
        [native[n] for n in names[:6]] + ['structure TxState where' + record] + [native[n] for n in names[6:]] +
        [domains['inRange'], valid, *pair]) + '''
def equivalent : Prop := ∀ x, valid x → ∃ o, a x=some o ∧ b x=some o
def refutationAt (x oa ob : Words) : Prop := valid x ∧ a x=some oa ∧ b x=some ob ∧ oa≠ob
end Task
'''
    (task / 'Task.lean').write_text(public)
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
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000
open SpecLessBenchStateful
def lift (s : Task.TxState) : TxState := ⟨s.slots,s.snaps,s.undo,s.marks⟩
def liftPair (p : Task.TxState × Task.Words) : TxState × Words := (lift p.1,p.2)
theorem restore_lift (s : Task.TxState) (u : Int × Int × Int) :
  lift (Task.restoreUndo s u) = restoreUndo (lift s) u := by rfl
theorem restore_fold_lift (us : List (Int × Int × Int)) (s : Task.TxState) :
  lift (us.foldl Task.restoreUndo s) = us.foldl restoreUndo (lift s) := by
  induction us generalizing s with
  | nil => rfl
  | cons u us ih => simpa only [List.foldl_cons, restore_lift] using ih (Task.restoreUndo s u)
theorem undo_lift (s : Task.TxState) (mark : Nat) :
  lift (Task.undoTo s mark) = undoTo (lift s) mark := by
  unfold Task.undoTo undoTo
  have h := restore_fold_lift (s.undo.drop mark).reverse s
  cases s
  simp only [lift] at h ⊢
  rw [← h]
def liftInt (p : Task.TxState × Int) : TxState × Int := (lift p.1,p.2)
theorem liftInt_pair (s : Task.TxState) (i : Int) : liftInt (s,i) = (lift s,i) := by rfl
theorem depth_lift (style : Nat) (s : Task.TxState) : Task.txDepth style s = txDepth style (lift s) := by rfl
theorem write_lift (style : Nat) (s : Task.TxState) (key : Nat) (f v : Int) :
  lift (Task.txWrite style s key f v) = txWrite style (lift s) key f v := by
  unfold Task.txWrite txWrite Task.appendUndo appendUndo
  simp only [← depth_lift]
  split <;> rfl
theorem begin_lift (style : Nat) (s : Task.TxState) : liftInt (Task.txBegin style s) = txBegin style (lift s) := by
  unfold Task.txBegin txBegin
  simp only [← depth_lift]
  split
  · rfl
  · split <;> rfl
theorem commit_lift (style : Nat) (s : Task.TxState) : liftInt (Task.txCommit style s) = txCommit style (lift s) := by
  unfold Task.txCommit txCommit
  simp only [← depth_lift]
  split
  · rfl
  · split <;> rfl
theorem rollback_lift (style : Nat) (s : Task.TxState) : liftInt (Task.txRollback style s) = txRollback style (lift s) := by
  unfold Task.txRollback txRollback
  simp only [← depth_lift]
  split
  · rfl
  · split
    · rfl
    · have h := undo_lift s (Task.getOr s.marks 0 0)
      dsimp only [Task.getOr, getOr, lift] at h ⊢
      rw [← h]
      rfl
theorem execute_lift (style : Nat) (s : Task.TxState) (op key value : Int) :
  liftPair (Task.executeTx style s op key value) = executeTx style (lift s) op key value := by
  unfold Task.executeTx executeTx
  have h : liftInt (if op == 0 then (Task.txWrite style s key.toNat 1 value,0)
    else if op == 1 then (Task.txWrite style s key.toNat 0 0,0)
    else if op == 3 then Task.txBegin style s else if op == 4 then Task.txCommit style s
    else if op == 5 then Task.txRollback style s else (s,0)) =
    (if op == 0 then (txWrite style (lift s) key.toNat 1 value,0)
    else if op == 1 then (txWrite style (lift s) key.toNat 0 0,0)
    else if op == 3 then txBegin style (lift s) else if op == 4 then txCommit style (lift s)
    else if op == 5 then txRollback style (lift s) else (lift s,0)) := by
      by_cases h0 : (op == 0) = true
      · simp only [if_pos h0, liftInt_pair, write_lift]
      · simp only [if_neg h0]
        by_cases h1 : (op == 1) = true
        · simp only [if_pos h1, liftInt_pair, write_lift]
        · simp only [if_neg h1]
          by_cases h3 : (op == 3) = true
          · simp only [if_pos h3, begin_lift]
          · simp only [if_neg h3]
            by_cases h4 : (op == 4) = true
            · simp only [if_pos h4, commit_lift]
            · simp only [if_neg h4]
              by_cases h5 : (op == 5) = true
              · simp only [if_pos h5, rollback_lift]
              · simp only [if_neg h5, liftInt_pair]
  rw [← h]
  dsimp only [liftInt, liftPair]
  rfl
theorem commands_lift (style : Nat) (xs : Task.Words) (is : List Nat) (p : Task.TxState × Task.Words) :
  liftPair (is.foldl (fun (s,out) i =>
    let (next,data) := Task.executeTx style s (Task.iz xs (1+3*i)) (Task.iz xs (2+3*i)) (Task.iz xs (3+3*i))
    (next,out++data)) p) =
  is.foldl (fun (s,out) i =>
    let (next,data) := executeTx style s (iz xs (1+3*i)) (iz xs (2+3*i)) (iz xs (3+3*i))
    (next,out++data)) (liftPair p) := by
  induction is generalizing p with
  | nil => rfl
  | cons i is ih =>
    cases p with
    | mk s out =>
      dsimp only [List.foldl_cons, liftPair, Prod.fst, Prod.snd]
      rw [← execute_lift]
      simpa only [liftPair, Task.iz, Task.getOr, iz, getOr] using ih _
'''
    for name, style in zip(('a', 'b'), styles):
        bridge += f'''theorem {name}_binding : Task.{name} = entry 1 {style} := by
  funext xs
  unfold Task.{name} entry transactions
  have h := commands_lift {style} xs (List.range (Task.iz xs 0).toNat) (({{}} : Task.TxState),([] : Task.Words))
  dsimp only [liftPair, lift, Task.iz, Task.getOr, iz, getOr] at h ⊢
  change some _ = some _
  rw [← h]
  rfl
'''
    bridge += f'''theorem domain_binding : Task.valid = valid 1 := by rfl
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
