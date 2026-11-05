"""Isolate frozen word-vector programs and check both source target bindings."""
import hashlib
import json
import re
import resource
import time

from prepare_evaluation import ROOT, PACKAGES, compile_rocq, compile_lean
from prepare_classics_evaluation import declarations, lean_declarations
from single_task_runner import tree_digest


def prepare_word_rocq(row):
    ctx = row['context']
    boundary=ctx.get('tranche')=='boundaries' and ctx.get('family_index') in (4,6)
    if ctx.get('tranche') != 'graphsuite' and not boundary:
        return None
    package = PACKAGES/row['pilot_id']/'rocq'
    if (package/'registry.json').exists():
        meta = json.loads((package/'registry.json').read_text())
        if tree_digest(package/'task') != meta['public_sha256']:
            raise ValueError('Existing graph/search task changed')
        return meta
    if package.exists():
        raise ValueError('Incomplete graph/search preparation needs inspection: '+str(package))
    started = time.monotonic();task = package/'task';binding = package/'binding'
    task.mkdir(parents=True,mode=0o700);binding.mkdir(mode=0o700)
    prefix='Boundary' if boundary else 'GraphSuite'
    source = ROOT/'benchmarks/tasks'/('boundaries-core' if boundary else 'graphsuite-core')/'rocq'
    native = declarations(re.sub(r'\(\*.*?\*\)', '', (source/(prefix+'Native.v')).read_text(), flags=re.S))
    domain = declarations((source/(prefix+'Domain.v')).read_text())
    goals = declarations((source/(prefix+'Goals.v')).read_text())
    selected = [goals[ctx[k]] for k in ('equivalence_goal','refutation_at_goal')]
    family = ctx['family_index'];index = ctx['domain_index'];root = ({4:'tlv',6:'packbits'}[family] if boundary else ('apsp','scc','search')[family])
    styles = re.findall(prefix+r'Native.entry\s+'+str(family)+r'\s+(\d+)',selected[0])
    if len(styles)!=2 or styles[0]!='0' or styles[1] not in ('1','2') or not re.search(prefix+r'Domain.valid\s+'+str(index)+r'\b',selected[0]):
        raise ValueError('Unexpected frozen graph/search pair or domain')
    pair=[];algorithms=[]
    for name,style in zip(('a','b'),map(int,styles)):
        text=native[root].replace('Definition '+root+' style xs','Definition '+name+' xs',1)
        if boundary:
            stem='tlv' if family==4 else 'pack'
            algorithm=stem+('_suffix' if style==1 else '_indexed')
            expression=(stem+'_suffix false 128 data 0 0[]' if style==1 else stem+'_indexed '+('true' if style==2 else 'false')+' data 128 0 0[]') if family==4 else (stem+'_suffix false cap 128 data 0[]' if style==1 else stem+'_indexed '+('true' if style==2 else 'false')+' cap data 128 0[]')
            pattern=r'if Nat.eqb style 1 then tlv_suffix false 128 data 0 0\[\]else tlv_indexed\(Nat.eqb style 2\)data 128 0 0\[\]' if family==4 else r'if Nat.eqb style 1 then pack_suffix false cap 128 data 0\[\]else pack_indexed\(Nat.eqb style 2\)cap data 128 0\[\]'
            text,count=re.subn(pattern,expression+' ',text)
        elif family==0:
            algorithm='floyd' if style==0 else 'dijkstra_one'
            expression='floyd n xs' if style==0 else 'flat_map(dijkstra_one n xs '+('true' if style==2 else 'false')+')(seq 0 n)'
            text,count=re.subn(r'if Nat.eqb style 0 then floyd n xs else flat_map\(dijkstra_one n xs\(Nat.eqb style 2\)\)\(seq 0 n\)',expression+' ',text)
        elif family==1:
            algorithm='tarjan' if style==0 else 'kosaraju'
            expression='tarjan n xs' if style==0 else 'kosaraju n xs '+('true' if style==2 else 'false')
            text,count=re.subn(r'if Nat.eqb style 0 then tarjan n xs else kosaraju n xs\(Nat.eqb style 2\)',expression+' ',text)
        else:
            algorithm='brute' if style==0 else 'bm_loop'
            expression='brute text pattern' if style==0 else 'if Nat.eqb m 0 then 0%Z else bm_loop 49 0 text pattern '+('true' if style==2 else 'false')
            text,count=re.subn(r'if Nat.eqb style 0 then brute text pattern else if Nat.eqb m 0 then 0%Z else bm_loop 49 0 text pattern\(Nat.eqb style 2\)',expression+' ',text)
        if count!=1 or re.search(r'\bstyle\b',text):raise ValueError('Unexpected implementation dispatcher')
        pair.append(text);algorithms.append(algorithm)
    if boundary:
        pre,match=domain['validb'].split(':=',1)[1].split('match domain with',1)
        clauses=re.findall(r'\n  \| (.*?)=>(.*?)(?=\n  \| |\n  end\.)',match,re.S)
        choices=[body for pattern,body in clauses if pattern.count('S')==index and pattern.strip()!='_']
        if len(choices)!=1:raise ValueError('Missing isolated codec input domain')
        valid='Definition valid (xs:words) : Prop := ('+pre+choices[0]+')=true.'
    else:
        branches=re.fullmatch(r'\s*if Nat.eqb domain 0\|\|Nat.eqb domain 1 then\s*(.*?)\n else if Nat.eqb domain 2 then (.*?)\n else false\.',domain['validb'].split(':=',1)[1],re.S)
        if not branches:raise ValueError('Unexpected graph/search domain dispatcher')
        valid='Definition valid (xs:words) : Prop := ('+re.sub(r'\bdomain\b',str(index),branches.group(1 if index in (0,1) else 2))+')=true.'
    available=dict(native);extra=('get','in_range') if boundary else ('between',)
    available.update({n:domain[n] for n in extra});needed=set();todo=[*pair,valid]
    while todo:
        text=todo.pop();deps=set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b',text))
        if 'let*' in text:deps.add('obind')
        for name in deps & available.keys():
            if name not in needed:needed.add(name);todo.append(available[name])
    if needed & {'entry','apsp','scc','search','tree','unionfind','priority','evaluator','tlv','quotes','packbits','path','Equivalent','RefutationAt'}:raise ValueError('Unrelated dispatcher in dependency closure')
    notation='Notation "\'let*\' x \':=\' c \'in\' b" := (obind c (fun x=>b)) (at level 200,x ident,c at level 100,b at level 200).'
    parts=[]
    for name,d in available.items():
        if name in needed:
            parts.append(d)
            if name=='obind':parts.append(notation)
    public='From Coq Require Import ZArith List Bool.\nImport ListNotations.\nOpen Scope nat_scope.\n'+'\n'.join(parts+[valid,*pair])+'''
Definition equivalent : Prop := forall x, valid x -> exists o, a x=Some o /\ b x=Some o.
Definition refutationAt (x oa ob:words) : Prop := valid x /\ a x=Some oa /\ b x=Some ob /\ oa<>ob.
'''
    public=re.sub(r'\bmutant\b','mode',public)
    (task/'Task.v').write_text(public);(task/'Obligation.v').write_text('From Trusted Require Import Task.\nDefinition goal:Prop:=Task.equivalent.\n')
    original=ROOT/('_build/pilot-v1/'+prefix.lower()+'-rocq-binding');original.mkdir(parents=True,exist_ok=True)
    paths=[(task,'Trusted'),(binding,'Binding'),(original,'Frozen')]
    def compile_at(folder,name):return compile_rocq(folder,name,paths)
    logs=[compile_at(task,n) for n in ('Task','Obligation')]
    for name in (prefix+'Native',prefix+'Domain'):
        src=source/(name+'.v');dest=original/src.name
        if not dest.exists() or dest.read_bytes()!=src.read_bytes() or not (original/(name+'.vo')).exists():
            dest.write_bytes(src.read_bytes());logs.append(compile_at(original,name))
    (binding/'FrozenTarget.v').write_text('From Frozen Require Import '+prefix+'Native '+prefix+'Domain.\n'+'\n'.join(selected)+'\n');logs.append(compile_at(binding,'FrozenTarget'))
    bridge=f'From Coq Require Import ZArith List Bool.\nImport ListNotations.\nOpen Scope nat_scope.\nFrom Trusted Require Import Task.\nFrom Frozen Require Import {prefix}Native {prefix}Domain.\nFrom Binding Require Import FrozenTarget.\n';helpers=[]
    for name,d in available.items():
        if name not in needed or name=='words':continue
        owner=prefix+'Domain' if name in extra else prefix+'Native';deps=set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b',d))
        if 'let*' in d:deps.add('obind')
        rewrites=''.join('try rewrite clone_'+n+'.\n' for n in helpers if n in deps)
        bridge+=f'Lemma clone_{name} : @Task.{name} = @{owner}.{name}.\nProof. unfold Task.{name}, {owner}.{name}.\n'+rewrites+'reflexivity. Qed.\n';helpers.append(name)
    for algorithm in algorithms:bridge+=f'Opaque Task.{algorithm} {prefix}Native.{algorithm}.\n'
    if 'obind' in needed:bridge+='Local '+notation.replace('(obind c','(Task.obind c')+'\n'
    for name,style,body,algorithm in zip(('a','b'),styles,pair,algorithms):
        def qualify(m):
            token=m.group();return 'sl_impl_fn' if token==algorithm else ('Task.'+token if token in native else token)
        context=re.sub(r'\b[A-Za-z_][A-Za-z_0-9]*\b',qualify,body.split(':=',1)[1].strip()[:-1])
        bridge+=f'''Lemma {name}_eq : Task.{name} = {prefix}Native.entry {family} {style}.
Proof. let sl_type:=type of Task.{algorithm} in
exact (@f_equal sl_type (Task.words -> option Task.words)
 (fun (sl_impl_fn:sl_type) => fun (xs:Task.words) => {context})
 Task.{algorithm} {prefix}Native.{algorithm} clone_{algorithm}). Qed.
'''
    bridge+=f'''Lemma valid_eq : Task.valid = {prefix}Domain.valid {index}. Proof. reflexivity. Qed.
Lemma source_congruence3 {{A B C D:Type}} (f:A->B->C->D) {{a a':A}} {{b b':B}} {{c c':C}}
 (ha:a=a') (hb:b=b') (hc:c=c') : f a b c = f a' b' c'.
Proof. destruct ha,hb,hc. reflexivity. Qed.
Example equivalent_binding : Task.equivalent = FrozenTarget.{ctx['equivalence_goal']}.
Proof. exact (@source_congruence3 _ _ _ Prop {prefix}Native.Equivalent
 Task.valid ({prefix}Domain.valid {index}) Task.a ({prefix}Native.entry {family} {styles[0]}) Task.b ({prefix}Native.entry {family} {styles[1]}) valid_eq a_eq b_eq). Qed.
Example refutation_binding (x oa ob:Task.words) : Task.refutationAt x oa ob = FrozenTarget.{ctx['refutation_at_goal']} x oa ob.
Proof. exact (@source_congruence3 _ _ _ Prop (fun v a b => {prefix}Native.RefutationAt v a b x oa ob)
 Task.valid ({prefix}Domain.valid {index}) Task.a ({prefix}Native.entry {family} {styles[0]}) Task.b ({prefix}Native.entry {family} {styles[1]}) valid_eq a_eq b_eq). Qed.
'''
    (binding/'Binding.v').write_text(bridge);logs.append(compile_at(binding,'Binding'));(binding/'compile.log').write_text('\n'.join(logs))
    meta={'pilot_id':row['pilot_id'],'platform':'rocq','public_sha256':tree_digest(task),
        'binding':'rocq-kernel-checked-exact-frozen-target-for-both-branches','source_context':row['source_context_id'],'source_goal':ctx['equivalence_goal'],
        'frozen_source_sha256':{n:hashlib.sha256((source/(n+'.v')).read_bytes()).hexdigest() for n in (prefix+'Native',prefix+'Domain',prefix+'Goals')},
        'preparation_wall_seconds':time.monotonic()-started,'preparation_controller_peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
        'compiler_costs':'compile-costs.jsonl','preparation_model_tokens':None,'final_proof_attempted':False}
    (package/'registry.json').write_text(json.dumps(meta,indent=2)+'\n');return meta


