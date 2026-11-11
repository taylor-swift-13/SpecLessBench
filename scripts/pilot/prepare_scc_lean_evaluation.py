"""Prepare an isolated Lean SCC pair and certify both frozen targets."""
import hashlib
import json
from pathlib import Path
import re
import resource
import textwrap
import time

from prepare_classics_evaluation import lean_declarations
from prepare_evaluation import PACKAGES, ROOT, compile_lean
from prepare_leases_lean_evaluation import assert_idle, idle_preparation
from single_task_runner import tree_digest


SCC_BRIDGE = '''import Task
import GraphSuiteTargets
open SpecLessBenchGraphSuite
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000

def liftTS (s : Task.TS) : TS := ⟨s.idx,s.low,s.stack,s.ons,s.comp,s.clock,s.count⟩

theorem word_to_task : word = Task.word := rfl
theorem getOr_bool_to_task : @getOr Bool = @Task.getOr Bool := rfl
theorem put_bool_to_task : @put Bool = @Task.put Bool := rfl
theorem put_int_to_task : @put Int = @Task.put Int := rfl
theorem lift_stack (s : Task.TS) : (liftTS s).stack = s.stack := rfl
theorem lift_idx (s : Task.TS) : (liftTS s).idx = s.idx := rfl
theorem lift_low (s : Task.TS) : (liftTS s).low = s.low := rfl
theorem lift_ons (s : Task.TS) : (liftTS s).ons = s.ons := rfl

theorem foldlM_lift {S T I : Type} (lift : S → T)
    (stepA : S → I → Option S) (stepB : T → I → Option T)
    (agree : ∀ s i, (stepA s i).map lift = stepB (lift s) i)
    (items : List I) (state : S) :
    (items.foldlM stepA state).map lift = items.foldlM stepB (lift state) := by
  induction items generalizing state with
  | nil => rfl
  | cons item items ih =>
    rw [List.foldlM_cons, List.foldlM_cons, ← agree]
    cases stepA state item with
    | none => rfl
    | some next => exact ih next

theorem tarjanPop_lift (fuel v : Nat) (s : Task.TS) :
    (Task.tarjanPop fuel v s).map liftTS = tarjanPop fuel v (liftTS s) := by
  induction fuel generalizing s with
  | zero => rfl
  | succ fuel ih =>
    rw [Task.tarjanPop, tarjanPop, lift_stack]
    cases hstack : s.stack with
    | nil => rfl
    | cons x rest =>
      by_cases same : (x == v) = true
      · simp [hstack, same, liftTS, Task.put, put]
      · simp [hstack, same, ih, liftTS, Task.put, put]

def taskVisitStep (recur : Nat → Task.TS → Option Task.TS)
    (n : Nat) (xs : Task.Words) (v : Nat) (s : Task.TS) (w : Nat) : Option Task.TS := do
  if Task.word xs (1+v*n+w) == 0 then pure s
  else if Task.word s.idx w < 0 then
    let s ← recur w s
    pure {s with low := Task.put s.low v (min (Task.word s.low v) (Task.word s.low w))}
  else if Task.getOr s.ons w false then
    pure {s with low := Task.put s.low v (min (Task.word s.low v) (Task.word s.idx w))}
  else pure s

def sourceVisitStep (recur : Nat → TS → Option TS)
    (n : Nat) (xs : Words) (v : Nat) (s : TS) (w : Nat) : Option TS := do
  if word xs (1+v*n+w) == 0 then pure s
  else if word s.idx w < 0 then
    let s ← recur w s
    pure {s with low := put s.low v (min (word s.low v) (word s.low w))}
  else if getOr s.ons w false then
    pure {s with low := put s.low v (min (word s.low v) (word s.idx w))}
  else pure s

theorem visitStep_lift (recurA : Nat → Task.TS → Option Task.TS)
    (recurB : Nat → TS → Option TS)
    (agree : ∀ w s, (recurA w s).map liftTS = recurB w (liftTS s))
    (n : Nat) (xs : Words) (v : Nat) (s : Task.TS) (w : Nat) :
    (taskVisitStep recurA n xs v s w).map liftTS = sourceVisitStep recurB n xs v (liftTS s) w := by
  unfold taskVisitStep sourceVisitStep
  simp only [word_to_task, getOr_bool_to_task, lift_idx, lift_ons]
  by_cases empty : (Task.word xs (1+v*n+w) == 0) = true
  · simp only [empty, if_true] <;> rfl
  · simp only [empty, if_false]
    by_cases fresh : Task.word s.idx w < 0
    · simp only [fresh, if_true]
      rw [← agree]
      cases recurA w s <;> rfl
    · simp only [fresh, if_false]
      by_cases stacked : Task.getOr s.ons w false = true
      · simp only [stacked, if_true] <;> rfl
      · simp only [stacked, if_false] <;> rfl

theorem tarjanVisit_lift (n : Nat) (xs : Words) (fuel v : Nat) (s : Task.TS) :
    (Task.tarjanVisit n xs fuel v s).map liftTS = tarjanVisit n xs fuel v (liftTS s) := by
  induction fuel generalizing v s with
  | zero => rfl
  | succ fuel ih =>
    let start : Task.TS := ⟨Task.put s.idx v s.clock, Task.put s.low v s.clock,
      v::s.stack, Task.put s.ons v true, s.comp, s.clock+1, s.count⟩
    let stepA := taskVisitStep (Task.tarjanVisit n xs fuel) n xs v
    let stepB := sourceVisitStep (tarjanVisit n xs fuel) n xs v
    have folds := foldlM_lift liftTS stepA stepB
      (visitStep_lift _ _ ih n xs v) (List.range n) start
    rw [Task.tarjanVisit, tarjanVisit]
    change (((List.range n).foldlM stepA start >>= fun next =>
      if Task.word next.low v == Task.word next.idx v then Task.tarjanPop 9 v next else some next).map liftTS) =
      ((List.range n).foldlM stepB (liftTS start) >>= fun next =>
        if word next.low v == word next.idx v then tarjanPop 9 v next else some next)
    rw [← folds]
    cases (List.range n).foldlM stepA start with
    | none => rfl
    | some next =>
      change (if Task.word next.low v == Task.word next.idx v then Task.tarjanPop 9 v next else some next).map liftTS =
        if Task.word next.low v == Task.word next.idx v then tarjanPop 9 v (liftTS next) else some (liftTS next)
      by_cases root : (Task.word next.low v == Task.word next.idx v) = true
      · simpa only [root, if_true] using tarjanPop_lift 9 v next
      · simp only [root, if_false] <;> rfl

theorem tarjan_eq (n : Nat) (xs : Words) : Task.tarjan n xs = tarjan n xs := by
  let start : Task.TS := ⟨List.replicate n (-1),List.replicate n 0,[],List.replicate n false,List.replicate n (-1),0,0⟩
  let stepA := fun (s : Task.TS) v => if Task.word s.idx v < 0 then Task.tarjanVisit n xs 9 v s else some s
  let stepB := fun (s : TS) v => if word s.idx v < 0 then tarjanVisit n xs 9 v s else some s
  have agree (s : Task.TS) (v : Nat) : (stepA s v).map liftTS = stepB (liftTS s) v := by
    simp only [stepA, stepB, word_to_task, lift_idx]
    by_cases fresh : Task.word s.idx v < 0
    · simpa only [fresh, if_true] using tarjanVisit_lift n xs 9 v s
    · simp only [fresh, if_false] <;> rfl
  have folds := foldlM_lift liftTS stepA stepB agree (List.range n) start
  change ((List.range n).foldlM stepA start >>= fun next => some next.comp) =
    ((List.range n).foldlM stepB (liftTS start) >>= fun next => some next.comp)
  rw [← folds]
  cases (List.range n).foldlM stepA start <;> rfl

theorem firstVisit_eq (n : Nat) (xs : Words) (fuel v : Nat) (seen : List Bool) (order : List Nat) :
    Task.firstVisit n xs fuel v seen order = firstVisit n xs fuel v seen order := by
  induction fuel generalizing v seen order with
  | zero => rfl
  | succ fuel ih =>
    rw [Task.firstVisit, firstVisit]
    simp only [word_to_task, getOr_bool_to_task, put_bool_to_task, ih] <;> rfl

theorem secondVisit_eq (n : Nat) (xs : Words) (mode : Bool) (fuel v : Nat) (c : Int) (comp : Words) :
    Task.secondVisit n xs mode fuel v c comp = secondVisit n xs mode fuel v c comp := by
  induction fuel generalizing v c comp with
  | zero => rfl
  | succ fuel ih =>
    rw [Task.secondVisit, secondVisit]
    simp only [word_to_task, put_int_to_task, ih] <;> rfl

theorem kosaraju_eq (n : Nat) (xs : Words) (mode : Bool) : Task.kosaraju n xs mode = kosaraju n xs mode := by
  unfold Task.kosaraju kosaraju
  simp only [getOr_bool_to_task, word_to_task, firstVisit_eq, secondVisit_eq] <;> rfl
'''


