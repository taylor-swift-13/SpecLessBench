"""Minimal quoted-tokenizer package; transport its private record representation."""
import hashlib
import json
import re
import resource
import time

from prepare_evaluation import ROOT, PACKAGES, compile_rocq
from prepare_classics_evaluation import declarations
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
