"""Append new branch target bindings without modifying earlier program registries."""
import json,os,hashlib
from boundaries_common import ROOT,CORE,BUILD,GROUPS,LEAN,COQC,FIVE
from measure import measured
def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'benchmarks/proof-interface/v1';manifest=json.loads((out/'manifest.json').read_text())
    ls=['import BoundaryGoals','namespace EqualBenchBoundarySubmission']
    rs=['From EqualBenchBoundaryNative Require Import BoundaryGoals.']
    cs=['From EqualBenchBoundary Require Import '+ ' '.join(g[0].upper()+'Goals'for g in GROUPS)+'.']
    bindings=[]
    for i,(name,gid,contexts,_)in enumerate(GROUPS):
        for tid,right,d in contexts:
            t=tid.replace('-','_')
            for suffix in ('equivalence','refutationAt'):
                nm=t+'_'+suffix
                if suffix=='equivalence':
                    ls.append(f'def {nm} : Prop := EqualBenchBoundary.{nm}')
                    rs.append(f'Definition {nm} : Prop := BoundaryGoals.{nm}.')
                    cs.append(f'Definition {nm} : Prop := {name.upper()}Goals.{nm}.')
                else:
                    ls.append(f'def {nm} := EqualBenchBoundary.{nm}')
                    rs.append(f'Definition {nm} := BoundaryGoals.{nm}.')
                    cs.append(f'Definition {nm} := {name.upper()}Goals.{nm}.')
            bindings.append({'context_id':tid,'group_id':gid,'family':name,'family_index':i,'domain_index':d,'tranche':'boundaries',
                'goal_module':'BoundaryTargets','lean_namespace':'EqualBenchBoundarySubmission',
                'equivalence_goal':t+'_equivalence','refutation_at_goal':t+'_refutationAt'})
    write(out/'lean/BoundaryTargets.lean','\n'.join(ls+['end EqualBenchBoundarySubmission'])+'\n')
    write(out/'rocq/BoundaryTargets.v','\n'.join(rs)+'\n');write(out/'compcert/BoundaryTargets.v','\n'.join(cs)+'\n')
    os.environ['LEAN_PATH']=str(BUILD/'lean')
    measured([LEAN,'-o',str(out/'lean/BoundaryTargets.olean'),str(out/'lean/BoundaryTargets.lean')],'shared-boundaries-interface','check-lean-branch-targets')
    measured([COQC,'-Q',str(CORE/'rocq'),'EqualBenchBoundaryNative',str(out/'rocq/BoundaryTargets.v')],'shared-boundaries-interface','check-rocq-branch-targets')
    measured([FIVE+'/coqc','-Q',str(BUILD/'compcert'),'EqualBenchBoundary','-Q',str(CORE/'compcert/ast'),'EqualBenchBoundary.Generated',str(out/'compcert/BoundaryTargets.v')],'shared-boundaries-interface','check-compcert-branch-targets')
    manifest['contexts']=[c for c in manifest['contexts']if c['tranche']!='boundaries']+bindings
    manifest['files']=[{'path':p.relative_to(out).as_posix(),'sha256':sha(p)}for p in sorted(out.rglob('*'))if p.suffix in('.v','.lean')]
    manifest['submission_validator_sha256']=sha(ROOT/'scripts/construction/submission_contract.py')
    write(out/'manifest.json',json.dumps(manifest,indent=2)+'\n')
    print('40 contexts have three-platform explicit-branch target types; no final proofs.')
if __name__=='__main__':main()
