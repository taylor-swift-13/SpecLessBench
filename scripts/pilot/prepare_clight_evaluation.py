"""Package two frozen Clight programs with their unchanged execution semantics."""
import hashlib
import json
import re
import resource
import time

from prepare_evaluation import ROOT, PACKAGES, COMPCERT, compile_rocq
from single_task_runner import tree_digest


def prepare_compcert(row):
    ctx = row['context']; family = ctx.get('family_index')
    if ctx.get('tranche') != 'algorithms' or family not in (1, 2, 3, 4, 5):
        return None
    package = PACKAGES/row['pilot_id']/'compcert'
    if (package/'registry.json').exists():
        meta = json.loads((package/'registry.json').read_text())
        if tree_digest(package/'task') != meta['public_sha256']:
            raise ValueError('Existing Clight package changed')
        return meta
    if package.exists():
        raise ValueError('Incomplete Clight preparation needs inspection: '+str(package))
    started = time.monotonic(); task = package/'task'; binding = package/'binding'
    task.mkdir(parents=True, mode=0o700); binding.mkdir(mode=0o700)
    source = ROOT/'benchmarks/tasks/algorithms-core/compcert'
    targets = (ROOT/'benchmarks/proof-interface/compcert/BranchTargets.v').read_text()
    def target_definition(name):
        match = re.search(r'^Definition '+re.escape(name)+r'\b.*?(?=\nDefinition |\Z)', targets, re.M | re.S)
        if not match:
            raise ValueError('Missing frozen Clight target')
        return match.group().strip()
    selected = [target_definition(ctx[k]) for k in ('equivalence_goal', 'refutation_at_goal')]
    stem = {1: 'REVERSE', 2: 'SUM', 3: 'MATRIX', 4: 'SEARCH', 5: 'QUEUE'}[family]
    styles = re.findall(r'impl_'+stem+r'_V(\d+)', selected[0])
    if len(styles) != 2 or styles[0] != '0' or styles[1] not in ('1', '2'):
        raise ValueError('Unexpected Clight implementation pair')
    style = int(styles[1]); modules = [stem+'_V0', stem+'_V'+str(style)]
    paths = [(task, 'Trusted'), (binding, 'Frozen')]
    def compile_at(folder, name):
        return compile_rocq(folder, name, paths, toolchain=COMPCERT)
    logs = []; hashes = {}
    def frozen_copy(original, destination):
        hashes[original.relative_to(ROOT).as_posix()] = hashlib.sha256(original.read_bytes()).hexdigest()
        destination.write_bytes(original.read_bytes())
    frozen_copy(source/'Execution.v', task/'Execution.v'); logs.append(compile_at(task, 'Execution'))
    frozen_copy(source/'BasicDomain.v', binding/'BasicDomain.v'); logs.append(compile_at(binding, 'BasicDomain'))
    exports = json.loads((source/'build.json').read_text())['exports']
    for public_name, module in zip(('Left', 'Right'), modules):
        original = source/'ast'/(module+'.v'); frozen_copy(original, binding/original.name)
        ast = original.read_text()
        ast, removed = re.subn(r'^Module Info\..*?^End Info\.\s*', '', ast, flags=re.M | re.S)
        if removed != 1:
            raise ValueError('Expected one non-executable AST metadata module')
        (task/(public_name+'.v')).write_text(ast)
        logs.append(compile_at(task, public_name)); logs.append(compile_at(binding, module))
        cfile = ROOT/'_build/algorithms-v0.3/compcert'/(module+'.c')
        export = next(e for e in exports if e['module'] == module)
        if hashlib.sha256(cfile.read_bytes()).hexdigest() != export['preprocessed_sha256']:
            raise ValueError('Readable C source does not match frozen AST build provenance')
        (task/(public_name+'.c')).write_bytes(cfile.read_bytes())
    native = (PACKAGES/row['pilot_id']/'rocq/task/Task.v').read_text()
    domain = []
    for name in ('words', 'iz', 'in_range', 'valid'):
        match = re.search(r'^Definition '+name+r'\b.*?(?=\n(?:Definition|Fixpoint) |\Z)', native, re.M | re.S)
        if not match:
            raise ValueError('Missing isolated input domain')
        domain.append(match.group().strip())
    text = 'From Stdlib Require Import ZArith List Bool.\nFrom Trusted Require Import Execution Left Right.\nImport ListNotations.\nOpen Scope nat_scope.\n'+'\n'.join(domain)+'''
Definition encode (xs : words) := xs ++ repeat 0%Z (8192-length xs).
Definition left : Execution.implementation := {| Execution.program := Left.prog; Execution.input_symbol := Left._eb_input; Execution.output_symbol := Left._eb_output |}.
Definition right : Execution.implementation := {| Execution.program := Right.prog; Execution.input_symbol := Right._eb_input; Execution.output_symbol := Right._eb_output |}.
Definition equivalent : Prop := Execution.Equivalent valid encode left right.
Definition refutationAt (x : words) (oa ob : Execution.observation) : Prop :=
  valid x /\ Execution.run left (encode x) oa /\ Execution.run right (encode x) ob /\ oa <> ob.
'''
    (task/'Task.v').write_text(text); logs.append(compile_at(task, 'Task'))
    (task/'Obligation.v').write_text('From Trusted Require Import Task.\nDefinition goal : Prop := Task.equivalent.\n')
    logs.append(compile_at(task, 'Obligation'))
    goals = (source/(stem+'Goals.v')).read_text(); records = []
    for module in modules:
        match = re.search(r'Definition impl_'+module+r' : implementation :=\s*\{\|.*?\|\}\.', goals, re.S)
        if not match:
            raise ValueError('Missing frozen implementation record')
        records.append(match.group())
    rebound = '\n'.join(selected)
    for a, b in (('SpecLessBenchAlgorithms.Execution.', 'Execution.'), ('SpecLessBenchAlgorithms.BasicDomain.', 'BasicDomain.'), ('SpecLessBenchAlgorithms.'+stem+'Goals.', '')):
        rebound = rebound.replace(a, b)
    if 'SpecLessBenchAlgorithms.' in rebound:
        raise ValueError('Unresolved original module path')
    (binding/'FrozenTarget.v').write_text('From Stdlib Require Import ZArith List.\nFrom Trusted Require Import Execution.\nFrom Frozen Require Import BasicDomain '+' '.join(modules)+'.\n'+'\n'.join(records)+'\n'+rebound+'\n')
    logs.append(compile_at(binding, 'FrozenTarget'))
    (binding/'ExactTargetBinding.v').write_text(f'''From Trusted Require Import Task Execution.
From Frozen Require Import FrozenTarget.
Example equivalent_binding : Task.equivalent = FrozenTarget.{ctx['equivalence_goal']}. Proof. reflexivity. Qed.
Example refutation_binding (x : Task.words) (oa ob : Execution.observation) : Task.refutationAt x oa ob = FrozenTarget.{ctx['refutation_at_goal']} x oa ob. Proof. reflexivity. Qed.
''')
    logs.append(compile_at(binding, 'ExactTargetBinding')); (binding/'compile.log').write_text('\n'.join(logs))
    meta = {'pilot_id': row['pilot_id'], 'platform': 'compcert', 'public_sha256': tree_digest(task),
            'binding': 'rocq-kernel-checked-exact-Clight-target-under-module-rebinding',
            'semantics': 'Unchanged frozen Execution.v; safety, termination, return and full 8192-word output buffer',
            'source_context': row['source_context_id'], 'source_goal': ctx['equivalence_goal'],
            'frozen_source_sha256': hashes, 'target_source_sha256': hashlib.sha256(targets.encode()).hexdigest(),
            'source_packaging': 'AST library names Left/Right; unused Info metadata omitted; program equality checked by kernel; C bytes checked against frozen build hashes',
            'preparation_wall_seconds': time.monotonic()-started,
            'preparation_controller_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
            'preparation_child_peak_rss_bytes_cumulative': resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024,
            'preparation_model_tokens': None, 'final_proof_attempted': False}
    (package/'registry.json').write_text(json.dumps(meta, indent=2)+'\n')
    return meta
