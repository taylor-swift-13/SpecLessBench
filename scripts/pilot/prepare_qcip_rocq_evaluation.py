"""Stage a Rocq QCIP task and certify its projection from frozen sources.

The public modules project the frozen implementations and domain. The
private reference uses the full original files under the same logical
module names, in a separate Coq load path. Both environments are compiled
and checked independently, and their public declarations are compared
after accounting for any neutralized local binder name. Private binding
proofs relate the raw-word grading interface to the original typed targets.
"""

import hashlib
import json
import os
from pathlib import Path
import re
import resource
import time

from prepare_evaluation import PACKAGES, ROCQ, ROOT, compile_rocq, run_compiler
from prepare_leases_lean_evaluation import assert_idle, idle_preparation
from private_paths import PRIVATE
from single_task_runner import tree_digest
from verify_freeze import frozen_path


SOURCE = Path('benchmarks/tasks/qcip-core')
FROZEN_FILES = {
    'Native': SOURCE / 'rocq_native/Native.v',
    'Domain': SOURCE / 'rocq/Domain.v',
    'Goals': SOURCE / 'rocq_native/Goals.v',
    'BranchTargets': Path('benchmarks/proof-interface/rocq/BranchTargets.v'),
}
FAMILY_MODULES = {'bst': 'BST', 'avl': 'AVL', 'ring': 'Ring', 'dijkstra': 'Dijkstra'}
# Preserve the pretty-printer columns while neutralizing the local name.
LOCAL_BINDER_RENAMES = {'avl': {'mutant': 'choice'}}
AXIOM_AUDITS = ('encode_binding', 'a_binding', 'b_binding', 'domain_binding', 'equivalent_binding',
                'refutation_binding', 'native_target_binding')


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _frozen_inputs(context_row):
    mapping_bytes = (PRIVATE / 'mapping.json').read_bytes()
    manifest = json.loads((ROOT / 'benchmarks/pilot/manifest.json').read_text())
    if _sha(mapping_bytes) != manifest['private_mapping_sha256']:
        raise ValueError('QCIP private mapping does not match frozen manifest')
    mapping = json.loads(mapping_bytes)
    if context_row not in mapping['contexts']:
        raise ValueError('QCIP context does not match frozen private mapping')
    protected = {frozen_path(row['path']): row['sha256'] for row in mapping['protected_files']}
    result = {}
    for name, path in FROZEN_FILES.items():
        data = (ROOT / path).read_bytes()
        if _sha(data) != protected.get(path.as_posix()):
            raise ValueError(f'QCIP frozen source mismatch: {path}')
        result[name] = data
    return result


def _slice(text, start, stop):
    left = text.index('\n' + start) + 1
    right = text.index('\n' + stop, left)
    return text[left:right].rstrip() + '\n'


def _rename_local_binders(text, renames):
    for name, neutral in renames.items():
        text = re.sub(r'\b' + re.escape(name) + r'\b', neutral, text)
    return text


def _project_native(text, family):
    prefix = text[:text.index('Inductive tree')]
    tree = _slice(text, 'Inductive tree', 'Fixpoint insert_bst')
    if family == 'bst':
        body = _slice(text, 'Fixpoint insert_bst', 'Definition rot_l')
        return prefix + tree + body
    if family == 'avl':
        body = _slice(text, 'Definition rot_l', 'Record ring_state')
        return prefix + tree + _rename_local_binders(body, LOCAL_BINDER_RENAMES[family])
    if family == 'ring':
        return prefix + _slice(text, 'Record ring_state', 'Definition item')
    if family == 'dijkstra':
        return prefix + _slice(text, 'Definition item', 'Definition entry')
    raise ValueError(f'Unsupported QCIP family: {family}')


def _project_domain(text, module):
    prefix = text[:text.index('Module BST.')]
    match = re.search(r'^Module ' + module + r'\.$.*?^End ' + module + r'\.$', text, re.M | re.S)
    if match is None:
        raise ValueError(f'QCIP domain module missing: {module}')
    return prefix + match.group() + '\n'


def _goal_declaration(text, name):
    match = re.search(r'^Definition ' + re.escape(name) + r'\b.*?\.(?=\n|\Z)', text, re.M | re.S)
    if match is None:
        raise ValueError(f'QCIP branch declaration missing: {name}')
    return match.group()


