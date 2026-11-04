"""One-time, auditable identifier migration; historical logs stay immutable."""
import hashlib, json, subprocess
from pathlib import Path

root=Path(__file__).resolve().parents[2]
paths=subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().split('\0')
old='Equal'+'Bench'; new='SpecLessBench'
replacements=((old,new),(old.upper(),new.upper()),(old.lower(),new.lower()))
changed=[]
for name in paths:
    if not name or name == 'scripts/construction/rename_project.py': continue
    p=root/name
    if not p.is_file() or p.suffix not in {'.py','.v','.lean','.goal','.md','.tex','.bib','.c','.h'}: continue
    if name.startswith('benchmarks/construction/'): continue
    if name.startswith('benchmarks/source-material/') and p.suffix != '.md': continue
    data=p.read_bytes()
    try: text=data.decode('utf-8')
    except UnicodeDecodeError: continue
    updated=text
    for before,after in replacements: updated=updated.replace(before,after)
    if updated!=text:
        out=updated.encode('utf-8');p.write_bytes(out)
        changed.append({'path':name,'before_sha256':hashlib.sha256(data).hexdigest(),'after_sha256':hashlib.sha256(out).hexdigest()})
path=root/'benchmarks/construction/rename-speclessbench.json'
path.write_text(json.dumps({'schema_version':1,'baseline_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
    'scope':'mechanical project identifier replacement; historical construction logs and evidence retain original values',
    'changed_files':changed,'verification':'new revision requires rebuilding and refreshed source bindings; previous reports describe pre-rename sources'},indent=2)+'\n')
print('Renamed',len(changed),'active source and documentation files')
