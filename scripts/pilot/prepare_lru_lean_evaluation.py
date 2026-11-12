"""Stage source-bound Lean LRU packages without enabling them."""
import hashlib
import json
from pathlib import Path
import re
import resource
import time

from prepare_classics_evaluation import lean_declarations
from prepare_evaluation import PACKAGES, ROOT, compile_lean
from prepare_leases_lean_evaluation import assert_idle, idle_preparation
from single_task_runner import tree_digest


LRU_BRIDGE = '''import Task
import StatefulTargets
open SpecLessBenchStateful
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000

def liftNode (n : Task.CacheNode) : CacheNode :=
  ⟨n.key,n.value,n.prev,n.next,n.live⟩

def liftState (s : Task.CacheState) : CacheState :=
  ⟨s.cap,s.order,s.nodes.map liftNode,s.head,s.tail⟩

def liftPair (p : Task.CacheState × Task.Words) : CacheState × Words :=
  (liftState p.1,p.2)

theorem lifted_key (n : Task.CacheNode) : (liftNode n).key = n.key := rfl
theorem lifted_value (n : Task.CacheNode) : (liftNode n).value = n.value := rfl
theorem lifted_prev (n : Task.CacheNode) : (liftNode n).prev = n.prev := rfl
theorem lifted_next (n : Task.CacheNode) : (liftNode n).next = n.next := rfl
theorem lifted_live (n : Task.CacheNode) : (liftNode n).live = n.live := rfl
theorem lifted_cap (s : Task.CacheState) : (liftState s).cap = s.cap := rfl
theorem lifted_order (s : Task.CacheState) : (liftState s).order = s.order := rfl
theorem lifted_head (s : Task.CacheState) : (liftState s).head = s.head := rfl
theorem lifted_tail (s : Task.CacheState) : (liftState s).tail = s.tail := rfl

theorem lookup_node_lift (nodes : List Task.CacheNode) (i : Nat) :
    liftNode (Task.getOr nodes i {}) = getOr (nodes.map liftNode) i {} := by
  unfold Task.getOr getOr
  rw [List.getElem?_map]
  exact (Option.getD_map liftNode {} nodes[i]?).symm

theorem node_lift (s : Task.CacheState) (id : Int) :
    liftNode (Task.nodeAt s id) = nodeAt (liftState s) id :=
  lookup_node_lift s.nodes id.toNat

theorem set_node_lift (s : Task.CacheState) (id : Int) (n : Task.CacheNode) :
    liftState (Task.setNode s id n) = setNode (liftState s) id (liftNode n) := by
  simp [liftState, Task.setNode, setNode, Task.put, put]

theorem size_lift (style : Nat) (s : Task.CacheState) :
    Task.cacheSize style s = cacheSize style (liftState s) := by
  simp [Task.cacheSize, cacheSize, liftState, List.filter_map, Function.comp_def, liftNode]

theorem find_congr (p q : Nat → Bool) (ids : List Nat) (h : ∀ i, p i = q i) :
    ids.find? p = ids.find? q := by
  induction ids with
  | nil => rfl
  | cons i tail ih =>
    rw [List.find?_cons, List.find?_cons, h i, ih]

theorem lookup_lift (style : Nat) (s : Task.CacheState) (key : Int) :
    Task.lookupKey style s key = lookupKey style (liftState s) key := by
  unfold Task.lookupKey lookupKey
  have h : ∀ i : Nat,
      (if style == 0 then (Task.getOr s.order i (0,0)).1 == key
       else let n := Task.getOr s.nodes i {}; n.live && n.key == key) =
      (if style == 0 then (getOr (liftState s).order i (0,0)).1 == key
       else let n := getOr (liftState s).nodes i {}; n.live && n.key == key) := by
    intro i
    change (if style == 0 then (Task.getOr s.order i (0,0)).1 == key
        else let n := Task.getOr s.nodes i {}; n.live && n.key == key) =
      (if style == 0 then (Task.getOr s.order i (0,0)).1 == key
        else let n := getOr (s.nodes.map liftNode) i {}; n.live && n.key == key)
    rw [← lookup_node_lift]
    rfl
  simp only [lifted_order, find_congr _ _ _ h]
  rfl

theorem item_lift (style : Nat) (s : Task.CacheState) (id : Int) :
    Task.itemAt style s id = itemAt style (liftState s) id := by
  unfold Task.itemAt itemAt
  rw [← node_lift]
  rfl

theorem set_head_lift (s : Task.CacheState) (head : Int) :
    liftState {s with head := head} = {liftState s with head := head} := rfl

theorem set_tail_lift (s : Task.CacheState) (tail : Int) :
    liftState {s with tail := tail} = {liftState s with tail := tail} := rfl

theorem set_next_lift (n : Task.CacheNode) (next : Int) :
    liftNode {n with next := next} = {liftNode n with next := next} := rfl

theorem set_prev_lift (n : Task.CacheNode) (prev : Int) :
    liftNode {n with prev := prev} = {liftNode n with prev := prev} := rfl

theorem detach_lift (s : Task.CacheState) (id : Int) :
    liftState (Task.detach s id) = detach (liftState s) id := by
  simp only [Task.detach, detach, ← node_lift, lifted_prev, lifted_next]
  have first :
      (if (Task.nodeAt s id).prev < 0 then {liftState s with head := (Task.nodeAt s id).next}
       else setNode (liftState s) (Task.nodeAt s id).prev
          {liftNode (Task.nodeAt s (Task.nodeAt s id).prev) with next := (Task.nodeAt s id).next}) =
      liftState (if (Task.nodeAt s id).prev < 0 then {s with head := (Task.nodeAt s id).next}
        else Task.setNode s (Task.nodeAt s id).prev
          {Task.nodeAt s (Task.nodeAt s id).prev with next := (Task.nodeAt s id).next}) := by
    split <;> simp only [set_head_lift, set_node_lift, set_next_lift]
  simp only [lifted_prev, lifted_next] at first
  rw [first]
  split <;> simp only [← node_lift, ← set_prev_lift, ← set_node_lift, ← set_tail_lift]

theorem link_lift (s : Task.CacheState) (id : Int) :
    liftState (Task.linkFront s id) = linkFront (liftState s) id := by
  simp only [Task.linkFront, linkFront, ← node_lift, lifted_head]
  have updated : ({liftNode (Task.nodeAt s id) with prev := -1, next := s.head}) =
      liftNode {Task.nodeAt s id with prev := -1, next := s.head} := rfl
  simp only [updated, ← set_node_lift]
  by_cases h : s.head < 0
  · simp only [h, if_true, ← set_tail_lift, ← set_head_lift]
  · simp only [h, if_false,
      ← node_lift, ← set_prev_lift, ← set_node_lift, ← set_head_lift]

theorem erase_lift (style : Nat) (s : Task.CacheState) (id : Int) :
    liftState (Task.eraseAt style s id) = eraseAt style (liftState s) id := by
  unfold Task.eraseAt eraseAt
  split
  · rfl
  · simp only [← detach_lift, ← node_lift]
    rw [show ({liftNode (Task.nodeAt (Task.detach s id) id) with live := false}) =
      liftNode {Task.nodeAt (Task.detach s id) id with live := false} from rfl]
    exact set_node_lift _ _ _

theorem touch_lift (style : Nat) (s : Task.CacheState) (id : Int) :
    liftState (Task.touch style s id) = touch style (liftState s) id := by
  unfold Task.touch touch
  split
  · rw [← item_lift]
    rfl
  · rw [← detach_lift, ← link_lift]

theorem value_lift (style : Nat) (s : Task.CacheState) (id value : Int) :
    liftState (Task.setValue style s id value) = setValue style (liftState s) id value := by
  unfold Task.setValue setValue
  split
  · rw [← item_lift]
    rfl
  · rw [← node_lift]
    rw [show ({liftNode (Task.nodeAt s id) with value := value}) =
      liftNode {Task.nodeAt s id with value := value} from rfl]
    exact set_node_lift _ _ _

theorem insert_lift (style : Nat) (s : Task.CacheState) (key value : Int) :
    liftState (Task.insertFront style s key value) = insertFront style (liftState s) key value := by
  unfold Task.insertFront insertFront
  split
  · rfl
  · have h : ∀ i : Nat, (!(Task.getOr s.nodes i {}).live) =
        (!(getOr (liftState s).nodes i {}).live) := by
      intro i
      change (!(Task.getOr s.nodes i {}).live) = (!(getOr (s.nodes.map liftNode) i {}).live)
      rw [← lookup_node_lift]
      rfl
    simp only [← find_congr _ _ _ h, ← node_lift]
    let id := Int.ofNat (((List.range 8).find? (fun i => !(Task.getOr s.nodes i {}).live)).getD 0)
    have updated : ({liftNode (Task.nodeAt s id) with key := key, value := value, live := true}) =
        liftNode {Task.nodeAt s id with key := key, value := value, live := true} := rfl
    rw [updated, ← set_node_lift, ← link_lift]

theorem evict_lift (style : Nat) (s : Task.CacheState) :
    (liftState (Task.evictTail style s).1,(Task.evictTail style s).2) =
    evictTail style (liftState s) := by
  unfold Task.evictTail evictTail
  change (liftState (Task.eraseAt style s _),Task.itemAt style s _) =
    (eraseAt style (liftState s) _,itemAt style (liftState s) _)
  simp only [erase_lift, item_lift, lifted_order, lifted_tail]

def liftPut (r : Task.CacheState × Int × List Task.Item) : CacheState × Int × List Item :=
  (liftState r.1,r.2)

theorem put_lift (style : Nat) (s : Task.CacheState) (key value : Int) :
    liftPut (Task.cachePut style s key value) = cachePut style (liftState s) key value := by
  simp only [Task.cachePut, cachePut, ← lookup_lift, ← size_lift, lifted_cap]
  split
  · simp only [liftPut, ← value_lift, ← touch_lift]
  · split
    · rfl
    · by_cases full : (Task.cacheSize style s == s.cap) = true
      · simp only [full, if_true, ← evict_lift]
        simp only [liftPut, ← insert_lift]
      · simp only [if_neg full, liftPut, ← insert_lift]

def liftQuery (r : Task.CacheState × Int × Int) : CacheState × Int × Int :=
  (liftState r.1,r.2)

theorem query_lift (style : Nat) (s : Task.CacheState) (key : Int) (update : Bool) :
    liftQuery (Task.cacheQuery style s key update) = cacheQuery style (liftState s) key update := by
  simp only [Task.cacheQuery, cacheQuery, ← lookup_lift, ← item_lift]
  split
  · rfl
  · split <;> simp only [liftQuery, ← touch_lift]

def liftItems (r : Task.CacheState × List Task.Item) : CacheState × List Item :=
  (liftState r.1,r.2)

theorem shrink_lift (style fuel : Nat) (s : Task.CacheState) (out : List Task.Item) :
    (Task.shrinkCache style fuel s out).map liftItems = shrinkCache style fuel (liftState s) out := by
  induction fuel generalizing s out with
  | zero =>
    simp only [Task.shrinkCache, shrinkCache, ← size_lift, lifted_cap]
    split <;> rfl
  | succ fuel ih =>
    simp only [Task.shrinkCache, shrinkCache, ← size_lift, lifted_cap]
    split
    · rfl
    · rw [← evict_lift]
      cases Task.evictTail style s
      exact ih _ _

theorem execute_lift (style : Nat) (s : Task.CacheState) (op key value : Int) :
    (Task.executeCache style s op key value).map liftPair =
    executeCache style (liftState s) op key value := by
  unfold Task.executeCache executeCache
  split
  · rw [← put_lift]
    cases Task.cachePut style s key value with
    | mk next result =>
      cases result
      rfl
  · split
    · rw [← query_lift]
      cases Task.cacheQuery style s key (op == 1) with
      | mk next result =>
        cases result
        rfl
    · split
      · simp only [← lookup_lift, ← item_lift, ← erase_lift]
        split <;> rfl
      · have cap_lift :
            {liftState s with cap := key.toNat} = liftState {s with cap := key.toNat} := rfl
        rw [cap_lift]
        rw [← shrink_lift]
        cases Task.shrinkCache style 8 {s with cap := key.toNat} [] with
        | none => rfl
        | some result =>
          cases result
          rfl

theorem view_lift (fuel : Nat) (s : Task.CacheState) (id : Int) :
    Task.linkedView fuel s id = linkedView fuel (liftState s) id := by
  induction fuel generalizing id with
  | zero => simp [Task.linkedView, linkedView]
  | succ fuel ih =>
    simp only [Task.linkedView, linkedView, ← node_lift, lifted_next, lifted_key, lifted_value]
    split
    · rfl
    · rw [← ih (Task.nodeAt s id).next]
      rfl

def taskCommand (style : Nat) (xs : Task.Words) (p : Task.CacheState × Task.Words) (i : Nat) :
    Option (Task.CacheState × Task.Words) := do
  let (next,data) ← Task.executeCache style p.1 (Task.iz xs (2+3*i)) (Task.iz xs (3+3*i)) (Task.iz xs (4+3*i))
  pure (next,p.2++data)

def sourceCommand (style : Nat) (xs : Words) (p : CacheState × Words) (i : Nat) :
    Option (CacheState × Words) := do
  let (next,data) ← executeCache style p.1 (iz xs (2+3*i)) (iz xs (3+3*i)) (iz xs (4+3*i))
  pure (next,p.2++data)

theorem command_lift (style : Nat) (xs : Task.Words) (p : Task.CacheState × Task.Words) (i : Nat) :
    (taskCommand style xs p i).map liftPair = sourceCommand style xs (liftPair p) i := by
  unfold taskCommand sourceCommand
  change _ = (do
    let (next,data) ← executeCache style (liftState p.1) (Task.iz xs (2+3*i))
      (Task.iz xs (3+3*i)) (Task.iz xs (4+3*i))
    pure (next,p.2++data))
  rw [← execute_lift]
  cases Task.executeCache style p.1 (Task.iz xs (2+3*i)) (Task.iz xs (3+3*i)) (Task.iz xs (4+3*i)) with
  | none => rfl
  | some result =>
    cases result
    rfl

theorem commands_lift (style : Nat) (xs : Task.Words) (indices : List Nat)
    (p : Task.CacheState × Task.Words) :
    (indices.foldlM (taskCommand style xs) p).map liftPair =
    indices.foldlM (sourceCommand style xs) (liftPair p) := by
  induction indices generalizing p with
  | nil => rfl
  | cons i rest ih =>
    simp only [List.foldlM_cons, ← command_lift]
    cases taskCommand style xs p i with
    | none => rfl
    | some result => exact ih result

def taskObserve (style : Nat) (p : Task.CacheState × Task.Words) : Option Task.Words := do
  let s := p.1
  let data ← if style == 0 then some (s.order.flatMap (fun (k,v) => [k,v])) else Task.linkedView 8 s s.head
  pure (Task.finish (p.2++[Int.ofNat s.cap,Int.ofNat (Task.cacheSize style s)]++data))

def sourceObserve (style : Nat) (p : CacheState × Words) : Option Words := do
  let s := p.1
  let data ← if style == 0 then some (s.order.flatMap (fun (k,v) => [k,v])) else linkedView 8 s s.head
  pure (finish (p.2++[Int.ofNat s.cap,Int.ofNat (cacheSize style s)]++data))

theorem observe_lift (style : Nat) (p : Task.CacheState × Task.Words) :
    taskObserve style p = sourceObserve style (liftPair p) := by
  simp only [taskObserve, sourceObserve, liftPair, lifted_order, lifted_head, lifted_cap, ← size_lift, ← view_lift]
  rfl

theorem initial_lift (cap : Nat) :
    liftPair (({cap := cap} : Task.CacheState),([] : Task.Words)) = (({cap := cap} : CacheState),[]) := by
  simp [liftPair, liftState, liftNode]
'''


