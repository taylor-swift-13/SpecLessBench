"""Record an explicit freeze amendment without altering task semantics."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'construction'))
from accounting import AUDIT,append,now
append(AUDIT/'issues.jsonl',{'schema_version':1,'id':'PILOT-FREEZE-VALIDATOR-DEPS',
 'timestamp_utc':now(),'group_id':'shared-pilot-freeze','kind':'incomplete-initial-freeze',
 'status':'resolved-by-addendum','description':'Initial snapshot omitted four Python validator dependencies.',
 'resolution':'Recorded a separate hashed dependency addendum; task sources and targets unchanged.'})
