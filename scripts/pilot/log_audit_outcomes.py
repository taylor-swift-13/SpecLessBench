"""Append resolved prototype diagnostics and unresolved release blockers."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'construction'))
from accounting import AUDIT,append,now
items=[
 ('PILOT-LEAKAGE','open','Neutral index hides original IDs, but shared program sources and public history retain explicit and structural polarity hints.'),
 ('PILOT-RELEASE-PACKAGE','open','Per-task solver packaging, target binding and solver-side leak/contamination audit are not implemented; all real submissions fail closed.'),
 ('PILOT-TRUST-BOUNDARY','open','Synthetic checks do not establish full hostile-code security; Rocq assumption-output handling and shared kernel need adversarial review.'),
 ('PILOT-DIRECT-CGROUP','resolved','System cgroup root is not writable, but a user systemd scope successfully enforces and records cgroup-v2 memory and process limits.'),
 ('PILOT-LEAN-TOY-DIAGNOSTICS','resolved','Toy module namespaces, sysroot lookup and type binding were corrected; valid/sorry/axiom/wrong-goal regressions pass.'),
 ('PILOT-RESOURCE-TOY-DIAGNOSTICS','resolved','Lean thread creation under a 4-GiB virtual address cap failed; single-thread mode with a 16-GiB virtual cap and separate 3-GiB cgroup memory cap passed.'),
 ('PILOT-ROCQ-TOY-NAMESPACE','resolved','Coq output logical paths were corrected using explicit protected and candidate namespaces; synthetic three-platform tests pass.')]
for ident,status,desc in items:
    append(AUDIT/'issues.jsonl',{'schema_version':1,'id':ident,'timestamp_utc':now(),'group_id':'shared-pilot-audit',
        'kind':'pilot-audit','status':status,'description':desc,'final_target_proofs_attempted':False})
