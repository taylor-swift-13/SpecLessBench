"""Minimal quoted-tokenizer package; transport its private record representation."""
import hashlib
import json
import re
import resource
import time

from prepare_evaluation import ROOT, PACKAGES, compile_rocq, compile_lean
from prepare_classics_evaluation import declarations, lean_declarations
from single_task_runner import tree_digest


def prepare_quotes_rocq(row):
    ctx = row['context']
    if ctx.get('tranche') != 'boundaries' or ctx.get('family_index') != 5:
        return None
    package = PACKAGES / row['pilot_id'] / 'rocq'
    if (package / 'registry.json').exists():
        meta = json.loads((package / 'registry.json').read_text())
        if tree_digest(package / 'task') != meta['public_sha256']:
            raise ValueError('Existing quoted-tokenizer package changed')
        return meta
    if package.exists():
        raise ValueError('Incomplete preparation requires inspection: ' + str(package))
    started = time.monotonic()
    source = ROOT / 'benchmarks/tasks/boundaries-core/rocq'
    raw = (source / 'BoundaryNative.v').read_text()
    native = declarations(raw)
    domain = declarations((source / 'BoundaryDomain.v').read_text())
    goals = declarations((source / 'BoundaryGoals.v').read_text())
    selected = [goals[ctx[k]] for k in ('equivalence_goal', 'refutation_at_goal')]
    styles = re.findall(r'BoundaryNative.entry\s+5\s+(\d+)', selected[0])
    if styles not in (['0', '1'], ['0', '2']):
        raise ValueError('Unexpected frozen quoted-tokenizer pair')
    record = re.search(r'^Record quote_state:.*?\.', raw, re.M | re.S).group()
    before, observe = native['quotes'].split('  let final:=', 1)
    observe = 'Definition observe (s:quote_state) (data:words) := let final:=' + observe
    pair = []
    pattern = r'if Nat.eqb style 1 then quote_spans 128 data 0 quote_initial\s+else Some\(fold_left\(fun s cp=>quote_step\(Nat.eqb style 2\)s\(snd cp\)\(fst cp\)\)\(List.combine\(seq 0\(length data\)\)data\)quote_initial\)'
    for name, style in zip(('a', 'b'), styles):
        text = before.replace('Definition quotes style xs', 'Definition ' + name + ' xs', 1)
        expr = ('quote_spans 128 data 0 quote_initial' if style == '1' else
                'Some(fold_left(fun s cp=>quote_step ' + ('true' if style == '2' else 'false') + ' s(snd cp)(fst cp))(List.combine(seq 0(length data))data)quote_initial)')
        text, count = re.subn(pattern, expr + ' ', text)
        if count != 1 or re.search(r'\bstyle\b', text):
            raise ValueError('Unexpected tokenizer dispatcher')
        pair.append(text + ' observe s data.\n')
    pre, match = domain['validb'].split(':=', 1)[1].split('match domain with', 1)
    clauses = re.findall(r'\n  \| (.*?)=>(.*?)(?=\n  \| |\n  end\.)', match, re.S)
    bodies = [body for pat, body in clauses if pat.count('S') == 6 and pat.strip() != '_']
    if not bodies:
        bodies = [body for pat, body in clauses if pat.strip() == '_']
    if len(bodies) != 1:
        raise ValueError('Missing frozen tokenizer domain')
    valid = 'Definition valid (xs:words) : Prop := (' + pre + bodies[0] + ')=true.'
    names = ['words', 'iz', 'finish', 'obind', 'quote_initial', 'qmake', 'qadd', 'qcommit', 'quote_step', 'ordinary', 'take_ordinary', 'quote_spans']
    parts = [native[n] for n in names[:4]]
    notation = 'Notation "\'let*\' x \':=\' c \'in\' b" := (obind c (fun x=>b)) (at level 200,x ident,c at level 100,b at level 200).'
    parts += [notation, record] + [native[n] for n in names[4:]]
    parts += [domain['get'], domain['in_range'], valid, observe, *pair]
    header = 'From Coq Require Import ZArith List Bool.\nImport ListNotations.\nOpen Scope nat_scope.\n'
    public = header + '\n'.join(parts) + '''
Definition equivalent : Prop := forall x, valid x -> exists o, a x=Some o /\ b x=Some o.
Definition refutationAt (x oa ob:words) : Prop := valid x /\ a x=Some oa /\ b x=Some ob /\ oa<>ob.
'''
    public = re.sub(r'\bmutant\b', 'mode', public)
    task = package / 'task'
    binding = package / 'binding'
    task.mkdir(parents=True, mode=0o700)
    binding.mkdir(mode=0o700)
    (task / 'Task.v').write_text(public)
    (task / 'Obligation.v').write_text('From Trusted Require Import Task.\nDefinition goal : Prop := Task.equivalent.\n')
    original = ROOT / '_build/pilot-v1/boundary-rocq-binding'
    original.mkdir(parents=True, exist_ok=True)
    paths = [(task, 'Trusted'), (binding, 'Binding'), (original, 'Frozen')]
    def compile_at(folder, name):
        return compile_rocq(folder, name, paths)
    logs = [compile_at(task, n) for n in ('Task', 'Obligation')]
    for name in ('BoundaryNative', 'BoundaryDomain'):
        src = source / (name + '.v')
        dest = original / src.name
        if not dest.exists() or dest.read_bytes() != src.read_bytes() or not (original / (name + '.vo')).exists():
            dest.write_bytes(src.read_bytes())
            logs.append(compile_at(original, name))
    (binding / 'FrozenTarget.v').write_text('From Frozen Require Import BoundaryNative BoundaryDomain.\n' + '\n'.join(selected) + '\n')
    logs.append(compile_at(binding, 'FrozenTarget'))
    tokens = set(native) | {'quote_state', 'qm', 'qo', 'qe', 'qs', 'qa', 'qc', 'qt', 'qcode', 'qoffset'}
    original_observe = re.sub(r'\b[A-Za-z_][A-Za-z_0-9]*\b', lambda m: 'BoundaryNative.' + m.group() if m.group() in tokens else m.group(), observe.replace('Definition observe ', 'Definition source_observe ', 1))
    bridge = header + 'From Trusted Require Import Task.\nFrom Frozen Require Import BoundaryNative BoundaryDomain.\nFrom Binding Require Import FrozenTarget.\n' + original_observe + '''
Definition lift (s:Task.quote_state) : BoundaryNative.quote_state :=
 {| BoundaryNative.qm:=Task.qm s; BoundaryNative.qo:=Task.qo s;
    BoundaryNative.qe:=Task.qe s; BoundaryNative.qs:=Task.qs s;
    BoundaryNative.qa:=Task.qa s; BoundaryNative.qc:=Task.qc s;
    BoundaryNative.qt:=Task.qt s; BoundaryNative.qcode:=Task.qcode s;
    BoundaryNative.qoffset:=Task.qoffset s |}.
Ltac split_tests := repeat match goal with
 | |- context [if ?b then _ else _] => destruct b eqn:?; cbn
 end.
Lemma step_lift m s c p : lift (Task.quote_step m s c p) = BoundaryNative.quote_step m (lift s) c p.
Proof. destruct s; unfold Task.quote_step, BoundaryNative.quote_step;
 cbn; split_tests; reflexivity. Qed.
Lemma fold_lift m cps s :
 lift (fold_left (fun s cp=>Task.quote_step m s (snd cp) (fst cp)) cps s) =
 fold_left (fun s cp=>BoundaryNative.quote_step m s (snd cp) (fst cp)) cps (lift s).
Proof. revert s; induction cps; intros; cbn; [reflexivity|].
 rewrite <- step_lift. apply IHcps. Qed.
Lemma take_ordinary_eq : Task.take_ordinary = BoundaryNative.take_ordinary. Proof. reflexivity. Qed.
Lemma spans_lift fuel src p s :
 option_map lift (Task.quote_spans fuel src p s) = BoundaryNative.quote_spans fuel src p (lift s).
Proof. revert src p s; induction fuel; intros; destruct src; destruct s;
 cbn [Task.quote_spans BoundaryNative.quote_spans lift]; cbn;
 try rewrite take_ordinary_eq; try unfold Task.ordinary, BoundaryNative.ordinary; split_tests;
 repeat rewrite IHfuel; try rewrite step_lift; reflexivity. Qed.
Lemma observe_lift s data : Task.observe s data = source_observe (lift s) data.
Proof. destruct s; unfold Task.observe, source_observe; cbn; split_tests; reflexivity. Qed.
Lemma initial_lift : lift Task.quote_initial = BoundaryNative.quote_initial. Proof. reflexivity. Qed.
'''
    for name, style in zip(('a', 'b'), styles):
        data = 'firstn (Z.to_nat (Task.iz xs 0)) (skipn 1 xs)'
        state = ('Task.quote_spans 128 data 0 Task.quote_initial' if style == '1' else
                 'Some (fold_left (fun s cp=>Task.quote_step ' + ('true' if style == '2' else 'false') + ' s (snd cp) (fst cp)) (List.combine (seq 0 (length data)) data) Task.quote_initial)')
        frozen_state = state.replace('Task.', 'BoundaryNative.')
        transport = 'spans_lift' if style == '1' else 'fold_lift'
        bridge += f'''Lemma {name}_binding xs : Task.{name} xs = BoundaryNative.entry 5 {style} xs.
Proof.
 set (data := {data}).
 change ((match {state} with None=>None|Some s=>Task.observe s data end) =
 (match {frozen_state} with None=>None|Some s=>source_observe s data end)).
 rewrite <- initial_lift, <- {transport}.
 destruct ({state}) as [s|]; cbn; try reflexivity; apply observe_lift.
Qed.
'''
    # Rewriting the source state computation is performed before changing its
    # final observation. These are representation-transport proofs, not solve.
    bridge += f'''Lemma domain_binding : Task.valid = BoundaryDomain.valid 6. Proof. reflexivity. Qed.
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
            'binding': 'rocq-kernel-checked-record-transport-and-exact-frozen-target',
            'source_context': row['source_context_id'], 'source_goal': ctx['equivalence_goal'],
            'frozen_source_sha256': {n: hashlib.sha256((source / (n + '.v')).read_bytes()).hexdigest()
                                     for n in ('BoundaryNative', 'BoundaryDomain', 'BoundaryGoals')},
            'preparation_wall_seconds': time.monotonic() - started,
            'preparation_controller_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'compiler_costs': 'compile-costs.jsonl', 'preparation_model_tokens': None,
            'final_proof_attempted': False}
    (package / 'registry.json').write_text(json.dumps(meta, indent=2) + '\n')
    return meta


def prepare_quotes_lean(row):
    ctx = row['context']
    if ctx.get('tranche') != 'boundaries' or ctx.get('family_index') != 5:
        return None
    package = PACKAGES / row['pilot_id'] / 'lean'
    if (package / 'registry.json').exists():
        meta = json.loads((package / 'registry.json').read_text())
        if tree_digest(package / 'task') != meta['public_sha256']:
            raise ValueError('Existing quoted-tokenizer package changed')
        return meta
    if package.exists():
        raise ValueError('Incomplete preparation requires inspection: ' + str(package))
    started = time.monotonic()
    source = ROOT / 'benchmarks/tasks/boundaries-core/lean'
    raw = (source / 'BoundaryNative.lean').read_text()
    native = lean_declarations(raw)
    domains = lean_declarations((source / 'BoundaryDomain.lean').read_text())
    goals = lean_declarations((source / 'BoundaryGoals.lean').read_text())
    styles = re.findall(r'entry\s+5\s+(\d+)', goals[ctx['equivalence_goal']])
    if styles not in (['0', '1'], ['0', '2']):
        raise ValueError('Unexpected frozen tokenizer pair')
    record = raw.split('structure QuoteState where', 1)[1].split('def appendChar', 1)[0]
    before, after = native['quotes'].split('  let final :=', 1)
    observe = ('def observe (s : QuoteState) (data : Words) : Option Words := do\n  let final :=' + after).replace('  pure (finish', '  return (finish')
    pair = []
    pattern = r'if style == 1 then quoteSpans 128 data 0 \{\} else some \(\(data.zipIdx\).foldl \(fun s \(c,p\) => quoteStep \(style == 2\) s c p\) \{\}\)'
    for name, style in zip(('a', 'b'), styles):
        text = before.replace('def quotes (style : Nat)', 'def ' + name, 1)
        expr = ('quoteSpans 128 data 0 {}' if style == '1' else
                'some ((data.zipIdx).foldl (fun s (c,p) => quoteStep ' + ('true' if style == '2' else 'false') + ' s c p) {})')
        text, count = re.subn(pattern, expr, text)
        if count != 1 or re.search(r'\bstyle\b', text):
            raise ValueError('Unexpected tokenizer dispatcher')
        pair.append(text + '  observe s data\n')
    pre, branches = domains['validB'].split(':=', 1)[1].split('match domain with', 1)
    body = branches.split('  | _ =>', 1)[1]
    valid = 'def valid (xs : Words) : Prop := (' + pre + body + ') = true\n'
    task = package / 'task'; binding = package / 'binding'
    task.mkdir(parents=True, mode=0o700); binding.mkdir(mode=0o700)
    public = 'import Lean\nnamespace Task\n' + '\n'.join(
        [native[n] for n in ('Words', 'getOr', 'iz', 'finish')] + ['structure QuoteState where' + record] +
        [native[n] for n in ('appendChar', 'commitToken', 'quoteStep')] +
        ([native[n] for n in ('ordinary', 'quoteSpans')] if '1' in styles else []) + [domains['inRange'], valid, observe, *pair]) + '''
