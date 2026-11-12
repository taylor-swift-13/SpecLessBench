"""Prepare a single Lean QCIP family slice and replay its exact frozen targets."""

import hashlib
import json
import re
import resource
import time
from pathlib import Path

from prepare_classics_evaluation import lean_declarations
from prepare_evaluation import PACKAGES, ROOT, compile_lean
from prepare_leases_lean_evaluation import assert_idle, idle_preparation
from single_task_runner import tree_digest


FAMILY_NAMES = {'bst': 'BST', 'avl': 'AVL', 'ring': 'Ring', 'dijkstra': 'Dijkstra'}
OBLIGATION = '''import Task
namespace Obligation
def goal : Prop := Task.equivalent
end Obligation
'''

# The two environments use the same Lean toolchain, module names and constant
# names. Compare the actual kernel declarations rather than the source text
# alone: this detects a difference in elaboration after slicing a module.
# Lean's BEq Expr uses Expr.eqv, which ignores bound variable names.
REPLAY_AUDIT = '''import Lean
open Lean

-- In the whole module, the matcher cache reuses the BST loop's natural-number
-- match in the AVL loop. The AVL-only module gives that exact matcher its own
-- name. The replay checks the aliased declaration and all of its references.
def frozenName (name : Name) : Name :=
  if name == `SpecLessBench.avlLoop.match_1 then `SpecLessBench.bstLoop.match_1 else name

def frozenExpr (expression : Expr) : Expr :=
  expression.replace fun
    | .const name levels =>
      if frozenName name == name then none else some (.const (frozenName name) levels)
    | _ => none

def sameKernelDeclaration : ConstantInfo → ConstantInfo → Bool
  | .axiomInfo _, _ => false
  | .defnInfo a, .defnInfo b =>
      { a with
        name := frozenName a.name
        type := frozenExpr a.type
        value := frozenExpr a.value
        all := a.all.map frozenName } == b
  | .thmInfo a, .thmInfo b =>
      { a with
        name := frozenName a.name
        type := frozenExpr a.type
        value := frozenExpr a.value
        all := a.all.map frozenName } == b
  | .opaqueInfo a, .opaqueInfo b =>
      { a with
        name := frozenName a.name
        type := frozenExpr a.type
        value := frozenExpr a.value
        all := a.all.map frozenName } == b
  | .inductInfo a, .inductInfo b =>
      a.toConstantVal == b.toConstantVal &&
      a.numParams == b.numParams && a.numIndices == b.numIndices &&
      a.all == b.all && a.ctors == b.ctors && a.numNested == b.numNested &&
      a.isRec == b.isRec && a.isUnsafe == b.isUnsafe && a.isReflexive == b.isReflexive
  | .ctorInfo a, .ctorInfo b => a == b
  | .recInfo a, .recInfo b => a == b
  | _, _ => false

def importedFrom (env : Environment) (name : Name) : Option Name := do
  let idx ← env.getModuleIdxFor? name
  env.allImportedModuleNames[idx.toNat]?

def auditReplay (task frozen : System.FilePath) : IO Unit := do
  let original ← searchPathRef.get
  try
    searchPathRef.set (task :: original)
    let publicEnv ← importModules #[{ module := `Task }] {}
    searchPathRef.set (frozen :: original)
    let frozenEnv ← importModules #[{ module := `Task }] {}
    let modules := [`Native, `Domain, `Task]
    for moduleName in modules do
      let mut count := 0
      for (name, decl) in publicEnv.constants.toList do
        if importedFrom publicEnv name == some moduleName then
          let originalName := frozenName name
          if name != originalName && (publicEnv.find? originalName).isSome then
            throw <| IO.userError s!"Conflicting public declaration names: {name} and {originalName}"
          let some originalDecl := frozenEnv.find? originalName
            | throw <| IO.userError s!"Missing frozen declaration: {name}"
          if importedFrom frozenEnv originalName != some moduleName ||
             !sameKernelDeclaration decl originalDecl then
            throw <| IO.userError s!"Kernel declaration mismatch: {name}"
          count := count + 1
      if count == 0 then
        throw <| IO.userError s!"No declarations compared: {moduleName}"
      IO.println s!"QCIP kernel replay matched {moduleName}: {count}"
  finally
    searchPathRef.set original
'''


def between(text, first, last):
    if text.count(first) != 1 or text.count(last) != 1:
        raise ValueError('Unexpected frozen Lean source boundary')
    return text.split(first, 1)[1].split(last, 1)[0]


