"""Isolate one frozen counting-sort pair and certify its native Rocq target."""
import hashlib
import json
import re
import resource
import time

from prepare_evaluation import ROOT, PACKAGES, compile_rocq
from prepare_classics_evaluation import declarations
from single_task_runner import tree_digest


def prepare_countsort_rocq(row):
    ctx = row['context']
    if ctx.get('tranche') != 'countsort':
        return None
    package = PACKAGES / row['pilot_id'] / 'rocq'
    if (package / 'registry.json').exists():
        meta = json.loads((package / 'registry.json').read_text())
        if tree_digest(package / 'task') != meta['public_sha256']:
            raise ValueError('Existing counting-sort package changed')
        return meta
    if package.exists():
        raise ValueError('Incomplete preparation requires inspection: ' + str(package))
    started = time.monotonic()
    source = ROOT / 'benchmarks/tasks/countsort-core/rocq'
    native = declarations((source / 'CountSortNative.v').read_text())
    domains = declarations((source / 'CountSortDomain.v').read_text())
    goals = declarations((source / 'CountSortGoals.v').read_text())
    selected = [goals[ctx[k]] for k in ('equivalence_goal', 'refutation_at_goal')]
    styles = re.findall(r'CountSortNative.entry\s+0\s+(\d+)', selected[0])
    if styles not in (['0', '1'], ['0', '2']):
        raise ValueError('Unexpected frozen counting-sort pair')
    pair = []
    for name, style in zip(('a', 'b'), styles):
        text = native['entry'].replace('Definition entry (_family style:nat)', 'Definition ' + name, 1)
        expression = ('fold_left(fun acc x=>insert_record x acc)items[]' if name == 'a'
                      else 'counting items ' + ('true' if style == '2' else 'false'))
        text, count = re.subn(r'if Nat.eqb style 0 then fold_left\(fun acc x=>insert_record x acc\)items\[\] else counting items\(Nat.eqb style 2\)', expression + ' ', text)
        if count != 1 or re.search(r'\b(?:style|_family)\b', text):
            raise ValueError('Unexpected implementation dispatcher')
        pair.append(text)
    valid = 'Definition valid xs : Prop := (' + domains['validb'].split(':=', 1)[1].strip()[:-1].replace('Nat.eqb domain 0', 'Nat.eqb 0 0') + ') = true.'
    task = package / 'task'
    binding = package / 'binding'
    task.mkdir(parents=True, mode=0o700)
    binding.mkdir(mode=0o700)
    header = 'From Coq Require Import ZArith List Bool.\nImport ListNotations.\nOpen Scope nat_scope.\n'
    names = [n for n in native if n not in ('entry', 'Equivalent', 'RefutationAt')]
    public = header + '\n'.join([native[n] for n in names] + [domains['between'], valid, *pair]) + '''
Definition equivalent : Prop := forall x, valid x -> exists o, a x=Some o /\ b x=Some o.
Definition refutationAt (x oa ob:words) : Prop := valid x /\ a x=Some oa /\ b x=Some ob /\ oa<>ob.
'''
    (task / 'Task.v').write_text(public)
    (task / 'Obligation.v').write_text('From Trusted Require Import Task.\nDefinition goal : Prop := Task.equivalent.\n')
    original = ROOT / '_build/pilot-v1/countsort-rocq-binding'
    original.mkdir(parents=True, exist_ok=True)
    paths = [(task, 'Trusted'), (binding, 'Binding'), (original, 'Frozen')]
    def compile_at(folder, name):
        return compile_rocq(folder, name, paths)
    logs = [compile_at(task, n) for n in ('Task', 'Obligation')]
    for name in ('CountSortNative', 'CountSortDomain'):
        src = source / (name + '.v')
        dest = original / src.name
        if not dest.exists() or dest.read_bytes() != src.read_bytes() or not (original / (name + '.vo')).exists():
            dest.write_bytes(src.read_bytes())
            logs.append(compile_at(original, name))
    (binding / 'FrozenTarget.v').write_text('From Frozen Require Import CountSortNative CountSortDomain.\n' + '\n'.join(selected) + '\n')
    logs.append(compile_at(binding, 'FrozenTarget'))
    bridge = header + 'From Trusted Require Import Task.\nFrom Frozen Require Import CountSortNative CountSortDomain.\nFrom Binding Require Import FrozenTarget.\n'
    for name, style in zip(('a', 'b'), styles):
        bridge += f'Example {name}_binding : Task.{name} = CountSortNative.entry 0 {style}. Proof. reflexivity. Qed.\n'
    bridge += f'''Example domain_binding : Task.valid = CountSortDomain.valid 0. Proof. reflexivity. Qed.
Example equivalent_binding : Task.equivalent = FrozenTarget.{ctx['equivalence_goal']}. Proof. reflexivity. Qed.
Example refutation_binding (x oa ob:Task.words) : Task.refutationAt x oa ob = FrozenTarget.{ctx['refutation_at_goal']} x oa ob. Proof. reflexivity. Qed.
Print Assumptions equivalent_binding.
Print Assumptions refutation_binding.
'''
    (binding / 'Binding.v').write_text(bridge)
    logs.append(compile_at(binding, 'Binding'))
    (binding / 'compile.log').write_text('\n'.join(logs))
    meta = {'pilot_id': row['pilot_id'], 'platform': 'rocq', 'public_sha256': tree_digest(task),
            'binding': 'rocq-kernel-checked-exact-frozen-target-for-both-branches',
            'source_context': row['source_context_id'], 'source_goal': ctx['equivalence_goal'],
            'frozen_source_sha256': {n: hashlib.sha256((source / (n + '.v')).read_bytes()).hexdigest()
                                     for n in ('CountSortNative', 'CountSortDomain', 'CountSortGoals')},
            'preparation_wall_seconds': time.monotonic() - started,
            'preparation_controller_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'compiler_costs': 'compile-costs.jsonl', 'preparation_model_tokens': None,
            'final_proof_attempted': False}
    (package / 'registry.json').write_text(json.dumps(meta, indent=2) + '\n')
    return meta