def equivalent : Prop := ∀ x, valid x → ∃ o, a x=some o ∧ b x=some o
def refutationAt (x oa ob : Words) : Prop := valid x ∧ a x=some oa ∧ b x=some ob ∧ oa≠ob
end Task
'''
    public = re.sub(r'\bmutant\b', 'modeFlag', public)
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
    bridge = 'import Task\nimport BoundaryGoals\nopen SpecLessBenchBoundary\nset_option maxRecDepth 4096\nset_option maxHeartbeats 2000000\n'
    bridge += observe.replace('def observe ', 'def sourceObserve ', 1) + '''
def lift (s : Task.QuoteState) : QuoteState :=
  ⟨s.mode,s.opening,s.escaping,s.slash,s.active,s.current,s.tokens,s.code,s.offset⟩
theorem step_lift (m : Bool) (s : Task.QuoteState) (c : Int) (p : Nat) :
  lift (Task.quoteStep m s c p) = quoteStep m (lift s) c p := by
  cases s
  dsimp only [Task.quoteStep, quoteStep, Task.appendChar, appendChar, Task.commitToken, commitToken, lift]
  repeat first | rfl | split
theorem fold_lift (m : Bool) (cps : List (Int × Nat)) (s : Task.QuoteState) :
  lift (cps.foldl (fun s (c,p) => Task.quoteStep m s c p) s) =
  cps.foldl (fun s (c,p) => quoteStep m s c p) (lift s) := by
  induction cps generalizing s with
  | nil => rfl
  | cons cp cps ih =>
    cases cp
    simp only [List.foldl_cons]
    rw [← step_lift]
    exact ih _
