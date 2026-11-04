"""Record why curator secrets were moved off the Windows-mounted workspace."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'construction'))
from accounting import AUDIT,append,now
append(AUDIT/'issues.jsonl',{'schema_version':1,'id':'PILOT-PRIVATE-WINDOWS-MOUNT',
 'timestamp_utc':now(),'group_id':'shared-pilot-freeze','kind':'private-storage-permissions',
 'status':'resolved-moved-to-wsl-home','description':'WSL chmod on the Windows-mounted workspace left the curator secret with permissive displayed Unix mode.',
 'resolution':'Copied and hash-checked all curator files to a mode-0700 WSL home directory with mode-0600 files, then removed the checked original copy.',
 'remaining_risk':'The private WSL directory must be backed up securely; public Git history and shared task sources can still leak labels.'})
