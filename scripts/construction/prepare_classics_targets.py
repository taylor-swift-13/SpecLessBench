"""Append new branch target bindings without modifying earlier program registries."""
import json,os,hashlib
from classics_common import ROOT,CORE,BUILD,GROUPS,LEAN,COQC,FIVE
from measure import measured
def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'benchmarks/proof-interface';manifest=json.loads((out/'manifest.json').read_text())
    ls=['import ClassicsGoals','namespace SpecLessBenchClassicsSubmission']
    rs=['From SpecLessBenchClassicsNative Require Import ClassicsGoals.']
    cs=['From SpecLessBenchClassics Require Import '+ ' '.join(g[0].upper()+'Goals'for g in GROUPS)+'.']
    bindings=[]
    for i,(name,gid,contexts,_)in enumerate(GROUPS):
        for tid,right,d in contexts:
            t=tid.replace('-','_')
            for suffix in ('equivalence','refutationAt'):
                nm=t+'_'+suffix
                if suffix=='equivalence':
                    ls.append(f'def {nm} : Prop := SpecLessBenchClassics.{nm}')
                    rs.append(f'Definition {nm} : Prop := ClassicsGoals.{nm}.')
                    cs.append(f'Definition {nm} : Prop := {name.upper()}Goals.{nm}.')
                else:
                    ls.append(f'def {nm} := SpecLessBenchClassics.{nm}')
                    rs.append(f'Definition {nm} := ClassicsGoals.{nm}.')
                    cs.append(f'Definition {nm} := {name.upper()}Goals.{nm}.')
            bindings.append({'context_id':tid,'group_id':gid,'family':name,'family_index':i,'domain_index':d,'tranche':'classics',
                'goal_module':'ClassicsTargets','lean_namespace':'SpecLessBenchClassicsSubmission',
                'equivalence_goal':t+'_equivalence','refutation_at_goal':t+'_refutationAt'})
    write(out/'lean/ClassicsTargets.lean','\n'.join(ls+['end SpecLessBenchClassicsSubmission'])+'\n')
    write(out/'rocq/ClassicsTargets.v','\n'.join(rs)+'\n');write(out/'compcert/ClassicsTargets.v','\n'.join(cs)+'\n')
    os.environ['LEAN_PATH']=str(BUILD/'lean')
    measured([LEAN,'-o',str(out/'lean/ClassicsTargets.olean'),str(out/'lean/ClassicsTargets.lean')],'shared-classics-interface','check-lean-branch-targets')
    measured([COQC,'-Q',str(CORE/'rocq'),'SpecLessBenchClassicsNative',str(out/'rocq/ClassicsTargets.v')],'shared-classics-interface','check-rocq-branch-targets')
    measured([FIVE+'/coqc','-Q',str(BUILD/'compcert'),'SpecLessBenchClassics','-Q',str(CORE/'compcert/ast'),'SpecLessBenchClassics.Generated',str(out/'compcert/ClassicsTargets.v')],'shared-classics-interface','check-compcert-branch-targets')
    manifest['contexts']=[c for c in manifest['contexts']if c['tranche']!='classics']+bindings
    manifest['files']=[{'path':p.relative_to(out).as_posix(),'sha256':sha(p)}for p in sorted(out.rglob('*'))if p.suffix in('.v','.lean')]
    manifest['submission_validator_sha256']=sha(ROOT/'scripts/construction/submission_contract.py')
    write(out/'manifest.json',json.dumps(manifest,indent=2)+'\n')
    print(f"{len(manifest['contexts'])} contexts have three-platform explicit-branch target types.")
if __name__=='__main__':main()