def _targets(text, goals, context, family, module):
    eq_name = context['equivalence_goal']
    ref_name = context['refutation_at_goal']
    eq = _goal_declaration(text, eq_name)
    ref = _goal_declaration(text, ref_name)
    calls = re.findall(r'Native\.' + family + r'\s+([0-3])\s+\(Domain\.' + module + r'\.encode x\)', eq)
    if len(calls) != 2 or calls[0] != '0' or calls[1] not in ('1', '2', '3'):
        raise ValueError('Unexpected frozen QCIP implementation pair')
    if re.findall(r'Native\.' + family + r'\s+([0-3])\s+\(Domain\.' + module + r'\.encode x\)', ref) != calls:
        raise ValueError('Frozen QCIP branches use different implementation pairs')
    if f'Domain.{module}.valid' not in eq or f'Domain.{module}.valid x' not in ref:
        raise ValueError('Frozen QCIP branches use a different domain')
    original_name = context['context_id'].replace('-', '_')
    pattern = r'^Theorem ' + re.escape(original_name) + r'\s*:\s*(.*?)\.\s*\nAbort\.'
    original = re.search(pattern, goals, re.M | re.S)
    if original is None:
        raise ValueError('Frozen native QCIP goal declaration missing')
    native_body = original.group(1)
    native_calls = re.findall(r'\b' + family + r'\s+([0-3])\s+\(' + module + r'\.encode x\)', native_body)
    if native_calls != calls or f'{module}.valid' not in native_body:
        raise ValueError('Native QCIP goal and grading branches disagree')
    if not native_body.startswith(('Equivalent ', 'Counterexample ')):
        raise ValueError('Unexpected native QCIP goal shape')
    target = ('From Coq Require Import ZArith List.\n'
              'From Trusted Require Import Domain Native.\n'
              f'{eq}\n{ref}\nDefinition native_goal : Prop := {native_body}.\n')
    return target, calls[1], native_body.startswith('Counterexample ')


def _task_source(family, module, style, domain):
    encoder = re.search(r'^Definition encode \(x : input\) : list Z := pack\s+\((.*?)\)\.$',
                        domain, re.M | re.S)
    if encoder is None:
        raise ValueError('Frozen QCIP input encoder is missing its outer pack')
    names = _declaration_names(domain.split('Module ' + module + '.', 1)[1])
    payload = re.sub(r'\b\w+\b', lambda m: f'Domain.{module}.{m[0]}' if m[0] in names else m[0],
                     encoder[1])
    payload = re.sub(r'\b(?:encode_kv|pad)\b', lambda m: f'Domain.{m[0]}', payload)
    return f'''From Coq Require Import ZArith List.
From Trusted Require Import Domain Native.
Import ListNotations.
Definition words := list Z.
Definition payload (x : Domain.{module}.input) : words := {payload}.
Definition valid (raw : words) : Prop :=
  exists x : Domain.{module}.input, Domain.{module}.valid x /\\ raw = payload x.
Definition a (raw : words) : option words := Native.{family} 0%nat (Domain.pack raw).
Definition b (raw : words) : option words := Native.{family} {style}%nat (Domain.pack raw).
Definition equivalent : Prop := forall raw, valid raw -> exists out, a raw = Some out /\\ b raw = Some out.
Definition refutationAt (raw oa ob : words) : Prop :=
  valid raw /\\ a raw = Some oa /\\ b raw = Some ob /\\ oa <> ob.
'''