def public_sources(native, domain, family):
    common = between(native, 'namespace SpecLessBench\n', '\ninductive Tree where')
    tree = '\ninductive Tree where' + between(native, '\ninductive Tree where', '\ndef insertBST ')
    if family == 'bst':
        body = tree + '\ndef insertBST ' + between(native, '\ndef insertBST ', '\ndef rotL ')
    elif family == 'avl':
        body = tree + '\ndef rotL ' + between(native, '\ndef rotL ', '\nstructure RingState where')
        body, replacements = re.subn(r'\bmutant\b', 'mode', body)
        if replacements != 6:
            raise ValueError('Unexpected frozen AVL rotation parameter names')
    elif family == 'ring':
        body = '\nstructure RingState where' + between(native, '\nstructure RingState where', '\nabbrev Item ')
    else:
        body = '\nabbrev Item ' + between(native, '\nabbrev Item ', '\ndef entry ')
    family_name = FAMILY_NAMES[family]
    start = f'namespace {family_name}\n'
    end = f'end {family_name}\n'
    family_domain = between(domain, start, end)
    return {
        'Native': 'import Lean\nnamespace SpecLessBench\n' + common + body + '\nend SpecLessBench\n',
        'Domain': 'import Native\nnamespace SpecLessBench\n' + start + family_domain + end + 'end SpecLessBench\n',
    }, family_domain


def task_source(family, family_domain, style):
    family_name = FAMILY_NAMES[family]
    encode = lean_declarations(family_domain)['encode']
    header = 'def encode (x : Input) : Words := pad 8192'
    if not encode.startswith(header):
        raise ValueError('Unexpected frozen QCIP encoding')
    payload = encode[len(header):].strip()
    return f'''import Domain

namespace SpecLessBench.{family_name}
def encodePayload (x : Input) : Words := {payload}
end SpecLessBench.{family_name}

namespace Task
abbrev Words := SpecLessBench.Words
def valid (xs : Words) : Prop :=
  ∃ x : SpecLessBench.{family_name}.Input,
    SpecLessBench.{family_name}.valid x ∧ SpecLessBench.{family_name}.encodePayload x = xs
def a (xs : Words) : Option Words := SpecLessBench.{family} 0 (SpecLessBench.pad 8192 xs)
def b (xs : Words) : Option Words := SpecLessBench.{family} {style} (SpecLessBench.pad 8192 xs)
def equivalent : Prop := ∀ x, valid x → ∃ o, a x = some o ∧ b x = some o
def refutationAt (x oa ob : Words) : Prop :=
  valid x ∧ a x = some oa ∧ b x = some ob ∧ oa ≠ ob
end Task
'''


def binding_source(ctx, family, style):
    family_name = FAMILY_NAMES[family]
    equiv = ctx['equivalence_goal']
    refute = ctx['refutation_at_goal']
    return f'''import Task
import BranchTargets
open SpecLessBench

theorem encoding_binding (x : {family_name}.Input) :
    pad 8192 ({family_name}.encodePayload x) = {family_name}.encode x := rfl
theorem a_binding (x : {family_name}.Input) :
    Task.a ({family_name}.encodePayload x) = {family} 0 ({family_name}.encode x) := rfl
theorem b_binding (x : {family_name}.Input) :
    Task.b ({family_name}.encodePayload x) = {family} {style} ({family_name}.encode x) := rfl

theorem equivalent_binding : Task.equivalent ↔ SpecLessBenchSubmission.{equiv} := by
  unfold Task.equivalent SpecLessBenchSubmission.{equiv} Equivalent
  constructor
  · intro h x hx
    exact h ({family_name}.encodePayload x) ⟨x, hx, rfl⟩
  · rintro h xs ⟨x, hx, rfl⟩
    exact h x hx

theorem refutation_binding (xs oa ob : Task.Words) :
    Task.refutationAt xs oa ob ↔ ∃ x : {family_name}.Input,
      {family_name}.encodePayload x = xs ∧ SpecLessBenchSubmission.{refute} x oa ob := by
  unfold Task.refutationAt SpecLessBenchSubmission.{refute}
  constructor
  · rintro ⟨⟨x, hx, rfl⟩, ha, hb, hne⟩
    exact ⟨x, rfl, hx, ha, hb, hne⟩
  · rintro ⟨x, rfl, hx, ha, hb, hne⟩
    exact ⟨⟨x, hx, rfl⟩, ha, hb, hne⟩

#print axioms encoding_binding
#print axioms a_binding
#print axioms b_binding
#print axioms equivalent_binding
#print axioms refutation_binding
'''