def _task_source(native, domain, raw_native, styles):
    block = raw_native.split('structure CacheNode where', 1)[1].split('def lru (style : Nat)', 1)[0]
    public = [native[name] for name in ('Words', 'Item', 'getOr', 'iz', 'put', 'finish')]
    public.append('structure CacheNode where' + block.rstrip())
    before, body = domain['validB'].split('  match family with', 1)
    if not body.startswith('\n  | 0 =>') or '\n  | _ => ' not in body:
        raise ValueError('Frozen LRU domain dispatcher changed')
    last = body.rsplit('\n  | _ => ', 1)[1]
    first = before.split(':=', 1)[1]
    public += [domain['inRange'], 'def valid (xs : Words) : Prop := (' + first + '  ' + last + ') = true']
    for name, style in zip(('a', 'b'), styles):
        branch = native['lru'].replace('def lru (style : Nat)', 'def ' + name, 1)
        public.append(re.sub(r'\bstyle\b', style, branch))
    # The Task namespace also contains Lean's task monad. Name the Option constructor explicitly.
    declarations = re.sub(r'\bpure\b', 'some', '\n'.join(public))
    return 'import Lean\nnamespace Task\n' + declarations + '''
def equivalent : Prop := ∀ x, valid x → ∃ o, a x=some o ∧ b x=some o
def refutationAt (x oa ob : Words) : Prop := valid x ∧ a x=some oa ∧ b x=some ob ∧ oa≠ob
end Task
'''