def _binding_source(context, family, module, style, negative):
    text = f'''From Coq Require Import ZArith List.
From Trusted Require Import Domain Native Task Obligation.
From Binding Require Import FrozenTarget.

Lemma encode_binding x : Domain.pack (Task.payload x) = Domain.{module}.encode x.
Proof. reflexivity. Qed.
Lemma a_binding x : Task.a (Task.payload x) = Native.{family} 0%nat (Domain.{module}.encode x).
Proof. reflexivity. Qed.
Lemma b_binding x : Task.b (Task.payload x) = Native.{family} {style}%nat (Domain.{module}.encode x).
Proof. reflexivity. Qed.
Lemma domain_binding raw : Task.valid raw <->
  exists x : Domain.{module}.input, Domain.{module}.valid x /\\ raw = Task.payload x.
Proof. reflexivity. Qed.

Lemma equivalent_binding : Obligation.goal <-> FrozenTarget.{context['equivalence_goal']}.
Proof.
  unfold Obligation.goal, Task.equivalent, FrozenTarget.{context['equivalence_goal']}, Native.Equivalent.
  split.
  - intros H x Hvalid. specialize (H (Task.payload x)).
    assert (V : Task.valid (Task.payload x)) by (exists x; split; [exact Hvalid|reflexivity]).
    destruct (H V) as [out [Ha Hb]]. exists out. split.
    + rewrite <- a_binding. exact Ha.
    + rewrite <- b_binding. exact Hb.
  - intros H raw Hvalid. apply domain_binding in Hvalid.
    destruct Hvalid as [x [Hx Hraw]]. subst raw.
    destruct (H x Hx) as [out [Ha Hb]]. exists out. split.
    + rewrite a_binding. exact Ha.
    + rewrite b_binding. exact Hb.
Qed.

Lemma refutation_binding raw oa ob : Task.refutationAt raw oa ob <->
  exists x : Domain.{module}.input, raw = Task.payload x /\\ FrozenTarget.{context['refutation_at_goal']} x oa ob.
Proof.
  unfold Task.refutationAt, FrozenTarget.{context['refutation_at_goal']}.
  split.
  - intros [V [Ha [Hb Hneq]]]. apply domain_binding in V.
    destruct V as [x [Hx Hraw]]. subst raw.
    exists x. split; [reflexivity|].
    split; [exact Hx|].
    split; [exact Ha|].
    split; assumption.
  - intros [x [Hraw [V [Ha [Hb Hneq]]]]]. subst raw.
    split.
    + apply domain_binding. exists x. split; [exact V|reflexivity].
    + exact (conj Ha (conj Hb Hneq)).
Qed.
'''
    if negative:
        text += f'''
Lemma native_target_binding : (exists raw oa ob, Task.refutationAt raw oa ob) <-> FrozenTarget.native_goal.
Proof.
  unfold FrozenTarget.native_goal, Native.Counterexample.
  split.
  - intros [raw [oa [ob H]]]. apply refutation_binding in H.
    destruct H as [x [_ H]]. exists x, oa, ob. exact H.
  - intros [x [oa [ob H]]]. exists (Task.payload x), oa, ob.
    apply refutation_binding. exists x. split; [reflexivity|exact H].
Qed.
'''
    else:
        text += '\nLemma native_target_binding : Obligation.goal <-> FrozenTarget.native_goal.\nProof. exact equivalent_binding. Qed.\n'
    return text + '\n'.join(f'Print Assumptions {name}.' for name in AXIOM_AUDITS) + '\n'


def _declaration_names(source):
    names = re.findall(r'^(?:Definition|Fixpoint|Record|Inductive)\s+(\w+)', source, re.M)
    for body in re.findall(r'^Record\s+\w+\s*:=\s*\{([^}]*)\}', source, re.M | re.S):
        names.extend(re.findall(r'(?:^|;)\s*(\w+)\s*:', body))
    return names


def _projection_check_source(native, domain, module):
    names = [f'Trusted.Native.{name}' for name in _declaration_names(native)]
    common, body = domain.split('Module ' + module + '.', 1)
    names += [f'Trusted.Domain.{name}' for name in _declaration_names(common)]
    names += [f'Trusted.Domain.{module}.{name}' for name in _declaration_names(body)]
    names += ['Trusted.Task.' + name for name in ('words', 'payload', 'valid', 'a', 'b', 'equivalent', 'refutationAt')]
    names += ['Trusted.Obligation.goal']
    source = ('From Trusted Require Domain Native Task Obligation.\n'
              'Set Printing All.\nSet Printing Depth 100000.\nSet Printing Width 100000.\n')
    return source + ''.join(f'Print {name}.\n' for name in names), names


def _check_projection(public_print, reference_print, renames):
    if '...' in public_print or '...' in reference_print:
        raise ValueError('QCIP declaration comparison contains a truncated term')
    if not public_print or public_print != _rename_local_binders(reference_print, renames):
        raise ValueError('QCIP public declarations differ from the full frozen reference')


def _coqchk(folder, label, paths, module, deadline):
    argv = [str(ROCQ / 'bin/coqchk'), '-silent']
    for path, logical in paths:
        argv += ['-Q', str(path), logical]
    assert_idle()
    return run_compiler(folder, label, argv + [module],
                        dict(os.environ, OCAMLFIND_CONF=str(ROCQ / 'lib/findlib.conf'),
                             OCAMLPATH=str(ROCQ / 'lib')), timeout=180, deadline=deadline)