def _public_task(native, domain, raw_native, style):
    records = raw_native.split('structure TS where', 1)[1].split('def tarjanPop', 1)[0]
    shared = ('Words', 'getOr', 'word', 'put', 'finish')
    traversal = ('tarjanPop', 'tarjanVisit', 'tarjan', 'firstVisit', 'secondVisit', 'kosaraju')
    dispatcher = 'if style == 0 then tarjan n xs else kosaraju n xs (style == 2)'
    if native['scc'].count(dispatcher) != 1:
        raise ValueError('Frozen SCC dispatcher changed')
    implementations = []
    for name, expression in (('a', 'tarjan n xs'), ('b', 'kosaraju n xs ' + ('true' if style == '2' else 'false'))):
        text = native['scc'].replace('def scc (style : Nat)', 'def ' + name, 1)
        implementations.append(text.replace(dispatcher, expression, 1))

    graph_domain = re.search(r'if domain == 0 \|\| domain == 1 then\s*(.*?)\n  else if domain == 2 then',
                             domain['validB'], re.S)
    if graph_domain is None:
        raise ValueError('Frozen SCC input domain changed')
    branch = 'if domain == 1 then between v 0 1\n        else if p/n.toNat == p%n.toNat then v == -1 else between v (-1) 100'
    graph_domain = graph_domain.group(1)
    if graph_domain.count(branch) != 1:
        raise ValueError('Frozen SCC input domain branch changed')
    domain_body = textwrap.dedent('    ' + graph_domain.replace(branch, 'between v 0 1'))
    valid = 'def valid (xs : Words) : Prop := (\n' + textwrap.indent(domain_body, '  ') + '\n) = true'
    pieces = [native[name] for name in shared] + ['structure TS where' + records]
    pieces += [native[name] for name in traversal]
    pieces += [domain['between'], valid, *implementations]
    public = 'import Lean\nnamespace Task\n' + '\n'.join(pieces).replace('mutant', 'mode') + '''
def equivalent : Prop := ∀ x, valid x → ∃ o, a x=some o ∧ b x=some o
def refutationAt (x oa ob : Words) : Prop := valid x ∧ a x=some oa ∧ b x=some ob ∧ oa≠ob
end Task
'''
    return re.sub(r'(?<![A-Za-z0-9_.])pure\b', 'Pure.pure', public)


