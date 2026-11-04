"""Append new branch target bindings without modifying earlier program registries."""
import json,os,hashlib
from systems_common import ROOT,CORE,BUILD,GROUPS,LEAN,COQC,FIVE
from measure import measured
def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'benchmarks/proof-interface/v1';manifest=json.loads((out/'manifest.json').read_text())
    ls=['import SystemsGoals','namespace EqualBenchSystemsSubmission']
    rs=['From EqualBenchSystemsNative Require Import SystemsGoals.']
    cs=['From EqualBenchSystems Require Import '+ ' '.join(g[0].upper()+'Goals'for g in GROUPS)+'.']
    bindings=[]
    for i,(name,gid,contexts,_)in enumerate(GROUPS):
        for tid,right,d in contexts:
            t=tid.replace('-','_')
            for suffix in ('equivalence','refutationAt'):
                nm=t+'_'+suffix
                if suffix=='equivalence':
                    ls.append(f'def {nm} : Prop := EqualBenchSystems.{nm}')
                    rs.append(f'Definition {nm} : Prop := SystemsGoals.{nm}.')
                    cs.append(f'Definition {nm} : Prop := {name.upper()}Goals.{nm}.')
                else:
                    ls.append(f'def {nm} := EqualBenchSystems.{nm}')
                    rs.append(f'Definition {nm} := SystemsGoals.{nm}.')
                    cs.append(f'Definition {nm} := {name.upper()}Goals.{nm}.')
            bindings.append({'context_id':tid,'group_id':gid,'family':name,'family_index':i,'domain_index':d,'tranche':'systems',
                'goal_module':'SystemsTargets','lean_namespace':'EqualBenchSystemsSubmission',
                'equivalence_goal':t+'_equivalence','refutation_at_goal':t+'_refutationAt'})
    write(out/'lean/SystemsTargets.lean','\n'.join(ls+['end EqualBenchSystemsSubmission'])+'\n')
    write(out/'rocq/SystemsTargets.v','\n'.join(rs)+'\n');write(out/'compcert/SystemsTargets.v','\n'.join(cs)+'\n')
    os.environ['LEAN_PATH']=str(BUILD/'lean')
    measured([LEAN,'-o',str(out/'lean/SystemsTargets.olean'),str(out/'lean/SystemsTargets.lean')],'shared-systems-interface','check-lean-branch-targets')
    measured([COQC,'-Q',str(CORE/'rocq'),'EqualBenchSystemsNative',str(out/'rocq/SystemsTargets.v')],'shared-systems-interface','check-rocq-branch-targets')
    measured([FIVE+'/coqc','-Q',str(BUILD/'compcert'),'EqualBenchSystems','-Q',str(CORE/'compcert/ast'),'EqualBenchSystems.Generated',str(out/'compcert/SystemsTargets.v')],'shared-systems-interface','check-compcert-branch-targets')
    manifest['contexts']=[c for c in manifest['contexts']if c['tranche']!='systems']+bindings
    manifest['files']=[{'path':p.relative_to(out).as_posix(),'sha256':sha(p)}for p in sorted(out.rglob('*'))if p.suffix in('.v','.lean')]
    manifest['submission_validator_sha256']=sha(ROOT/'scripts/construction/submission_contract.py')
    write(out/'manifest.json',json.dumps(manifest,indent=2)+'\n')
    print(f"{len(manifest['contexts'])} contexts have three-platform explicit-branch target types.")
if __name__=='__main__':main()
