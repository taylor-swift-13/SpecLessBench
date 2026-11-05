"""Isolate the two selected classical implementations and their input domain."""
import hashlib
import json
import re
import resource
import time

from prepare_evaluation import ROOT, PACKAGES, compile_rocq
from single_task_runner import tree_digest


def declarations(text):
    return {m.group(1): m.group().strip() for m in re.finditer(
        r'^(?:Definition|Fixpoint)\s+([A-Za-z_][A-Za-z_0-9]*)\b.*?(?=\n(?:Definition|Fixpoint|Notation)\b|\Z)', text, re.M | re.S)}


def implementation(defs, family, style, name):
    source = defs['forest' if family == 0 else 'sorting']
    source = re.sub(r'^Definition\s+(?:forest|sorting)\s+style\s+xs', 'Definition '+name+' xs', source, count=1)
    if family == 0:
        pattern = r'if Nat\.eqb style 1 then prim n edges else kruskal\(Nat\.eqb style 2\)n edges'
        expression = 'prim n edges' if style == 1 else 'kruskal '+('true' if style == 2 else 'false')+' n edges'
        source, count = re.subn(pattern, expression, source)
    else:
        pattern = r'if Nat\.eqb style 0 then (.*?)\s+else if Nat\.eqb style 1 then merge_sort 8 items else selection_sort 64 items'
        source, count = re.subn(pattern, lambda m: m.group(1) if style == 0 else ('merge_sort 8 items' if style == 1 else 'selection_sort 64 items'), source, flags=re.S)
    if count != 1 or re.search(r'\bstyle\b', source):
        raise ValueError('Unexpected frozen implementation dispatcher')
    return source


