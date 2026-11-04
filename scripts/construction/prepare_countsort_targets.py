"""Append new branch target bindings without modifying earlier program registries."""
import json,os,hashlib
from countsort_common import ROOT,CORE,BUILD,GROUPS,LEAN,COQC,FIVE
from measure import measured
def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'benchmarks/proof-interface/v1';manifest=json.loads((out/'manifest.json').read_text())
    ls=['import CountSortGoals','namespace SpecLessBenchCountSortSubmission']
    rs=['From SpecLessBenchCountSortNative Require Import CountSortGoals.']
    cs=['From SpecLessBenchCountSort Require Import '+ ' '.join(g[0].upper()+'Goals'for g in GROUPS)+'.']
    bindings=[]
    for i,(name,gid,contexts,_)in enumerate(GROUPS):
        for tid,right,d in contexts:
            t=tid.replace('-','_')
            for suffix in ('equivalence','refutationAt'):
                nm=t+'_'+suffix
                if suffix=='equivalence':
                    ls.append(f'def {nm} : Prop := SpecLessBenchCountSort.{nm}')
                    rs.append(f'Definition {nm} : Prop := CountSortGoals.{nm}.')
                    cs.append(f'Definition {nm} : Prop := {name.upper()}Goals.{nm}.')
                else:
                    ls.append(f'def {nm} := SpecLessBenchCountSort.{nm}')
                    rs.append(f'Definition {nm} := CountSortGoals.{nm}.')
                    cs.append(f'Definition {nm} := {name.upper()}Goals.{nm}.')
            bindings.append({'context_id':tid,'group_id':gid,'family':name,'family_index':i,'domain_index':d,'tranche':'countsort',
                'goal_module':'CountSortTargets','lean_namespace':'SpecLessBenchCountSortSubmission',
                'equivalence_goal':t+'_equivalence','refutation_at_goal':t+'_refutationAt'})
    write(out/'lean/CountSortTargets.lean','\n'.join(ls+['end SpecLessBenchCountSortSubmission'])+'\n')
    write(out/'rocq/CountSortTargets.v','\n'.join(rs)+'\n');write(out/'compcert/CountSortTargets.v','\n'.join(cs)+'\n')
    os.environ['LEAN_PATH']=str(BUILD/'lean')
    measured([LEAN,'-o',str(out/'lean/CountSortTargets.olean'),str(out/'lean/CountSortTargets.lean')],'shared-countsort-interface','check-lean-branch-targets')
    measured([COQC,'-Q',str(CORE/'rocq'),'SpecLessBenchCountSortNative',str(out/'rocq/CountSortTargets.v')],'shared-countsort-interface','check-rocq-branch-targets')
    measured([FIVE+'/coqc','-Q',str(BUILD/'compcert'),'SpecLessBenchCountSort','-Q',str(CORE/'compcert/ast'),'SpecLessBenchCountSort.Generated',str(out/'compcert/CountSortTargets.v')],'shared-countsort-interface','check-compcert-branch-targets')
    manifest['contexts']=[c for c in manifest['contexts']if c['tranche']!='countsort']+bindings
    manifest['files']=[{'path':p.relative_to(out).as_posix(),'sha256':sha(p)}for p in sorted(out.rglob('*'))if p.suffix in('.v','.lean')]
    manifest['submission_validator_sha256']=sha(ROOT/'scripts/construction/submission_contract.py')
    write(out/'manifest.json',json.dumps(manifest,indent=2)+'\n')
    print(f"{len(manifest['contexts'])} contexts have three-platform explicit-branch target types.")
if __name__=='__main__':main()
