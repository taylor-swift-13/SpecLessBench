"""Isolate frozen Lean lease tables and certify their representation transport.

Preparation is serialized with the evaluator and leaves registry publication to
an explicit caller decision. Failed scratch directories are never removed.
"""
import contextlib
import fcntl
import hashlib
import json
from pathlib import Path
import re
import resource
import time

from prepare_evaluation import ROOT, PACKAGES, compile_lean
from prepare_classics_evaluation import lean_declarations
from single_task_runner import tree_digest


def assert_idle():
    """Do not overlap even the start of a queued evaluation."""
    for status in (PACKAGES.parent / 'batches').glob('*/status.json'):
        state = json.loads(status.read_text())
        if any(job['status'] == 'running' for job in state['jobs']):
            raise RuntimeError('Evaluation is running: ' + str(status))
        if state.get('ready_runs', 0):
            raise RuntimeError('Evaluation packages are ready: ' + str(status))
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():
            continue
        try:
            args = (proc / 'cmdline').read_bytes().decode(errors='replace').split('\0')
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
        if '/opt/goal_client.py' in args or (
                any(arg.endswith('/resource_supervisor.py') for arg in args)
                and any('/runs/evaluation/' in arg for arg in args)):
            raise RuntimeError('Evaluation descendant is live: ' + proc.name)