def prepare_qcip_lean(row, *, package_root, deadline=None):
    """Check one pair in private scratch and leave its registry pending."""
    ctx = row['context']
    if ctx.get('tranche') != 'qcip':
        return None
    family = ctx['family']
    package_root = Path(package_root).resolve()
    if package_root == PACKAGES.resolve() or PACKAGES.resolve() in package_root.parents:
        raise ValueError('QCIP preparation requires scratch outside the published package tree')
    package = package_root / row['pilot_id'] / 'lean'
    published = PACKAGES / row['pilot_id'] / 'lean' / 'registry.json'
    with idle_preparation():
        if package.exists() or published.exists():
            raise ValueError('QCIP package or prior scratch already exists')
        started = time.monotonic()
        source = ROOT / 'benchmarks/tasks/qcip-core/lean'
        basic = ROOT / 'benchmarks/tasks/algorithms-core/lean'
        source_paths = {
            'Native': source / 'Native.lean',
            'Domain': source / 'Domain.lean',
            'BasicNative': basic / 'BasicNative.lean',
            'BasicDomain': basic / 'BasicDomain.lean',
            'BranchTargets': ROOT / 'benchmarks/proof-interface/lean/BranchTargets.lean',
        }
        raw = {name: path.read_bytes() for name, path in source_paths.items()}
        text = {name: data.decode('utf-8').replace('\r\n', '\n') for name, data in raw.items()}
        targets = lean_declarations(text['BranchTargets'])
        styles = [re.findall(rf'SpecLessBench\.{family} ([0-9]+) \(SpecLessBench\.{FAMILY_NAMES[family]}\.encode x\)',
                             targets[ctx[key]]) for key in ('equivalence_goal', 'refutation_at_goal')]
        if styles[0] not in (['0', '1'], ['0', '2'], ['0', '3']) or styles[1] != styles[0]:
            raise ValueError('Unexpected frozen QCIP target pair')
        style = styles[0][1]
        public, family_domain = public_sources(text['Native'], text['Domain'], family)
        task = package / 'task'
        frozen = package / 'frozen'
        binding = package / 'binding'
        for folder in (task, frozen, binding):
            folder.mkdir(parents=True, mode=0o700)
        public['Task'] = task_source(family, family_domain, style)
        public['Obligation'] = OBLIGATION
        for name, code in public.items():
            if re.search(r'\bmutant\b|\bC_(?:AVL|BST|DIJK|RING)_', code, re.I):
                raise ValueError('Outcome label in public QCIP source')
            (task / (name + '.lean')).write_text(code)
        for name, data in raw.items():
            (frozen / (name + '.lean')).write_bytes(data)
        (frozen / 'Task.lean').write_bytes((task / 'Task.lean').read_bytes())
        (binding / 'Binding.lean').write_text(binding_source(ctx, family, style))
        (binding / 'ReplayAudit.lean').write_text(
            REPLAY_AUDIT + '\n#eval auditReplay ' + json.dumps(str(task)) + ' ' + json.dumps(str(frozen)) + '\n'
        )

        logs = []

        def compile_at(folder, name, paths):
            assert_idle()
            if published.exists():
                raise RuntimeError('QCIP registry appeared during preparation')
            output = compile_lean(folder, name, paths, deadline=deadline)
            logs.append(output)
            (binding / 'compile.log').write_text('\n'.join(logs))
            return output

        for name in public:
            compile_at(task, name, [task])
        for name in (*source_paths, 'Task'):
            compile_at(frozen, name, [frozen])
        replay = compile_at(binding, 'ReplayAudit', [binding])
        if set(re.findall(r'QCIP kernel replay matched (\w+): [1-9][0-9]*', replay)) != {'Native', 'Domain', 'Task'}:
            raise ValueError('Incomplete QCIP kernel replay audit')
        audit = compile_at(binding, 'Binding', [frozen, binding])
        expected = {'encoding_binding', 'a_binding', 'b_binding', 'equivalent_binding', 'refutation_binding'}
        checks = re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", audit)
        if len(checks) != len(expected) or {name for name, _ in checks} != expected:
            raise ValueError('Incomplete QCIP binding axiom audit')
        allowed = {'propext', 'Classical.choice', 'Quot.sound'}
        if any({axiom.strip() for axiom in axioms.split(',') if axiom.strip()} - allowed for _, axioms in checks):
            raise ValueError('Unapproved QCIP binding axiom')
        meta = {
            'pilot_id': row['pilot_id'], 'platform': 'lean', 'public_sha256': tree_digest(task),
            'binding': 'lean-kernel-replayed-qcip-encoding-image-and-exact-frozen-target',
            'source_context': row['source_context_id'], 'source_goal': ctx['equivalence_goal'],
            'frozen_source_sha256': {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()},
            'preparation_wall_seconds': time.monotonic() - started,
            'preparation_controller_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'compiler_costs': 'compile-costs.jsonl', 'preparation_model_tokens': None,
            'final_proof_attempted': False,
        }
        (package / 'registry.pending.json').write_text(json.dumps(meta, indent=2) + '\n')
        return meta
