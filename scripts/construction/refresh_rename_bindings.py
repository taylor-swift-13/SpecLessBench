"""Rebind current registries after recorded namespace-only migration.

Historical differential reports are deliberately not rewritten. The Git
baseline and rename audit retain their original hashes.
"""
import hashlib,json
from pathlib import Path
from accounting import ROOT

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
audit=ROOT/'benchmarks/construction/rename-speclessbench.json'
record=json.loads(audit.read_text()); changes={r['path']:r for r in record['changed_files']}
registries=[ROOT/'benchmarks/tasks/qcip-core/tasks.json',ROOT/'benchmarks/tasks/qcip-core/three-platform.json']+list((ROOT/'benchmarks/tasks').glob('*-core/groups.json'))
updated=record.get('registry_rebindings',[])
for path in registries:
    obj=json.loads(path.read_text()); before=sha(path); touched=[]
    for row in obj.get('protected_files',[]):
        src=path.parent/row['path']; rel=src.relative_to(ROOT).as_posix(); current=sha(src)
        if current!=row['sha256']:
            mapping=changes.get(rel)
            if not mapping or row['sha256']!=mapping['before_sha256'] or current!=mapping['after_sha256']:
                raise RuntimeError('Unaccounted source change: '+rel)
            touched.append(rel); row['sha256']=current
    if 'io_header_sha256' in obj:
        src=ROOT/'benchmarks/tasks/qcip-core/common/io.h'; rel=src.relative_to(ROOT).as_posix(); current=sha(src)
        if current!=obj['io_header_sha256']:
            mapping=changes.get(rel)
            if not mapping or obj['io_header_sha256']!=mapping['before_sha256'] or current!=mapping['after_sha256']:
                raise RuntimeError('Unaccounted shared header change: '+rel)
            touched.append(rel);obj['io_header_sha256']=current
    if touched:
        path.write_text(json.dumps(obj,indent=2)+'\n')
        updated.append({'path':path.relative_to(ROOT).as_posix(),'before_sha256':before,'after_sha256':sha(path),'updated_sources':touched})
record['registry_rebindings']=updated
audit.write_text(json.dumps(record,indent=2)+'\n')
print('Rebound',len(updated),'registries to mechanically renamed files')
