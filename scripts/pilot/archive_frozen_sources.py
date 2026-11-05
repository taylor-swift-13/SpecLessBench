"""Create a private, hash-checked source snapshot without overwriting files."""
import gzip,hashlib,io,json,tarfile
from pathlib import Path
from private_paths import PRIVATE
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'benchmarks/pilot';out=PRIVATE/'frozen-sources.tar.gz'
if out.exists():raise SystemExit('Frozen source archive exists; do not overwrite.')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
mapping=json.loads((PRIVATE/'mapping.json').read_text());rows=mapping['protected_files'][:]
for name in ('validator-dependencies.json','audit-inputs.json','audit-extras.json'):
    rows.extend(json.loads((PRIVATE/name).read_text())['files'])
files={r['path']:r['sha256'] for r in rows}
with out.open('wb')as raw:
    with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0)as compressed:
        with tarfile.open(fileobj=compressed,mode='w|')as tar:
            for name,digest in sorted(files.items()):
                source=ROOT/name;data=source.read_bytes();assert hashlib.sha256(data).hexdigest()==digest,name
                info=tarfile.TarInfo(name);info.size=len(data);info.mtime=0;info.mode=0o644
                tar.addfile(info,io.BytesIO(data))
manifest=json.loads((P/'manifest.json').read_text());manifest['private_source_archive_sha256']=sha(out)
manifest['private_source_archive_files']=len(files)
(P/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
print('Archived',len(files),'frozen source and support files; keep curator directory private and backed up.')