def prepare_classics(row):
    ctx = row['context']
    if ctx.get('tranche') != 'classics':
        return None
    package = PACKAGES/row['pilot_id']/'rocq'
    if (package/'registry.json').exists():
        meta = json.loads((package/'registry.json').read_text())
        if tree_digest(package/'task') != meta['public_sha256']:
            raise ValueError('Existing classical task changed')
        return meta
    if package.exists():
        raise ValueError('Incomplete preparation requires inspection: '+str(package))
    started = time.monotonic(); task = package/'task'; binding = package/'binding'
    task.mkdir(parents=True, mode=0o700); binding.mkdir(mode=0o700)
    source = ROOT/'benchmarks/tasks/classics-core/rocq'
    native = declarations((source/'ClassicsNative.v').read_text())
    domains = declarations((source/'ClassicsDomain.v').read_text())
    goals = declarations((source/'ClassicsGoals.v').read_text())
    selected = [goals[ctx[key]] for key in ('equivalence_goal', 'refutation_at_goal')]
    family = ctx['family_index']; domain = ctx['domain_index']
    styles = re.findall(r'ClassicsNative.entry\s+'+str(family)+r'\s+(\d+)', selected[0])
    if len(styles) != 2 or styles[0] != '0' or styles[1] not in ('1', '2') or not re.search(r'ClassicsDomain.valid\s+'+str(domain)+r'\b', selected[0]):
        raise ValueError('Frozen goal differs from selected pair/domain')
    pair = [implementation(native, family, int(style), name) for name, style in zip(('a', 'b'), styles)]
    body = domains['validb'].split(':=', 1)[1].strip()[:-1]
    branches = re.fullmatch(r'\s*if Nat\.eqb domain 2 then (.*?)\n else (.*)', body, re.S)
    if not branches:
        raise ValueError('Unexpected frozen domain dispatcher')
    valid = 'Definition valid (xs : words) : Prop := ('+re.sub(r'\bdomain\b', str(domain), branches.group(1 if domain == 2 else 2))+') = true.'
    available = dict(native); available['between'] = domains['between']
    needed = set(); todo = [*pair, valid]
    while todo:
        text = todo.pop()
        dependencies = set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b', text))
        if 'let*' in text:
            dependencies.add('obind')
        for name in dependencies & available.keys():
            if name not in needed:
                needed.add(name); todo.append(available[name])
    if needed & {'entry', 'forest', 'sorting', 'Equivalent', 'RefutationAt'}:
        raise ValueError('Projection includes an unrelated dispatcher or goal')
    parts = []
    for name, declaration in available.items():
        if name in needed:
            parts.append(declaration)
            if name == 'obind':
                parts.append('Notation "\'let*\' x \':=\' c \'in\' b" := (obind c (fun x=>b)) (at level 200,x ident,c at level 100,b at level 200).')
    text = 'From Coq Require Import ZArith List Bool.\nImport ListNotations.\nOpen Scope nat_scope.\n'+'\n'.join(parts+[valid, *pair])+'''
Definition equivalent : Prop := forall x, valid x -> exists o, a x = Some o /\ b x = Some o.
Definition refutationAt (x oa ob : words) : Prop := valid x /\ a x = Some oa /\ b x = Some ob /\ oa <> ob.
'''
    (task/'Task.v').write_text(text)
    (task/'Obligation.v').write_text('From Trusted Require Import Task.\nDefinition goal : Prop := Task.equivalent.\n')
    paths = [(task, 'Trusted'), (binding, 'Binding')]
    logs = [compile_rocq(task, name, paths) for name in ('Task', 'Obligation')]
    original = ROOT/'_build/pilot-v1/classics-rocq-binding'; original.mkdir(parents=True, exist_ok=True)
    for name in ('ClassicsNative', 'ClassicsDomain'):
        frozen = source/(name+'.v'); target = original/frozen.name
        if not target.exists() or target.read_bytes() != frozen.read_bytes() or not (original/(name+'.vo')).exists():
            target.write_bytes(frozen.read_bytes()); logs.append(compile_rocq(original, name, [(original, 'Frozen')]))
    paths.append((original, 'Frozen'))
    (binding/'FrozenTarget.v').write_text('From Frozen Require Import ClassicsNative ClassicsDomain.\n'+'\n'.join(selected)+'\n')
    logs.append(compile_rocq(binding, 'FrozenTarget', paths))
    # Relate helper functions before applying their bounded fuel constants.
    # Direct conversion of merge 128 can otherwise unfold an exponential tree.
    bridge = 'From Coq Require Import ZArith List Bool.\nImport ListNotations.\nOpen Scope nat_scope.\nFrom Trusted Require Import Task.\nFrom Frozen Require Import ClassicsNative ClassicsDomain.\nFrom Binding Require Import FrozenTarget.\n'
    helpers = []
    for name, declaration in available.items():
        if name not in needed or name in ('words', 'edge', 'record'):
            continue
        owner = 'ClassicsDomain' if name == 'between' else 'ClassicsNative'
        dependencies = set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b', declaration))
        if 'let*' in declaration:
            dependencies.add('obind')
        rewrites = ''.join('try rewrite clone_'+dep+'.\n' for dep in helpers if dep in dependencies)
        bridge += f'Time Lemma clone_{name} : @Task.{name} = @{owner}.{name}.\nProof. unfold Task.{name}, {owner}.{name}.\n'+rewrites+'reflexivity. Qed.\n'
        helpers.append(name)
    for name in ('kruskal', 'prim', 'insert_record', 'merge_sort', 'selection_sort'):
        if name in needed:
            bridge += f'Opaque Task.{name} ClassicsNative.{name}.\n'
    bridge += 'Local Notation "\'let*\' x \':=\' c \'in\' b" := (Task.obind c (fun x=>b)) (at level 200,x ident,c at level 100,b at level 200).\n'
    for name, style, root in zip(('a', 'b'), styles, pair):
        algorithm = ('prim' if int(style) == 1 else 'kruskal') if family == 0 else {0: 'insert_record', 1: 'merge_sort', 2: 'selection_sort'}[int(style)]
        body = root.split(':=', 1)[1].strip()[:-1]
        def qualify(match):
            token = match.group()
            return 'sl_impl_fn' if token == algorithm else ('Task.'+token if token in native else token)
        context = re.sub(r'\b[A-Za-z_][A-Za-z_0-9]*\b', qualify, body)
        bridge += f'''Lemma bind_{name} : Task.{name} = ClassicsNative.entry {family} {style}.
Proof. let sl_type := type of Task.{algorithm} in
exact (@f_equal sl_type (Task.words -> option Task.words)
 (fun (sl_impl_fn : sl_type) => fun (xs : Task.words) => {context})
 Task.{algorithm} ClassicsNative.{algorithm} clone_{algorithm}). Qed.
'''
    bridge += f'''Lemma bind_valid : Task.valid = ClassicsDomain.valid {domain}.
Proof. reflexivity. Qed.
Lemma source_congruence3 {{A B C D : Type}} (f : A -> B -> C -> D)
  {{a a' : A}} {{b b' : B}} {{c c' : C}} (ha : a=a') (hb : b=b') (hc : c=c') :
  f a b c = f a' b' c'.
Proof. destruct ha, hb, hc. reflexivity. Qed.
Example equivalent_binding : Task.equivalent = FrozenTarget.{ctx['equivalence_goal']}.
Proof. exact (@source_congruence3 _ _ _ Prop ClassicsNative.Equivalent
 Task.valid (ClassicsDomain.valid {domain}) Task.a (ClassicsNative.entry {family} {styles[0]}) Task.b (ClassicsNative.entry {family} {styles[1]}) bind_valid bind_a bind_b). Qed.
Example refutation_binding (x oa ob : Task.words) : Task.refutationAt x oa ob = FrozenTarget.{ctx['refutation_at_goal']} x oa ob.
Proof. exact (@source_congruence3 _ _ _ Prop (fun v a b => ClassicsNative.RefutationAt v a b x oa ob)
 Task.valid (ClassicsDomain.valid {domain}) Task.a (ClassicsNative.entry {family} {styles[0]}) Task.b (ClassicsNative.entry {family} {styles[1]}) bind_valid bind_a bind_b). Qed.
'''
    (binding/'ExactTargetBinding.v').write_text(bridge)
    logs.append(compile_rocq(binding, 'ExactTargetBinding', paths)); (binding/'compile.log').write_text('\n'.join(logs))
    meta = {'pilot_id': row['pilot_id'], 'platform': 'rocq', 'public_sha256': tree_digest(task),
            'binding': 'rocq-kernel-checked-exact-target-for-both-branches',
            'source_context': row['source_context_id'], 'source_goal': ctx['equivalence_goal'],
            'frozen_source_sha256': {n: hashlib.sha256((source/n).read_bytes()).hexdigest() for n in ('ClassicsNative.v', 'ClassicsDomain.v', 'ClassicsGoals.v')},
            'projection': 'Only selected pair, fixed domain and transitive declaration dependencies; dispatchers specialized before closure',
            'preparation_wall_seconds': time.monotonic()-started,
            'preparation_controller_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
            'compiler_costs': 'compile-costs.jsonl', 'preparation_model_tokens': None, 'final_proof_attempted': False}
    (package/'registry.json').write_text(json.dumps(meta, indent=2)+'\n')
    return meta
