"""Record a nonfatal target-type compilation performance warning."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'construction'))
from accounting import AUDIT,append,now
append(AUDIT/'issues.jsonl',{'schema_version':1,'id':'PILOT-COMPCERT-LARGE-OBSERVATION',
 'timestamp_utc':now(),'group_id':'shared-pilot-audit','kind':'compiler-warning','status':'observed',
 'description':'Rocq emits abstract-large-number warnings when literal CompCert observations use 8192-slot padded buffers.',
 'impact':'Nonfatal type-check warning; potential performance concern for grader inputs.',
 'resolution':'Keep fixed observation semantics; do not replace with unvalidated compression.',
 'final_target_proofs_attempted':False})
