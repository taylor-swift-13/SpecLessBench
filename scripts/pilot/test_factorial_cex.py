"""Test counterexample reference gate against proof bypasses, without proving it."""
import json
import tempfile
from pathlib import Path
from release_gate import score

ROOT=Path(__file__).resolve().parents[2]
meta=json.loads((ROOT/'_build/pilot-v1/factorial-cex/registry.json').read_text())
with tempfile.TemporaryDirectory(prefix='factorial-cex-bypass-') as tmp:
    proof=Path(tmp)/'Submission.lean'
    for label,body in [('sorry','theorem solve : Obligation.goal := by sorry'),
                       ('axiom','axiom bypass : Obligation.goal\ntheorem solve : Obligation.goal := bypass'),
                       ('wrong-goal','theorem solve : True := True.intro')]:
        proof.write_text('import Obligation\nnamespace Submission\n'+body+'\nend Submission\n')
        assert score(meta['pilot_id'],'lean',proof,purpose='evaluation')['status']=='reference-only'
        result=score(meta['pilot_id'],'lean',proof,purpose='reference')
        assert result['status']=='rejected',(label,result)
        print(label,'rejected',flush=True)
print('Only bypass proofs were tested; no benchmark theorem was proved.')
