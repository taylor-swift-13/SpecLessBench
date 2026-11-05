"""Check the archived construction logs and any restored copies."""
import hashlib
import tarfile
from pathlib import Path

root = Path(__file__).resolve().parents[2]
archive = root / 'benchmarks/construction/command-logs.tar.gz'
expected = (root / 'benchmarks/construction/command-logs.sha256').read_text().strip()
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
assert digest == expected, 'archive checksum mismatch'
with tarfile.open(archive, 'r:gz') as tar:
    members = tar.getmembers()
    assert all(m.isfile() and m.name.startswith('benchmarks/construction/logs/') for m in members)
    names = {m.name for m in members}
    assert len(names) == len(members)
    verified_disk = 0
    for member in members:
        path = root / member.name
        data = tar.extractfile(member).read()
        if path.is_file():
            assert hashlib.sha256(data).digest() == hashlib.sha256(path.read_bytes()).digest(), member.name
            verified_disk += 1
print(f'Archive: {len(members)} files; {verified_disk} restored files matched; SHA-256 {digest}')
