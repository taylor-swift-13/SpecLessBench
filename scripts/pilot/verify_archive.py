"""Verify private archive hashes without extracting paths to the filesystem."""
import hashlib,json,tarfile
from pathlib import Path
from private_paths import PRIVATE
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'benchmarks/pilot'
manifest=json.loads((P/'manifest.json').read_text());archive=PRIVATE/'frozen-sources.tar.gz'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==manifest['private_source_archive_sha256']
rows=json.loads((PRIVATE/'mapping.json').read_text())['protected_files'][:]
for name in ('validator-dependencies.json','audit-inputs.json','audit-extras.json'):
    rows.extend(json.loads((PRIVATE/name).read_text())['files'])
expected={r['path']:r['sha256']for r in rows};actual={}
with tarfile.open(archive,'r:gz')as tar:
    for entry in tar:
        assert entry.isfile() and entry.name in expected and entry.name not in actual
        actual[entry.name]=hashlib.sha256(tar.extractfile(entry).read()).hexdigest()
assert actual==expected
print('Verified',len(actual),'frozen archive members.')