def _binding_source(ctx, styles):
    bridge = LRU_BRIDGE
    for name, style in zip(('a', 'b'), styles):
        bridge += f'''
theorem {name}_binding : Task.{name} = entry 2 {style} := by
  funext xs
  let indices := List.range (Task.iz xs 1).toNat
  let initial := (({{cap := (Task.iz xs 0).toNat}} : Task.CacheState),([] : Task.Words))
  change (indices.foldlM (taskCommand {style} xs) initial).bind (taskObserve {style}) =
    (indices.foldlM (sourceCommand {style} xs) (({{cap := (Task.iz xs 0).toNat}} : CacheState),[])).bind
      (sourceObserve {style})
  rw [← initial_lift, ← commands_lift]
  cases indices.foldlM (taskCommand {style} xs) initial with
  | none => rfl
  | some result => exact observe_lift {style} result
'''
    bridge += f'''
theorem domain_binding : Task.valid = valid 2 := by rfl
theorem equivalent_binding : Task.equivalent = SpecLessBenchStatefulSubmission.{ctx['equivalence_goal']} := by
  unfold Task.equivalent SpecLessBenchStatefulSubmission.{ctx['equivalence_goal']} {ctx['equivalence_goal']} Equivalent
  rw [domain_binding, a_binding, b_binding]
theorem refutation_binding (x oa ob : Task.Words) :
    Task.refutationAt x oa ob = SpecLessBenchStatefulSubmission.{ctx['refutation_at_goal']} x oa ob := by
  unfold Task.refutationAt SpecLessBenchStatefulSubmission.{ctx['refutation_at_goal']} {ctx['refutation_at_goal']} RefutationAt
  rw [domain_binding, a_binding, b_binding]
#print axioms a_binding
#print axioms b_binding
#print axioms domain_binding
#print axioms equivalent_binding
#print axioms refutation_binding
'''
    return bridge


