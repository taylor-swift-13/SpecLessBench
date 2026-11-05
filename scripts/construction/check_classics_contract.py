"""Type-check literal specialized goals, never prove the final obligations."""
import copy,hashlib,json,os
from classics_common import ROOT,CORE,BUILD,LEAN,COQC,FIVE,GROUPS
from submission_contract import validate,render
from measure import measured
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    contracts=ROOT/'benchmarks/proof-interface';work=BUILD/'contract-checks';work.mkdir(exist_ok=True)
    prior=json.loads((contracts/'validation.json').read_text())
    prior_batches=prior.get('batches',[prior]); prior_batches=[b for b in prior_batches if b.get('tranche')!='classics']
    counts={'valid_counterexample_packages':0,'rejected_malformed_packages':0,'unproved_obligations_checked':0}
    for platform in ('lean','rocq','compcert'):
        texts=[]
        for i,(name,gid,contexts,_)in enumerate(GROUPS):
            witness=json.loads((CORE/'evidence'/(name+'.json')).read_text())['witness']
            request={'context_id':contexts[-1][0],'platform':platform,'claim':'counterexample','proof_module':'Submission','proof_theorem':'solve',
              'input':witness['input'],'left_observation':{'return':0,'payload':witness['v0'][1:]},'right_observation':{'return':0,'payload':witness['v2'][1:]}}
            validate(request);counts['valid_counterexample_packages']+=1
            path=render(request,work/platform/name);text=path.read_text()
            if platform=='lean':text=text.replace('import ClassicsTargets\n','').replace('SpecLessBenchObligation',f'ClassicsContractCheck{i}')
            else:text=text.replace('Definition goal :',f'Definition goal_{i} :')
            texts.append(text)
            for mutation in ('bare-disjunction','nonliteral-witness','identical-observations','extra-field','invalid-identifier','wrong-container','outside-domain'):
                bad=copy.deepcopy(request)
                if mutation=='bare-disjunction':bad['claim']='disjunction'
                elif mutation=='nonliteral-witness':bad['input']='Classical.choice arbitraryInput'
                elif mutation=='identical-observations':bad['right_observation']=bad['left_observation']
                elif mutation=='extra-field':bad['arbitrary_target']='Certificate'
                elif mutation=='invalid-identifier':bad['proof_module']='Submission; admit'
                elif mutation=='wrong-container':bad['input']=[[0]]
                else:bad['input']=[]
                try:validate(bad)
                except ValueError:counts['rejected_malformed_packages']+=1
                else:raise AssertionError('Malformed submission accepted: '+mutation)
        source=work/('ClassicsContractChecks_'+platform+('.lean'if platform=='lean'else'.v'))
        source.write_text(('import ClassicsTargets\n'if platform=='lean'else'')+'\n'.join(texts))
        if platform=='lean':
            os.environ['LEAN_PATH']=str(BUILD/'lean')+':'+str(contracts/'lean')
            measured([LEAN,str(source)],'shared-classics-interface','validate-literal-lean-obligations')
        elif platform=='rocq':
            measured([COQC,'-Q',str(CORE/'rocq'),'SpecLessBenchClassicsNative','-Q',str(contracts/'rocq'),'',str(source)],'shared-classics-interface','validate-literal-rocq-obligations')
        else:
            measured([FIVE+'/coqc','-Q',str(BUILD/'compcert'),'SpecLessBenchClassics','-Q',str(CORE/'compcert/ast'),'SpecLessBenchClassics.Generated','-Q',str(contracts/'compcert'),'',str(source)],'shared-classics-interface','validate-literal-compcert-obligations')
        counts['unproved_obligations_checked']+=len(GROUPS)
    counts.update(tranche='classics',final_target_proofs_attempted=False,gate_proofs_supplied=False,scope='classics tranche validator/generated obligation types; no final proofs or complete isolated grader')
    totals={k:sum(b[k]for b in prior_batches)+counts[k]for k in ('valid_counterexample_packages','rejected_malformed_packages','unproved_obligations_checked')}
    totals.update(batches=prior_batches+[counts],final_target_proofs_attempted=False,gate_proofs_supplied=False,
      scope='all current literal obligation types; solver isolation, proof-axiom auditing and full grading pending')
    (contracts/'validation-classics.json').write_text(json.dumps(counts,indent=2)+'\n')
    (contracts/'validation.json').write_text(json.dumps(totals,indent=2)+'\n')
    m=json.loads((contracts/'manifest.json').read_text());m['validation_evidence_sha256']=sha(contracts/'validation.json');m['submission_validator_sha256']=sha(ROOT/'scripts/construction/submission_contract.py')
    (contracts/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    print(json.dumps(totals))
if __name__=='__main__':main()
