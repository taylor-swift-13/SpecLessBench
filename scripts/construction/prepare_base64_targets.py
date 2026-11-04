"""Append new branch target bindings without modifying earlier program registries."""
import json,os,hashlib
from base64_common import ROOT,CORE,BUILD,GROUPS,LEAN,COQC,FIVE
from measure import measured
def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'benchmarks/proof-interface/v1';manifest=json.loads((out/'manifest.json').read_text())
    ls=['import Base64Goals','namespace EqualBenchBase64Submission']
    rs=['From EqualBenchBase64Native Require Import Base64Goals.']
    cs=['From EqualBenchBase64 Require Import '+ ' '.join(g[0].upper()+'Goals'for g in GROUPS)+'.']
    bindings=[]
    for i,(name,gid,contexts,_)in enumerate(GROUPS):
        for tid,right,d in contexts:
            t=tid.replace('-','_')
            for suffix in ('equivalence','refutationAt'):
                nm=t+'_'+suffix
                if suffix=='equivalence':
                    ls.append(f'def {nm} : Prop := EqualBenchBase64.{nm}')
                    rs.append(f'Definition {nm} : Prop := Base64Goals.{nm}.')
                    cs.append(f'Definition {nm} : Prop := {name.upper()}Goals.{nm}.')
                else:
                    ls.append(f'def {nm} := EqualBenchBase64.{nm}')
                    rs.append(f'Definition {nm} := Base64Goals.{nm}.')
                    cs.append(f'Definition {nm} := {name.upper()}Goals.{nm}.')
            bindings.append({'context_id':tid,'group_id':gid,'family':name,'family_index':i,'domain_index':d,'tranche':'base64',
                'goal_module':'Base64Targets','lean_namespace':'EqualBenchBase64Submission',
                'equivalence_goal':t+'_equivalence','refutation_at_goal':t+'_refutationAt'})
    write(out/'lean/Base64Targets.lean','\n'.join(ls+['end EqualBenchBase64Submission'])+'\n')
    write(out/'rocq/Base64Targets.v','\n'.join(rs)+'\n');write(out/'compcert/Base64Targets.v','\n'.join(cs)+'\n')
    os.environ['LEAN_PATH']=str(BUILD/'lean')
    measured([LEAN,'-o',str(out/'lean/Base64Targets.olean'),str(out/'lean/Base64Targets.lean')],'shared-base64-interface','check-lean-branch-targets')
    measured([COQC,'-Q',str(CORE/'rocq'),'EqualBenchBase64Native',str(out/'rocq/Base64Targets.v')],'shared-base64-interface','check-rocq-branch-targets')
    measured([FIVE+'/coqc','-Q',str(BUILD/'compcert'),'EqualBenchBase64','-Q',str(CORE/'compcert/ast'),'EqualBenchBase64.Generated',str(out/'compcert/Base64Targets.v')],'shared-base64-interface','check-compcert-branch-targets')
    manifest['contexts']=[c for c in manifest['contexts']if c['tranche']!='base64']+bindings
    manifest['files']=[{'path':p.relative_to(out).as_posix(),'sha256':sha(p)}for p in sorted(out.rglob('*'))if p.suffix in('.v','.lean')]
    manifest['submission_validator_sha256']=sha(ROOT/'scripts/construction/submission_contract.py')
    write(out/'manifest.json',json.dumps(manifest,indent=2)+'\n')
    print(f"{len(manifest['contexts'])} contexts have three-platform explicit-branch target types.")
if __name__=='__main__':main()
