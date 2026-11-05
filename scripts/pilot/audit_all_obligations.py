"""Type-check one literal refutation and one equality obligation per task.

Concrete data are arbitrary type-checking probes, not alleged witnesses; the
script supplies no proof and runs no final target. Outputs containing curator
identifiers are kept in the private build workspace.
"""
import importlib,json,os,re,subprocess,sys
from pathlib import Path
from private_paths import PRIVATE
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'benchmarks/pilot';W=ROOT/'_build/pilot-v1/platform-audit/workspace';OUT=ROOT/'_build/pilot-v1/obligation-audit'
sys.path[:0]=[str(ROOT/'scripts/construction'),str(ROOT/'scripts/pilot')]
from submission_contract import validate,render
from verify_freeze import main as verify

LEAN='/home/yangfp/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean'
COQC='/home/yangfp/.opam/qcp-8.20/bin/coqc';FIVE='/home/yangfp/.opam/five/bin/coqc'
CONFIG={
 'boundaries':('boundaries-core','boundaries-v0.4','Boundary'),
 'stateful':('stateful-core','stateful-v0.5','Stateful'),
 'systems':('systems-core','systems-v0.6','Systems'),
 'base64':('base64-core','base64-v0.7','Base64'),
 'classics':('classics-core','classics-v0.8','Classics'),
 'graphsuite':('graphsuite-core','classics-graphs-v0.10','GraphSuite'),
 'countsort':('countsort-core','construction-continuation-v0.11','CountSort')}
QCP={'bst':{'initial':[],'commands':[]},'avl':{'commands':[]},
     'ring':{'capacity':1,'commands':[]},'dijkstra':{'vertices':1,'start':0,'edges':[]}}
cache={}
def inputs(ctx):
    if ctx['tranche']=='qcip':return [QCP[ctx['family']]]
    kind=ctx['tranche'];index=ctx['family_index'];key=(kind,index)
    if key not in cache:
        module=importlib.import_module('differential_algorithms' if kind=='algorithms' else
          {'boundaries':'boundary_cases','stateful':'stateful_cases','systems':'systems_cases'}.get(kind,kind+'_cases'))
        cache[key]=module.corpus(index,0,True)[0]
    return cache[key]
def coq_paths(kind,platform):
    iface=W/'benchmarks/proof-interface/v1'/platform
    old=W/'benchmarks/tasks/qcip-core';basic=W/'benchmarks/tasks/algorithms-core'
    if kind in ('qcip','algorithms'):
        if platform=='rocq':return ['-Q',str(old/'rocq'),'SpecLessBench.QCIP','-Q',str(old/'rocq_native'),'SpecLessBenchNative','-Q',str(basic/'rocq'),'SpecLessBenchBasic','-Q',str(iface),'']
        return ['-Q',str(W/'_build/three-platform/compcert'),'SpecLessBench.QCIP','-Q',str(old/'compcert/ast'),'SpecLessBench.QCIP.Generated',
          '-Q',str(W/'_build/algorithms-v0.3/compcert'),'SpecLessBenchAlgorithms','-Q',str(basic/'compcert/ast'),'SpecLessBenchAlgorithms.Generated','-Q',str(iface),'']
    core,batch,prefix=CONFIG[kind];base=W/'benchmarks/tasks'/core
    if platform=='rocq':return ['-Q',str(base/'rocq'),'SpecLessBench'+prefix+'Native','-Q',str(iface),'']
    return ['-Q',str(W/'_build'/batch/'compcert'),'SpecLessBench'+prefix,'-Q',str(base/'compcert/ast'),'SpecLessBench'+prefix+'.Generated','-Q',str(iface),'']
def main():
    verify()
    if OUT.exists():raise SystemExit('Obligation audit workspace already exists; preserve it and use a new revision.')
    OUT.mkdir(parents=True);mapping=json.loads((PRIVATE/'mapping.json').read_text())['contexts']
    grouped={};counts={'equivalence':0,'literal_refutation':0}
    for i,row in enumerate(mapping):
        ctx=row['context'];kind=ctx['tranche'];module=ctx.get('goal_module','BranchTargets')
        for platform in ('lean','rocq','compcert'):
            base={'context_id':ctx['context_id'],'platform':platform,'claim':'equivalence','proof_module':'Submission','proof_theorem':'solve'}
            validate(base)
            candidate=None
            for x in inputs(ctx):
                request=dict(base,claim='counterexample',input=x,left_observation={'return':0,'payload':[]},right_observation={'return':0,'payload':[0]})
                try:validate(request);candidate=request;break
                except ValueError:pass
            assert candidate is not None,ctx['context_id']
            for claim,request in [('equivalence',base),('literal_refutation',candidate)]:
                raw=render(request,OUT/'raw'/str(i)/platform/claim).read_text()
                line=next(s for s in raw.splitlines()if s.startswith('def goal :')or s.startswith('Definition goal :'))
                key=(kind if module!='BranchTargets' else 'branch',module,platform)
                group=grouped.setdefault(key,[]);unique=f'goal_{i}_{claim}'
                line=line.replace('def goal :',f'def {unique} :').replace('Definition goal :',f'Definition {unique} :')
                group.append(line);counts[claim]+=1
    lean_paths=[str(W/'benchmarks/proof-interface/v1/lean')]+[str(p)for p in sorted((W/'_build').glob('*/lean'))if p.is_dir()]
    env=dict(os.environ,LEAN_PATH=':'.join(lean_paths));compiled=[]
    for (kind,module,platform),lines in grouped.items():
        name=f'Check_{module}_{platform}';path=OUT/(name+('.lean'if platform=='lean'else'.v'))
        if platform=='lean':
            source=f'import {module}\nnamespace SpecLessBenchObligation\n'+'\n'.join(lines)+'\nend SpecLessBenchObligation\n'
            command=[LEAN,str(path)]
        else:
            source=('From Stdlib'if platform=='compcert'else'From Coq')+' Require Import ZArith List.\nRequire Import '+module+'.\nImport ListNotations.\nOpen Scope Z_scope.\n'+'\n'.join(lines)+'\n'
            command=[COQC if platform=='rocq'else FIVE,*coq_paths('qcip' if kind=='branch' else kind,platform),str(path)]
        path.write_text(source);log=OUT/(name+'.log')
        with log.open('wb')as stream:result=subprocess.run(command,env=env,cwd=W,stdout=stream,stderr=subprocess.STDOUT,timeout=900)
        compiled.append({'module':module,'platform':platform,'obligation_count':len(lines),'exit_code':result.returncode})
        if result.returncode:raise SystemExit(f'Obligation typecheck failed; see private log {log}')
        print(module,platform,len(lines),'types checked',flush=True)
    assert counts=={'equivalence':213,'literal_refutation':213}
    verify();report={'schema_version':1,'status':'passed','contexts':71,'platform_instances':213,
      'equivalence_obligations':counts['equivalence'],'literal_refutation_obligations':counts['literal_refutation'],
      'aggregate_compilation_units':len(compiled),'compiled':compiled,
      'scope':'goal types only, using arbitrary valid probe inputs and fabricated distinct observations; no claim these are witnesses and no proofs attempted',
      'solver_package_verified':False}
    (P/'obligation-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(counts))
if __name__=='__main__':main()
