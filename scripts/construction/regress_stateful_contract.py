"""Revalidate all earlier/current literal packages with the extended frontend."""
import json
from accounting import ROOT
from submission_contract import validate
def main():
    seen={}
    for batch in ('algorithms-v0.3','boundaries-v0.4','stateful-v0.5'):
        for p in(ROOT/'_build'/batch/'contract-checks').rglob('submission.json'):
            req=json.loads(p.read_text());context=validate(req)
            key=(req['context_id'],req['platform']);seen[key]=context['tranche']
    evidence=json.loads((ROOT/'benchmarks/proof-interface/validation.json').read_text())
    assert len(seen)==evidence['valid_counterexample_packages']==51
    assert set(seen.values())=={'qcip','algorithms','boundaries','stateful'}
    print('51 prior/current literal packages pass the extended validator; no final proof submitted.')
if __name__=='__main__':main()