def _binding_text(ctx, style):
    return SCC_BRIDGE + f'''
theorem a_binding : Task.a = entry 1 0 := by
  funext xs
  unfold Task.a
  dsimp only
  rw [tarjan_eq] <;> rfl
theorem b_binding : Task.b = entry 1 {style} := by
  funext xs
  unfold Task.b
  dsimp only
  rw [kosaraju_eq] <;> rfl
theorem domain_binding : Task.valid = valid 1 := by rfl
theorem equivalent_binding : Task.equivalent = SpecLessBenchGraphSuiteSubmission.{ctx['equivalence_goal']} := by
  unfold Task.equivalent SpecLessBenchGraphSuiteSubmission.{ctx['equivalence_goal']} SpecLessBenchGraphSuite.{ctx['equivalence_goal']} Equivalent
  rw [domain_binding, a_binding, b_binding]
theorem refutation_binding (x oa ob : Task.Words) : Task.refutationAt x oa ob = SpecLessBenchGraphSuiteSubmission.{ctx['refutation_at_goal']} x oa ob := by
  unfold Task.refutationAt SpecLessBenchGraphSuiteSubmission.{ctx['refutation_at_goal']} SpecLessBenchGraphSuite.{ctx['refutation_at_goal']} RefutationAt
  rw [domain_binding, a_binding, b_binding]
#print axioms a_binding
#print axioms b_binding
#print axioms domain_binding
#print axioms equivalent_binding
#print axioms refutation_binding
'''