def prepare_qcip_rocq(row, *, package_root, deadline=None):
    """Compile one private QCIP package and leave its registry pending."""
    context = row['context']
    if context.get('tranche') != 'qcip':
        return None
    family = context['family']
    module = FAMILY_MODULES[family]
    package_root = Path(package_root).resolve()
    if package_root == PACKAGES.resolve() or PACKAGES.resolve() in package_root.parents:
        raise ValueError('QCIP preparation requires scratch outside published packages')
    package = package_root / row['pilot_id'] / 'rocq'
    published = PACKAGES / row['pilot_id'] / 'rocq' / 'registry.json'

    with idle_preparation():
        if package.exists() or published.exists():
            raise ValueError('QCIP package or scratch directory already exists')
        started = time.monotonic()
        frozen = _frozen_inputs(row)
        text = {name: data.decode('utf-8').replace('\r\n', '\n') for name, data in frozen.items()}
        targets, style, negative = _targets(text['BranchTargets'], text['Goals'], context, family, module)
        public_native = _project_native(text['Native'], family)
        public_domain = _project_domain(text['Domain'], module)
        task_text = _task_source(family, module, style, public_domain)
        obligation = 'From Trusted Require Import Task.\nDefinition goal : Prop := Task.equivalent.\n'
        task = package / 'task'
        public_build = package / 'public-build'
        reference = package / 'reference'
        binding = package / 'binding'
        audit = package / 'public-audit'
        for directory in (task, public_build, reference, binding, audit):
            directory.mkdir(parents=True, mode=0o700)
        (public_build / 'Native.v').write_text(public_native)
        (public_build / 'Domain.v').write_text(public_domain)
        for folder in (public_build, reference):
            (folder / 'Task.v').write_text(task_text)
            (folder / 'Obligation.v').write_text(obligation)
        for name, data in frozen.items():
            (reference / f'{name}.v').write_bytes(data)
        (binding / 'FrozenTarget.v').write_text(targets)
        (binding / 'Binding.v').write_text(_binding_source(context, family, module, style, negative))
        projection, names = _projection_check_source(public_native, public_domain, module)
        for folder in (audit, binding):
            (folder / 'Projection.v').write_text(projection)
        logs = []

        def compile_at(folder, name, paths):
            assert_idle()
            if published.exists():
                raise RuntimeError('QCIP registry appeared during preparation')
            result = compile_rocq(folder, name, paths, deadline=deadline)
            logs.append(f'[{folder.name}/{name}]\n{result}')
            (binding / 'compile.log').write_text('\n'.join(logs))
            return result

        public_paths = [(public_build, 'Trusted'), (audit, 'Audit')]
        reference_paths = [(reference, 'Trusted'), (binding, 'Binding')]
        for folder, paths in ((public_build, public_paths), (reference, reference_paths)):
            for name in ('Native', 'Domain', 'Task', 'Obligation'):
                compile_at(folder, name, paths)
        public_print = compile_at(audit, 'Projection', public_paths)
        reference_print = compile_at(binding, 'Projection', reference_paths)
        (binding / 'public-declarations.txt').write_text(public_print)
        (binding / 'reference-declarations.txt').write_text(reference_print)
        renames = LOCAL_BINDER_RENAMES.get(family, {})
        _check_projection(public_print, reference_print, renames)
        compile_at(binding, 'FrozenTarget', reference_paths)
        assumptions = compile_at(binding, 'Binding', reference_paths)
        if (assumptions.count('Closed under the global context') != len(AXIOM_AUDITS)
                or 'Axioms:' in assumptions):
            raise ValueError('QCIP binding assumptions are not closed: ' + assumptions)
        for name in ('Native', 'Domain', 'Task', 'Obligation'):
            for suffix in ('.v', '.vo'):
                (public_build / (name + suffix)).replace(task / (name + suffix))
        for paths, name, label in (([(task, 'Trusted')], 'Trusted.Obligation', 'public-coqchk'),
                                   (reference_paths, 'Binding.Binding', 'binding-coqchk')):
            logs.append(f'[{label}]\n' + _coqchk(binding, label, paths, name, deadline))
            (binding / 'compile.log').write_text('\n'.join(logs))
        assert_idle()
        meta = {
            'pilot_id': row['pilot_id'], 'platform': 'rocq', 'public_sha256': tree_digest(task),
            'binding': 'rocq-kernel-checked-qcip-exact-source-projection-and-typed-encoding-image',
            'source_context': row['source_context_id'], 'source_goal': context['equivalence_goal'],
            'source_refutation_goal': context['refutation_at_goal'],
            'frozen_source_sha256': {name: _sha(data) for name, data in frozen.items()},
            'declaration_comparison': {'count': len(names), 'names': names,
                                       'printing_depth': 100000,
                                       'reference_local_binder_renames': renames,
                                       'public_and_reference_sha256': _sha(public_print.encode())},
            'binding_audits': list(AXIOM_AUDITS), 'independent_coqchk': ['Trusted.Obligation', 'Binding.Binding'],
            'preparation_wall_seconds': time.monotonic() - started,
            'preparation_controller_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'compiler_costs': 'compile-costs.jsonl', 'preparation_model_tokens': None,
            'final_proof_attempted': False,
        }
        (package / 'registry.pending.json').write_text(json.dumps(meta, indent=2) + '\n')
        return meta