@contextlib.contextmanager
def idle_preparation():
    PACKAGES.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (PACKAGES / 'activity.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert_idle()
        yield
        assert_idle()


LEASE_BRIDGE = '''import Task
import SystemsGoals
open SpecLessBenchSystems
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000
set_option backward.isDefEq.respectTransparency false

def liftLease (item : Task.Lease) : Lease := ⟨item.live,item.value,item.deadline⟩
def liftTable (s : Task.LeaseTable) : LeaseTable := ⟨s.clock,s.entries.map liftLease,s.wheel⟩
def liftPair (p : Task.LeaseTable × Task.Words) : LeaseTable × Words := (liftTable p.1,p.2)

theorem get_lift (es : List Task.Lease) (key : Nat) :
  liftLease (Task.getOr es key {}) = getOr (es.map liftLease) key {} := by
  induction es generalizing key with
  | nil => rfl
  | cons item es ih => cases key with
    | zero => rfl
    | succ key => exact ih key

theorem replace_lift (es : List Task.Lease) (key : Nat) (item : Task.Lease) :
  (Task.replaceAt es key item).map liftLease = replaceAt (es.map liftLease) key (liftLease item) := by
  simp [Task.replaceAt, replaceAt]

theorem lease_lift (s : Task.LeaseTable) (key : Nat) :
  liftLease (Task.leaseAt s key) = leaseAt (liftTable s) key := by
  exact get_lift s.entries key

theorem clear_lift (style : Nat) (s : Task.LeaseTable) (key : Nat) :
  liftTable (Task.clearLease style s key) = clearLease style (liftTable s) key := by
  unfold Task.clearLease clearLease
  rw [← lease_lift]
  dsimp only [liftLease, liftTable]
  rw [replace_lift]
  rfl

theorem set_lift (style : Nat) (s : Task.LeaseTable) (key : Nat) (value : Int) (ttl : Nat) :
  liftTable (Task.setLease style s key value ttl) = setLease style (liftTable s) key value ttl := by
  unfold Task.setLease setLease
  rw [← clear_lift]
  split <;> dsimp only [liftTable]
  all_goals rw [replace_lift]
  all_goals rfl

theorem clock_lift (s : Task.LeaseTable) : (liftTable s).clock = s.clock := by rfl
theorem wheel_lift (s : Task.LeaseTable) : (liftTable s).wheel = s.wheel := by rfl
theorem wheel_update_lift (s : Task.LeaseTable) (wheel : Task.Words) :
  liftTable {s with wheel := wheel} = {liftTable s with wheel := wheel} := by rfl

def taskExpireCommand (style : Nat) (p : Task.LeaseTable × Task.Words) (key : Nat) :=
  let (table,out) := p
  let old := Task.leaseAt table key
  let idx := Task.wheelIndex table.clock key
  let due := if style == 0 then old.deadline == table.clock else Task.word table.wheel idx == 1
  let next := if style == 0 then table else {table with wheel := Task.replaceAt table.wheel idx 0}
  if due && old.live == 1 then (Task.clearLease style next key,out++[Int.ofNat key])
  else (next,out)

def sourceExpireCommand (style : Nat) (p : LeaseTable × Words) (key : Nat) :=
  let (table,out) := p
  let old := leaseAt table key
  let idx := wheelIndex table.clock key
  let due := if style == 0 then old.deadline == table.clock else word table.wheel idx == 1
  let next := if style == 0 then table else {table with wheel := replaceAt table.wheel idx 0}
  if due && old.live == 1 then (clearLease style next key,out++[Int.ofNat key])
  else (next,out)

theorem expire_command_lift (style : Nat) (p : Task.LeaseTable × Task.Words) (key : Nat) :
  liftPair (taskExpireCommand style p key) = sourceExpireCommand style (liftPair p) key := by
  cases p with
  | mk s out =>
    unfold taskExpireCommand sourceExpireCommand
    dsimp only [liftPair]
    rw [← lease_lift]
    simp only [liftLease, clock_lift, wheel_lift, show word = Task.word from rfl,
      show wheelIndex = Task.wheelIndex from rfl,
      show @replaceAt Int = @Task.replaceAt Int from rfl, ← wheel_update_lift]
    split <;> split <;> dsimp only [liftPair]
    all_goals try rw [clear_lift]
    all_goals rfl

theorem expire_commands_lift (style : Nat) (ids : List Nat) (p : Task.LeaseTable × Task.Words) :
  liftPair (ids.foldl (taskExpireCommand style) p) = ids.foldl (sourceExpireCommand style) (liftPair p) := by
  induction ids generalizing p with
  | nil => rfl
  | cons key ids ih => simpa only [List.foldl_cons, expire_command_lift] using ih (taskExpireCommand style p key)

theorem expire_lift (style : Nat) (s : Task.LeaseTable) (keys : Task.Words) :
  liftPair (Task.expireAtTick style s keys) = expireAtTick style (liftTable s) keys := by
  exact expire_commands_lift style Task.nodes ({s with clock := s.clock+1},keys)

theorem advance_commands_lift (style : Nat) (ids : List Nat) (p : Task.LeaseTable × Task.Words) :
  liftPair (ids.foldl (fun (table,keys) _ => Task.expireAtTick style table keys) p) =
  ids.foldl (fun (table,keys) _ => expireAtTick style table keys) (liftPair p) := by
  induction ids generalizing p with
  | nil => rfl
  | cons key ids ih =>
    cases p with
    | mk s keys =>
      simp only [List.foldl_cons]
      change liftPair (ids.foldl (fun (table,keys) _ => Task.expireAtTick style table keys)
        (Task.expireAtTick style s keys)) =
        ids.foldl (fun (table,keys) _ => expireAtTick style table keys)
        (expireAtTick style (liftTable s) keys)
      rw [← expire_lift]
      exact ih (Task.expireAtTick style s keys)

theorem advance_lift (style : Nat) (s : Task.LeaseTable) (ticks : Nat) :
  liftPair (Task.advanceClock style s ticks) = advanceClock style (liftTable s) ticks := by
  exact advance_commands_lift style (List.range ticks) (s,[])

theorem step_lift (style : Nat) (s : Task.LeaseTable) (op : Int) (a : Nat) (value : Int) (ttl : Nat) :
  liftPair (Task.leaseStep style s op a value ttl) = leaseStep style (liftTable s) op a value ttl := by
  unfold Task.leaseStep leaseStep
  split
  · exact congrArg (fun t => (t,[op,0,0,0])) (set_lift style s a value ttl)
  · split
    · rw [← advance_lift]
      cases Task.advanceClock style s a
      rfl
    · rw [← lease_lift]
      split <;> dsimp only [liftPair, liftLease]
      all_goals first | rw [clear_lift] | rfl

def taskCommand (style : Nat) (p : Task.LeaseTable × Task.Words) (cmd : Int × Nat × Int × Nat) :=
  let (s,out) := p
  let (op,a,b,c) := cmd
  let (next,obs) := Task.leaseStep style s op a b c
  (next,out++obs)

def sourceCommand (style : Nat) (p : LeaseTable × Words) (cmd : Int × Nat × Int × Nat) :=
  let (s,out) := p
  let (op,a,b,c) := cmd
  let (next,obs) := leaseStep style s op a b c
  (next,out++obs)

theorem command_lift (style : Nat) (p : Task.LeaseTable × Task.Words) (cmd : Int × Nat × Int × Nat) :
  liftPair (taskCommand style p cmd) = sourceCommand style (liftPair p) cmd := by
  cases p with
  | mk s out =>
    rcases cmd with ⟨op,a,b,c⟩
    unfold taskCommand sourceCommand
    dsimp only [liftPair]
    rw [← step_lift]
    cases Task.leaseStep style s op a b c
    rfl

theorem commands_lift (style : Nat) (cmds : List (Int × Nat × Int × Nat)) (p : Task.LeaseTable × Task.Words) :
  liftPair (cmds.foldl (taskCommand style) p) = cmds.foldl (sourceCommand style) (liftPair p) := by
  induction cmds generalizing p with
  | nil => rfl
  | cons cmd cmds ih => simpa only [List.foldl_cons, command_lift] using ih (taskCommand style p cmd)

def taskObserve (s : Task.LeaseTable) (out : Task.Words) :=
  Task.finish (out++[Int.ofNat s.clock]++Task.nodes.flatMap (fun key =>
    let item := Task.leaseAt s key
    [item.live,item.value]))

def sourceObserve (s : LeaseTable) (out : Words) :=
  finish (out++[Int.ofNat s.clock]++nodes.flatMap (fun key =>
    let item := leaseAt s key
    [item.live,item.value]))

theorem observe_lift (s : Task.LeaseTable) (out : Task.Words) :
  taskObserve s out = sourceObserve (liftTable s) out := by
  unfold taskObserve sourceObserve
  have view : Task.nodes.flatMap (fun key => [(Task.leaseAt s key).live,(Task.leaseAt s key).value]) =
      nodes.flatMap (fun key => [(leaseAt (liftTable s) key).live,(leaseAt (liftTable s) key).value]) := by
    apply congrArg (fun f : Nat → List Int => nodes.flatMap f)
    funext key
    rw [← lease_lift]
    rfl
  rw [view]
  rfl
'''


def _prepare(row, package):
    ctx = row['context']
    final = PACKAGES / row['pilot_id'] / 'lean' / 'registry.json'
    if final.exists() or (package / 'registry.json').exists():
        raise ValueError('Lease registry already exists; inspect before preparation')
    if package.exists():
        raise ValueError('Incomplete preparation requires inspection: ' + str(package))
    started = time.monotonic()
    source = ROOT / 'benchmarks/tasks/systems-core/lean'
    source_bytes = {name: (source / (name + '.lean')).read_bytes()
                    for name in ('SystemsNative', 'SystemsDomain', 'SystemsGoals')}
    raw = source_bytes['SystemsNative'].decode().replace('\r\n', '\n')
    native = lean_declarations(raw)
    domains = lean_declarations(source_bytes['SystemsDomain'].decode().replace('\r\n', '\n'))
    goals = lean_declarations(source_bytes['SystemsGoals'].decode().replace('\r\n', '\n'))
    selected = [goals[ctx[k]] for k in ('equivalence_goal', 'refutation_at_goal')]
    styles = re.findall(r'entry\s+2\s+(\d+)', selected[0])
    if styles not in (['0', '1'], ['0', '2']) or ctx.get('domain_index') != 2:
        raise ValueError('Unexpected frozen lease pair/domain')
    if re.findall(r'entry\s+2\s+(\d+)', selected[1]) != styles:
        raise ValueError('Frozen lease targets disagree')
    records = raw.split('structure Lease where', 1)[1].split('def leaseAt', 1)[0]
    names = list(native)
    helpers = names[names.index('leaseAt'):names.index('leases')]
    pair = [re.sub(r'\bstyle\b', style, native['leases'].replace('def leases (style : Nat)', 'def ' + name, 1))
            for name, style in zip(('a', 'b'), styles)]
    valid_command = 'def validCommand (op a b c : Int) : Bool :=\n' + domains['validCommand'].rsplit('\n  else\n', 1)[1]
    prefix = domains['validFamilyB'].split(':=', 1)[1].split('  if family == 3 then', 1)[0]
    body = domains['validFamilyB'].rsplit('\n  else\n', 1)[1].replace('validCommand family', 'validCommand')
    body = re.sub(r'^  ', '', body, flags=re.M)
    valid = 'def valid (xs : Words) : Prop := (' + prefix + body + ') = true\n'
    task = package / 'task'; binding = package / 'binding'; original = package / 'frozen'
    for path in (task, binding, original):
        path.mkdir(parents=True, mode=0o700)
    (task / 'Task.lean').write_text('import Lean\nnamespace Task\n' + '\n'.join(
        [native[n] for n in ('Words', 'getOr', 'word', 'replaceAt', 'finish', 'commands', 'nodes', 'zeroes')] +
        ['structure Lease where' + records] + [native[n] for n in helpers] +
        [domains['between'], valid_command, valid, *pair]) + '''
def equivalent : Prop := ∀ x, valid x → ∃ o, a x=some o ∧ b x=some o
def refutationAt (x oa ob : Words) : Prop := valid x ∧ a x=some oa ∧ b x=some ob ∧ oa≠ob
end Task
''')
    (task / 'Obligation.lean').write_text('import Task\nnamespace Obligation\ndef goal : Prop := Task.equivalent\nend Obligation\n')
    logs = []
    def compile_at(folder, name):
        assert_idle()
        if final.exists():
            raise RuntimeError('Registry appeared during lease preparation')
        log = compile_lean(folder, name, [task, original, binding])
        logs.append(log)
        (binding / 'compile.log').write_text('\n'.join(logs))
        assert_idle()
        return log
    for name in ('Task', 'Obligation'):
        compile_at(task, name)
    for name in ('SystemsNative', 'SystemsDomain', 'SystemsGoals'):
        (original / (name + '.lean')).write_bytes(source_bytes[name])
        compile_at(original, name)
    bridge = LEASE_BRIDGE
    for name, style in zip(('a', 'b'), styles):
        bridge += f'''theorem {name}_binding : Task.{name} = entry 2 {style} := by
  funext input
  change taskObserve ((Task.commands input).foldl (taskCommand {style}) ({{}},[])).1
      ((Task.commands input).foldl (taskCommand {style}) ({{}},[])).2 =
    sourceObserve ((Task.commands input).foldl (sourceCommand {style}) ({{}},[])).1
      ((Task.commands input).foldl (sourceCommand {style}) ({{}},[])).2
  have h := commands_lift {style} (Task.commands input) ({{}},[])
  have initial : liftPair ({{}},([] : Task.Words)) = (({{}} : LeaseTable),[]) := by
    simp [liftPair, liftTable, liftLease, Task.zeroes, zeroes]
  rw [initial] at h
  rw [← h]
  cases (Task.commands input).foldl (taskCommand {style}) ({{}},[])
  exact observe_lift _ _
'''
    bridge += f'''theorem domain_binding : Task.valid = valid 2 := by rfl
theorem equivalent_binding : Task.equivalent = {ctx['equivalence_goal']} := by
  unfold Task.equivalent {ctx['equivalence_goal']} Equivalent
  rw [domain_binding, a_binding, b_binding]
theorem refutation_binding (x oa ob : Task.Words) : Task.refutationAt x oa ob = {ctx['refutation_at_goal']} x oa ob := by
  unfold Task.refutationAt {ctx['refutation_at_goal']} RefutationAt
  rw [domain_binding, a_binding, b_binding]
#print axioms a_binding
#print axioms b_binding
#print axioms domain_binding
#print axioms equivalent_binding
#print axioms refutation_binding
'''
    (binding / 'Binding.lean').write_text(bridge)
    audit_log = compile_at(binding, 'Binding')
    allowed = {'propext', 'Classical.choice', 'Quot.sound'}
    audits = re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", audit_log)
    expected = {'a_binding', 'b_binding', 'domain_binding', 'equivalent_binding', 'refutation_binding'}
    if {name for name, _ in audits} != expected or len(audits) != len(expected):
        raise ValueError('Incomplete lease axiom audit: ' + audit_log)
    for name, axioms in audits:
        if {a.strip() for a in axioms.split(',') if a.strip()} - allowed:
            raise ValueError('Unapproved lease correspondence axiom: ' + name)
    if re.search(r'\b(?:sorry|axiom|native_decide)\b', bridge):
        raise ValueError('Unapproved proof construct')
    meta = {'pilot_id': row['pilot_id'], 'platform': 'lean', 'public_sha256': tree_digest(task),
            'binding': 'lean-kernel-checked-lease-table-transport-and-exact-frozen-target',
            'source_context': row['source_context_id'], 'source_goal': ctx['equivalence_goal'],
            'frozen_source_sha256': {n: hashlib.sha256(data).hexdigest() for n, data in source_bytes.items()},
            'preparation_wall_seconds': time.monotonic() - started,
            'preparation_controller_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'compiler_costs': 'compile-costs.jsonl', 'preparation_model_tokens': None,
            'final_proof_attempted': False}
    (package / 'registry.pending.json').write_text(json.dumps(meta, indent=2) + '\n')
    return meta


def prepare_leases_lean(row, *, package_root=None):
    """Prepare one systems family2 pair with registry publication always deferred.

    ``package_root`` selects an unpublished private preparation root for review.
    This entry point owns the activity lock; callers must not already hold it.
    """
    ctx = row['context']
    if ctx.get('tranche') != 'systems' or ctx.get('family_index') != 2:
        return None
    package = (Path(package_root) if package_root is not None else PACKAGES) / row['pilot_id'] / 'lean'
    with idle_preparation():
        return _prepare(row, package)