def prepare_scc_lean(row, *, package_root, deadline=None):
    """Certify one SCC pair in private scratch and leave its registry pending."""
    ctx = row['context']
    if (ctx.get('tranche'), ctx.get('family_index'), ctx.get('domain_index')) != ('graphsuite', 1, 1):
        return None
    package_root = Path(package_root).resolve()
    if package_root == PACKAGES.resolve() or PACKAGES.resolve() in package_root.parents:
        raise ValueError('SCC preparation requires scratch outside the published package tree')
    package = package_root / row['pilot_id'] / 'lean'
    published = PACKAGES / row['pilot_id'] / 'lean' / 'registry.json'
    with idle_preparation():
        if package.exists() or published.exists():
            raise ValueError('SCC package or prior scratch already exists')
        started = time.monotonic()
        source = ROOT / 'benchmarks/tasks/graphsuite-core/lean'
        source_paths = {name: source / (name + '.lean')
                        for name in ('GraphSuiteNative', 'GraphSuiteDomain', 'GraphSuiteGoals')}
        source_paths['GraphSuiteTargets'] = ROOT / 'benchmarks/proof-interface/lean/GraphSuiteTargets.lean'
        raw = {name: path.read_bytes() for name, path in source_paths.items()}
        text = {name: data.decode('utf-8').replace('\r\n', '\n') for name, data in raw.items()}
        native = lean_declarations(text['GraphSuiteNative'])
        domain = lean_declarations(text['GraphSuiteDomain'])
        goals = lean_declarations(text['GraphSuiteGoals'])
        styles = [re.findall(r'entry\s+1\s+(\d+)', goals[ctx[key]])
                  for key in ('equivalence_goal', 'refutation_at_goal')]
        if styles[0] not in (['0', '1'], ['0', '2']) or styles[1] != styles[0]:
            raise ValueError('Frozen SCC pair or target changed')
        style = styles[0][1]

        task = package / 'task'
        binding = package / 'binding'
        frozen = package / 'frozen'
        for folder in (task, binding, frozen):
            folder.mkdir(parents=True, mode=0o700)
        (task / 'Task.lean').write_text(_public_task(native, domain, text['GraphSuiteNative'], style))
        (task / 'Obligation.lean').write_text('import Task\nnamespace Obligation\ndef goal : Prop := Task.equivalent\nend Obligation\n')
        for name, data in raw.items():
            (frozen / (name + '.lean')).write_bytes(data)
        (binding / 'Binding.lean').write_text(_binding_text(ctx, style))

        logs = []
        def compile_at(folder, module):
            assert_idle()
            if published.exists():
                raise RuntimeError('SCC registry appeared during preparation')
            log = compile_lean(folder, module, [task, frozen, binding], deadline=deadline)
            logs.append(log)
            (binding / 'compile.log').write_text('\n'.join(logs))
            return log

        for module in ('Task', 'Obligation'):
            compile_at(task, module)
        for module in source_paths:
            compile_at(frozen, module)
        audit = compile_at(binding, 'Binding')
        audits = re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", audit)
        expected = {'a_binding', 'b_binding', 'domain_binding', 'equivalent_binding', 'refutation_binding'}
        allowed = {'propext', 'Classical.choice', 'Quot.sound'}
        if len(audits) != len(expected) or {name for name, _ in audits} != expected:
            raise ValueError('Incomplete SCC correspondence axiom audit')
        if any({axiom.strip() for axiom in axioms.split(',') if axiom.strip()} - allowed
               for _, axioms in audits):
            raise ValueError('Unapproved SCC correspondence axiom')
        meta = {
            'pilot_id': row['pilot_id'], 'platform': 'lean', 'public_sha256': tree_digest(task),
            'binding': 'lean-kernel-checked-scc-state-transport-and-exact-frozen-target',
            'source_context': row['source_context_id'], 'source_goal': ctx['equivalence_goal'],
            'frozen_source_sha256': {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()},
            'preparation_wall_seconds': time.monotonic() - started,
            'preparation_controller_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'compiler_costs': 'compile-costs.jsonl', 'preparation_model_tokens': None,
            'final_proof_attempted': False,
        }
        (package / 'registry.pending.json').write_text(json.dumps(meta, indent=2) + '\n')
        return meta
