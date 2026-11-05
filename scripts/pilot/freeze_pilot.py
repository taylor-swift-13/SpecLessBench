"""Freeze current pilot sources and produce opaque task IDs.

Curator mapping is generated once and is deliberately not published. This is
a curation snapshot, not a claim that isolated solver packages exist yet.
"""
import hashlib,hmac,json,os,secrets,subprocess
from pathlib import Path
from private_paths import PRIVATE

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'benchmarks/pilot';
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def opaque(secret,kind,name):return kind+'-'+hmac.new(secret,name.encode(),hashlib.sha256).hexdigest()[:16]
def dump(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def main():
    active=json.loads((ROOT/'benchmarks/active-groups.json').read_text())
    interface=json.loads((ROOT/'benchmarks/proof-interface/manifest.json').read_text())
    contexts={x['context_id']:x for x in interface['contexts']}
    ids=[c for group in active['groups'] for c in group['contexts']]
    assert len(ids)==len(set(ids))==71 and set(ids)==set(contexts)
    tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    def is_protected(name):
        p=Path(name)
        return ((name.startswith('benchmarks/tasks/') and '/evidence/' not in name and p.suffix in ('.v','.lean','.c','.h','.goal'))
           or (name.startswith('benchmarks/proof-interface/') and p.suffix in ('.v','.lean'))
           or name in ('benchmarks/active-groups.json','benchmarks/split-family-policy.json','benchmarks/proof-interface/manifest.json','scripts/construction/submission_contract.py')
           or name in ('scripts/construction/differential_algorithms.py','scripts/construction/algorithms_common.py','scripts/construction/accounting.py','scripts/construction/measure.py')
           or (name.startswith('scripts/construction/') and name.endswith('_cases.py'))
           or name=='scripts/curation/check_qcip_core.py')
    files=[{'path':name,'sha256':sha(ROOT/name)}for name in tracked if name and is_protected(name)]
    assert files
    secret_path=PRIVATE/'secret.bin';mapping_path=PRIVATE/'mapping.json'
    if (OUT/'manifest.json').exists() or secret_path.exists() or mapping_path.exists():
        raise SystemExit('Pilot already frozen: verify it rather than silently replacing it.')
    PRIVATE.mkdir(parents=True,exist_ok=True);secret=secrets.token_bytes(32)
    secret_path.write_bytes(secret)
    try:os.chmod(secret_path,0o600)
    except OSError:pass
    mapping=[];public=[]
    for group in active['groups']:
        split=opaque(secret,'F',group['split_group_id'])
        for original in group['contexts']:
            pid=opaque(secret,'P',original)
            mapping.append({'pilot_id':pid,'split_family':split,'source_group_id':group['group_id'],
                            'source_context_id':original,'context':contexts[original]})
            public.append({'pilot_id':pid,'split_family':split,'platforms':['lean','rocq','compcert']})
    assert len({x['pilot_id']for x in public})==71
    source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    private={'schema_version':1,'source_commit':source_commit,'contexts':mapping,'protected_files':files,
        'active_groups_sha256':sha(ROOT/'benchmarks/active-groups.json'),
        'interface_manifest_sha256':sha(ROOT/'benchmarks/proof-interface/manifest.json')}
    dump(mapping_path,private)
    public_manifest={'schema_version':1,'status':'frozen-source-snapshot; solver-release-pending',
        'pilot_name':'SpecLessBench pilot v1','source_commit':source_commit,
        'contexts':sorted(public,key=lambda x:x['pilot_id']),'context_count':71,
        'split_family_count':len({x['split_family']for x in public}),'platform_instances':213,
        'protected_file_count':len(files),'private_mapping_sha256':sha(mapping_path),
        'truth_labels_in_this_manifest':False,'reference_certificates':0,
        'release_warning':'Curator mapping, evidence, original source history and sibling variants can leak labels; public isolated packaging is not certified.',
        'private_mapping_backup_required':True}
    dump(OUT/'manifest.json',public_manifest)
    print(json.dumps({'contexts':len(public),'families':public_manifest['split_family_count'],'protected_files':len(files),'source_commit':source_commit}))
if __name__=='__main__':main()