def prepare_graphsuite_lean(row):
    ctx=row['context'];family=ctx.get('family_index')
    if ctx.get('tranche')!='graphsuite' or family not in (0,2):return None
    package=PACKAGES/row['pilot_id']/'lean'
    if (package/'registry.json').exists():
        meta=json.loads((package/'registry.json').read_text())
        if tree_digest(package/'task')!=meta['public_sha256']:raise ValueError('Existing Lean graph/search task changed')
        return meta
    if package.exists():raise ValueError('Incomplete Lean graph/search preparation needs inspection: '+str(package))
    started=time.monotonic();task=package/'task';binding=package/'binding'
    task.mkdir(parents=True,mode=0o700);binding.mkdir(mode=0o700)
    source=ROOT/'benchmarks/tasks/graphsuite-core/lean'
    native=lean_declarations((source/'GraphSuiteNative.lean').read_text());domain=lean_declarations((source/'GraphSuiteDomain.lean').read_text());goals=lean_declarations((source/'GraphSuiteGoals.lean').read_text())
    styles=re.findall(r'entry\s+'+str(family)+r'\s+(\d+)',goals[ctx['equivalence_goal']])
    if len(styles)!=2 or styles[0]!='0' or styles[1] not in ('1','2'):raise ValueError('Unexpected frozen Lean pair')
    pair=[];algorithms=[]
    for name,style in zip(('a','b'),map(int,styles)):
        root='apsp' if family==0 else 'search';text=native[root].replace('def '+root+' (style : Nat)','def '+name,1)
        if family==0:
            algorithm='floyd' if style==0 else 'dijkstra'
            expression='floyd n xs' if style==0 else 'dijkstra n xs '+('true' if style==2 else 'false')
            text,count=re.subn(r'if style == 0 then floyd n xs else dijkstra n xs \(style == 2\)',expression,text)
        else:
            algorithm='brute' if style==0 else 'bmLoop'
            expression='brute text pattern' if style==0 else 'if m == 0 then 0 else bmLoop text pattern '+('true' if style==2 else 'false')+' 49 0'
            text,count=re.subn(r'if style == 0 then brute text pattern else if m == 0 then 0 else bmLoop text pattern \(style == 2\) 49 0',expression,text)
        if count!=1 or re.search(r'\bstyle\b',text):raise ValueError('Unexpected Lean implementation dispatcher')
        pair.append(text);algorithms.append(algorithm)
    branches=re.fullmatch(r'\s*if domain == 0 \|\| domain == 1 then\s*(.*?)\n  else if domain == 2 then\s*(.*?)\n  else false',domain['validB'].split(':=',1)[1],re.S)
    if not branches:raise ValueError('Unexpected Lean graph/search domain')
    valid='def valid (xs : Words) : Prop := ('+re.sub(r'\bdomain\b',str(family),branches.group(1 if family==0 else 2))+') = true'
    available=dict(native);available['between']=domain['between'];needed=set();todo=[*pair,valid]
    while todo:
        for name in set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b',todo.pop())) & available.keys():
            if name not in needed:needed.add(name);todo.append(available[name])
    if needed & {'entry','apsp','scc','search','TS','Equivalent','RefutationAt'}:raise ValueError('Unexpected unrelated Lean declaration')
    public='import Lean\nnamespace Task\n'+'\n'.join([d for n,d in available.items() if n in needed]+[valid,*pair])+'''
def equivalent : Prop := ∀ x, valid x → ∃ o, a x=some o ∧ b x=some o
def refutationAt (x oa ob : Words) : Prop := valid x ∧ a x=some oa ∧ b x=some ob ∧ oa≠ob
end Task
'''
    public=re.sub(r'\bmutant\b','mode',public);public=re.sub(r'(?<![A-Za-z0-9_.])pure\b','Pure.pure',public)
    (task/'Task.lean').write_text(public);(task/'Obligation.lean').write_text('import Task\nnamespace Obligation\ndef goal : Prop := Task.equivalent\nend Obligation\n')
    original=ROOT/'_build/pilot-v1/graphsuite-lean-binding';original.mkdir(parents=True,exist_ok=True);paths=[task,original]
    def compile_at(folder,name):return compile_lean(folder,name,paths)
    logs=[compile_at(task,n) for n in ('Task','Obligation')]
    for name in ('GraphSuiteNative','GraphSuiteDomain','GraphSuiteGoals'):
        src=source/(name+'.lean');dest=original/src.name
        if not dest.exists() or dest.read_bytes()!=src.read_bytes() or not (original/(name+'.olean')).exists():dest.write_bytes(src.read_bytes());logs.append(compile_at(original,name))
    bridge='import Task\nimport GraphSuiteGoals\n'
    if family==2:
        bridge+='''theorem bmLoop_eq (text pattern : Task.Words) (mode : Bool) (fuel i : Nat) :
    Task.bmLoop text pattern mode fuel i = SpecLessBenchGraphSuite.bmLoop text pattern mode fuel i := by
  induction fuel generalizing i with
  | zero => rfl
  | succ fuel ih =>
    simp only [Task.bmLoop, SpecLessBenchGraphSuite.bmLoop, Task.word,
      SpecLessBenchGraphSuite.word, Task.getOr, SpecLessBenchGraphSuite.getOr, ih]
    rfl
'''
    types={'floyd':'Nat → Task.Words → Task.Words','dijkstra':'Nat → Task.Words → Bool → Task.Words','brute':'Task.Words → Task.Words → Int','bmLoop':'Task.Words → Task.Words → Bool → Nat → Nat → Int'}
    for name,style,body,algorithm in zip(('a','b'),styles,pair,algorithms):
        def qualify(m):
            token=m.group();return 'sl_impl_fn' if token==algorithm else ('Task.'+token if token in native else token)
        context=re.sub(r'\b[A-Za-z_][A-Za-z_0-9]*\b',qualify,body.split(':=',1)[1])
        proof='by\n    funext text pattern mode fuel i\n    exact bmLoop_eq text pattern mode fuel i' if algorithm=='bmLoop' else 'by rfl'
        bridge+=f'''theorem {name}_eq : Task.{name} = SpecLessBenchGraphSuite.entry {family} {style} := by
  have h : Task.{algorithm} = SpecLessBenchGraphSuite.{algorithm} := {proof}
  exact congrArg (fun (sl_impl_fn : {types[algorithm]}) => fun (xs : Task.Words) => {context}) h
'''
    bridge+=f'''theorem valid_eq : Task.valid = SpecLessBenchGraphSuite.valid {family} := by rfl
example : Task.equivalent = SpecLessBenchGraphSuite.{ctx['equivalence_goal']} := by
  unfold Task.equivalent SpecLessBenchGraphSuite.{ctx['equivalence_goal']} SpecLessBenchGraphSuite.Equivalent
  rw [valid_eq,a_eq,b_eq]
example (x oa ob : Task.Words) : Task.refutationAt x oa ob = SpecLessBenchGraphSuite.{ctx['refutation_at_goal']} x oa ob := by
  unfold Task.refutationAt SpecLessBenchGraphSuite.{ctx['refutation_at_goal']} SpecLessBenchGraphSuite.RefutationAt
  rw [valid_eq,a_eq,b_eq]
'''
    (binding/'Binding.lean').write_text(bridge);logs.append(compile_at(binding,'Binding'));(binding/'compile.log').write_text('\n'.join(logs))
    meta={'pilot_id':row['pilot_id'],'platform':'lean','public_sha256':tree_digest(task),
        'binding':'lean-kernel-checked-exact-frozen-target-for-both-branches','source_context':row['source_context_id'],'source_goal':ctx['equivalence_goal'],
        'frozen_source_sha256':{n:hashlib.sha256((source/(n+'.lean')).read_bytes()).hexdigest() for n in ('GraphSuiteNative','GraphSuiteDomain','GraphSuiteGoals')},
        'preparation_wall_seconds':time.monotonic()-started,'preparation_controller_peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
        'compiler_costs':'compile-costs.jsonl','preparation_model_tokens':None,'final_proof_attempted':False}
    (package/'registry.json').write_text(json.dumps(meta,indent=2)+'\n');return meta