def prepare_lru_lean(row, *, package_root, deadline=None):
    """Stage one of the two frozen Lean LRU pairs in an unpublished scratch root."""
    ctx = row['context']
    if ctx.get('tranche') != 'stateful' or ctx.get('family_index') != 2 or ctx.get('domain_index') != 2:
        return None
    package_root = Path(package_root).resolve()
    if package_root == PACKAGES.resolve() or PACKAGES.resolve() in package_root.parents:
        raise ValueError('LRU preparation requires scratch outside the published package tree')
    package = package_root / row['pilot_id'] / 'lean'
    published = PACKAGES / row['pilot_id'] / 'lean' / 'registry.json'
    with idle_preparation():
        if package.exists() or published.exists():
            raise ValueError('LRU package or prior scratch already exists')
        started = time.monotonic()
        source = ROOT / 'benchmarks/tasks/stateful-core/lean'
        paths = {name: source / (name + '.lean') for name in ('StatefulNative', 'StatefulDomain', 'StatefulGoals')}
        paths['StatefulTargets'] = ROOT / 'benchmarks/proof-interface/lean/StatefulTargets.lean'
        raw = {name: path.read_bytes() for name, path in paths.items()}
        text = {name: data.decode('utf-8').replace('\r\n', '\n') for name, data in raw.items()}
        native = lean_declarations(text['StatefulNative'])
        domain = lean_declarations(text['StatefulDomain'])
        goals = lean_declarations(text['StatefulGoals'])
        styles = [re.findall(r'entry\s+2\s+(\d+)', goals[ctx[key]])
                  for key in ('equivalence_goal', 'refutation_at_goal')]
        if styles[0] not in (['0', '1'], ['0', '2']) or styles[1] != styles[0]:
            raise ValueError('Frozen LRU pair or target changed')

        task, frozen, binding = (package / name for name in ('task', 'frozen', 'binding'))
        for folder in (task, frozen, binding):
            folder.mkdir(parents=True, mode=0o700)
        (task / 'Task.lean').write_text(_task_source(native, domain, text['StatefulNative'], styles[0]))
        (task / 'Obligation.lean').write_text(
            'import Task\nnamespace Obligation\ndef goal : Prop := Task.equivalent\nend Obligation\n')
        for name, data in raw.items():
            (frozen / (name + '.lean')).write_bytes(data)
        (binding / 'Binding.lean').write_text(_binding_source(ctx, styles[0]))
        logs = []

        def compile_at(folder, module):
            assert_idle()
            if published.exists():
                raise RuntimeError('Registry appeared during LRU preparation')
            log = compile_lean(folder, module, [task, frozen, binding], deadline=deadline)
            logs.append(log)
            (binding / 'compile.log').write_text('\n'.join(logs))
            return log

        for name in ('Task', 'Obligation'):
            compile_at(task, name)
        for name in paths:
            compile_at(frozen, name)
        audit = compile_at(binding, 'Binding')
        expected = {'a_binding', 'b_binding', 'domain_binding', 'equivalent_binding', 'refutation_binding'}
        allowed = {'propext', 'Classical.choice', 'Quot.sound'}
        audits = re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", audit)
        if len(audits) != len(expected) or {name for name, _ in audits} != expected:
            raise ValueError('Incomplete LRU correspondence axiom audit: ' + audit)
        if any({axiom.strip() for axiom in axioms.split(',') if axiom.strip()} - allowed
               for _, axioms in audits):
            raise ValueError('Unapproved LRU correspondence axiom: ' + audit)
        meta = {
            'pilot_id': row['pilot_id'], 'platform': 'lean', 'public_sha256': tree_digest(task),
            'binding': 'lean-kernel-checked-lru-state-transport-and-exact-frozen-target',
            'source_context': row['source_context_id'], 'source_goal': ctx['equivalence_goal'],
            'frozen_source_sha256': {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()},
            'preparation_wall_seconds': time.monotonic() - started,
            'preparation_controller_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'compiler_costs': 'compile-costs.jsonl', 'preparation_model_tokens': None,
            'final_proof_attempted': False,
        }
        (package / 'registry.pending.json').write_text(json.dumps(meta, indent=2) + '\n')
        return meta