theorem observe_lift (s : Task.QuoteState) (data : Task.Words) :
  Task.observe s data = sourceObserve (lift s) data := by
  cases s
  dsimp only [Task.observe, sourceObserve, Task.commitToken, commitToken, lift]
  repeat first | rfl | split
'''
    if '1' in styles:
        bridge += '''theorem ordinary_binding : Task.ordinary = ordinary := by rfl
theorem spans_lift (fuel : Nat) (src : Task.Words) (p : Nat) (s : Task.QuoteState) :
  Option.map lift (Task.quoteSpans fuel src p s) = quoteSpans fuel src p (lift s) := by
  induction fuel generalizing src p s with
  | zero => cases src <;> rfl
  | succ fuel ih =>
    cases src with
    | nil => rfl
    | cons c cs =>
      cases s
      dsimp only [Task.quoteSpans, quoteSpans, lift, Task.iz, Task.getOr, iz, getOr]
      simp only [ordinary_binding]
      split
      · rfl
      · split
        · rw [ih]
          simp_all [lift]
        · rw [ih, step_lift]
          simp_all [lift]
'''
    for name, style in zip(('a', 'b'), styles):
        if style == '1':
            bridge += f'''theorem {name}_binding : Task.{name} = entry 5 {style} := by
  funext xs
  let data := (xs.drop 1).take (Task.iz xs 0).toNat
  change ((Task.quoteSpans 128 data 0 {{}}).bind (fun s => Task.observe s data)) =
    ((quoteSpans 128 data 0 {{}}).bind (fun s => sourceObserve s data))
  have h := spans_lift 128 data 0 ({{}} : Task.QuoteState)
  have init : lift ({{}} : Task.QuoteState) = ({{}} : QuoteState) := rfl
  rw [init] at h
  rw [← h]
  cases Task.quoteSpans 128 data 0 ({{}} : Task.QuoteState) with
  | none => rfl
  | some s => exact observe_lift s data
'''
            continue
        mode = 'true' if style == '2' else 'false'
        bridge += f'''theorem {name}_binding : Task.{name} = entry 5 {style} := by
  funext xs
  let data := (xs.drop 1).take (Task.iz xs 0).toNat
  change Task.observe (data.zipIdx.foldl (fun s (c,p) => Task.quoteStep {mode} s c p) {{}}) data =
    sourceObserve (data.zipIdx.foldl (fun s (c,p) => quoteStep {mode} s c p) {{}}) data
  have h := fold_lift {mode} data.zipIdx ({{}} : Task.QuoteState)
  have init : lift ({{}} : Task.QuoteState) = ({{}} : QuoteState) := rfl
  rw [init] at h
  rw [← h]
  exact observe_lift _ _
'''
    bridge += f'''theorem domain_binding : Task.valid = valid 6 := by rfl
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
                                     for n in ('BoundaryNative', 'BoundaryDomain', 'BoundaryGoals')},
            'preparation_wall_seconds': time.monotonic() - started,
            'preparation_controller_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'compiler_costs': 'compile-costs.jsonl', 'preparation_model_tokens': None,
            'final_proof_attempted': False}
    (package / 'registry.json').write_text(json.dumps(meta, indent=2) + '\n')
    return meta
